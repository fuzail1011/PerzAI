from fastapi import APIRouter, Depends, Form, Request, UploadFile, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.core.security import create_access_token, decode_access_token
from app.services.user_service import create_user, authenticate_user
from app.services.persona_service import (
    create_persona,
    get_personas_for_user,
    delete_persona,
    update_system_prompt,
)
from app.services.knowledge_service import ingest_document, get_documents_by_user
from app.services.retrieval_service import retrieve_response
from app.schemas.user import UserCreate
from app.schemas.persona import PersonaCreate, PersonaDelete
from app.config import Settings
from app.models.user import User
from app.models.persona import Persona
from sqlalchemy import select
import os

router = APIRouter()

_template_dir = os.path.join(os.path.dirname(__file__), "..", "frontend", "templates")
templates = Jinja2Templates(directory=_template_dir)


# ---------------------------------------------------------------------------
# Cookie-based auth helpers
# ---------------------------------------------------------------------------

def get_user_id_from_cookie(request: Request) -> str | None:
    token = request.cookies.get("access_token")
    if not token:
        return None
    return decode_access_token(token)


def require_auth(request: Request) -> str:
    """Dependency: returns user_id str or raises redirect."""
    user_id = get_user_id_from_cookie(request)
    if not user_id:
        raise HTTPException(status_code=302, headers={"Location": "/ui/login"})
    return user_id


def _set_auth_cookie(response, token: str):
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        max_age=Settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="lax",
    )


# ---------------------------------------------------------------------------
# Root redirect
# ---------------------------------------------------------------------------

@router.get("/", include_in_schema=False)
async def root_redirect(request: Request):
    if get_user_id_from_cookie(request):
        return RedirectResponse("/ui/dashboard", status_code=302)
    return RedirectResponse("/ui/login", status_code=302)


# ---------------------------------------------------------------------------
# Auth pages
# ---------------------------------------------------------------------------

@router.get("/ui/login", include_in_schema=False)
async def login_page(request: Request):
    if get_user_id_from_cookie(request):
        return RedirectResponse("/ui/dashboard", status_code=302)
    return templates.TemplateResponse(request, "auth.html", {"error": None})


@router.post("/ui/login", include_in_schema=False)
async def login_submit(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: AsyncSession = Depends(get_db),
):
    user = await authenticate_user(db, email, password)
    if not user:
        return templates.TemplateResponse(
            request,
            "auth.html",
            {"error": "Invalid email or password", "active_tab": "login"},
            status_code=401,
        )
    token = create_access_token(str(user.id))
    response = RedirectResponse("/ui/dashboard", status_code=303)
    _set_auth_cookie(response, token)
    return response


@router.post("/ui/signup", include_in_schema=False)
async def signup_submit(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: AsyncSession = Depends(get_db),
):
    try:
        user = await create_user(db, UserCreate(username=username, email=email, password=password))
    except HTTPException as e:
        return templates.TemplateResponse(
            request,
            "auth.html",
            {"error": e.detail, "active_tab": "signup"},
            status_code=400,
        )
    token = create_access_token(str(user.id))
    response = RedirectResponse("/ui/dashboard", status_code=303)
    _set_auth_cookie(response, token)
    return response


@router.get("/ui/logout", include_in_schema=False)
async def logout():
    response = RedirectResponse("/ui/login", status_code=302)
    response.delete_cookie("access_token")
    return response


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------

@router.get("/ui/dashboard", include_in_schema=False)
async def dashboard(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    user_id = get_user_id_from_cookie(request)
    if not user_id:
        return RedirectResponse("/ui/login", status_code=302)

    # Fetch user info
    result = await db.execute(select(User).where(User.id == int(user_id)))
    user = result.scalars().first()

    personas = await get_personas_for_user(db, int(user_id))

    return templates.TemplateResponse(request, "dashboard.html", {
        "username": user.username if user else "User",
        "personas": [_persona_dict_to_obj(p) for p in personas],
    })


# ---------------------------------------------------------------------------
# Persona HTMX endpoints
# ---------------------------------------------------------------------------

@router.post("/ui/personas", include_in_schema=False)
async def create_persona_htmx(
    request: Request,
    name: str = Form(...),
    description: str = Form(""),
    db: AsyncSession = Depends(get_db),
):
    user_id = require_auth(request)
    persona_data = PersonaCreate(name=name, description=description or None)
    persona = await create_persona(db, int(user_id), persona_data)

    # Return persona dict with proper types for template
    result = await db.execute(
        select(Persona).where(Persona.id == persona.id)
    )
    p = result.scalars().first()

    return templates.TemplateResponse(request, "persona_card.html", {
        "persona": p,
    })


@router.delete("/ui/personas/{persona_id}", include_in_schema=False)
async def delete_persona_htmx(
    persona_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    user_id = require_auth(request)
    await delete_persona(db, int(user_id), PersonaDelete(id=persona_id))
    return HTMLResponse("")


# ---------------------------------------------------------------------------
# Persona detail page
# ---------------------------------------------------------------------------

@router.get("/ui/persona/{persona_id}", include_in_schema=False)
async def persona_page(
    persona_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    user_id = get_user_id_from_cookie(request)
    if not user_id:
        return RedirectResponse("/ui/login", status_code=302)

    result = await db.execute(
        select(Persona).where(
            Persona.id == persona_id,
            Persona.user_id == int(user_id),
        )
    )
    persona = result.scalars().first()
    if not persona:
        return RedirectResponse("/ui/dashboard", status_code=302)

    # Get documents for this persona
    docs_result = await get_documents_by_user(db, int(user_id))
    documents = []
    for p_data in docs_result.get("personas", []):
        if p_data["persona_id"] == persona_id:
            documents = p_data["kb_documents"]
            break

    return templates.TemplateResponse(request, "persona.html", {
        "persona": persona,
        "documents": documents,
    })


# ---------------------------------------------------------------------------
# Chat HTMX endpoint
# ---------------------------------------------------------------------------

@router.post("/ui/persona/{persona_id}/chat", include_in_schema=False)
async def chat_htmx(
    persona_id: int,
    request: Request,
    query: str = Form(...),
    db: AsyncSession = Depends(get_db),
):
    user_id = require_auth(request)

    result = await retrieve_response(
        db=db,
        user_id=int(user_id),
        persona_id=persona_id,
        query=query,
        top_k=5,
    )

    # Fetch persona initial for avatar
    persona_result = await db.execute(
        select(Persona).where(Persona.id == persona_id)
    )
    persona = persona_result.scalars().first()
    initial = persona.name[0].upper() if persona else "A"

    return templates.TemplateResponse(request, "chat_message.html", {
        "response": result.get("response", ""),
        "initial": initial,
    })


# ---------------------------------------------------------------------------
# KB upload HTMX endpoint
# ---------------------------------------------------------------------------

@router.post("/ui/persona/{persona_id}/upload", include_in_schema=False)
async def upload_htmx(
    persona_id: int,
    request: Request,
    file: UploadFile,
    source: str = Form("manual"),
    category: str = Form("general"),
    db: AsyncSession = Depends(get_db),
):
    user_id = require_auth(request)

    result = await ingest_document(
        db=db,
        file=file,
        user_id=int(user_id),
        persona_id=persona_id,
        source=source,
        category=category,
    )

    if result.get("status") == "error":
        raise HTTPException(status_code=400, detail=result.get("message", "Ingestion failed"))

    doc_name = result.get("document_name", file.filename)
    return templates.TemplateResponse(request, "doc_item.html", {
        "doc": doc_name,
    })


# ---------------------------------------------------------------------------
# System prompt HTMX endpoint
# ---------------------------------------------------------------------------

@router.put("/ui/persona/{persona_id}/system-prompt", include_in_schema=False)
async def system_prompt_htmx(
    persona_id: int,
    request: Request,
    system_prompt: str = Form(...),
    db: AsyncSession = Depends(get_db),
):
    user_id = require_auth(request)
    await update_system_prompt(
        db=db,
        persona_id=persona_id,
        user_id=int(user_id),
        system_prompt=system_prompt,
    )
    return HTMLResponse("")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _persona_dict_to_obj(p: dict):
    """Wrap persona dict from service as a simple object for template access."""
    class _P:
        pass
    obj = _P()
    for k, v in p.items():
        setattr(obj, k, v)
    return obj
