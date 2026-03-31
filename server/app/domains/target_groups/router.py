from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select

from app.core.database import get_session
from app.domains.admin.dependencies import get_current_admin
from app.domains.target_groups.models import (
    PostStatus,
    PostStatusUpdate,
    ScrapedPost,
    ScrapedPostPublic,
    TargetGroup,
    TargetGroupCreate,
    TargetGroupPublic,
)

router = APIRouter(prefix="/target-groups", tags=["target-groups"])


# ---------- Target Group endpoints ----------


@router.get("/", response_model=List[TargetGroupPublic])
def list_target_groups(
    session: Session = Depends(get_session),
    _admin: dict = Depends(get_current_admin),
) -> List[TargetGroupPublic]:
    """List all configured target Facebook groups."""
    groups = list(session.exec(select(TargetGroup)).all())
    return [
        TargetGroupPublic(
            id=g.id,
            url=g.url,
            name=g.name,
            keywords=g.keywords,
            is_active=g.is_active,
            created_at=g.created_at,
        )
        for g in groups
    ]


@router.post("/", response_model=TargetGroupPublic, status_code=201)
def create_target_group(
    body: TargetGroupCreate,
    session: Session = Depends(get_session),
    _admin: dict = Depends(get_current_admin),
) -> TargetGroupPublic:
    """Add a new Facebook group as a scraping target."""
    if not body.url.strip():
        raise HTTPException(status_code=422, detail="url must not be empty")
    group = TargetGroup(
        url=body.url.strip(),
        name=body.name.strip(),
        keywords=body.keywords,
    )
    session.add(group)
    session.commit()
    session.refresh(group)
    return TargetGroupPublic(
        id=group.id,
        url=group.url,
        name=group.name,
        keywords=group.keywords,
        is_active=group.is_active,
        created_at=group.created_at,
    )


@router.delete("/{group_id}", status_code=204)
def delete_target_group(
    group_id: int,
    session: Session = Depends(get_session),
    _admin: dict = Depends(get_current_admin),
) -> None:
    """Delete a target group by ID."""
    group = session.get(TargetGroup, group_id)
    if not group:
        raise HTTPException(status_code=404, detail=f"Group {group_id} not found")
    session.delete(group)
    session.commit()


# ---------- Scraped Post endpoints ----------


@router.get("/posts/", response_model=List[ScrapedPostPublic])
def list_scraped_posts(
    status: Optional[str] = Query(default=None, description="Filter by status: PENDING, APPROVED, REJECTED"),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, le=500),
    session: Session = Depends(get_session),
    _admin: dict = Depends(get_current_admin),
) -> List[ScrapedPostPublic]:
    """List scraped Facebook posts with optional status filter."""
    query = select(ScrapedPost)
    if status:
        try:
            status_enum = PostStatus(status.upper())
            query = query.where(ScrapedPost.status == status_enum)
        except ValueError:
            raise HTTPException(status_code=422, detail=f"Invalid status: {status}")
    query = query.offset(skip).limit(limit)
    posts = list(session.exec(query).all())
    return [
        ScrapedPostPublic(
            id=p.id,
            original_url=p.original_url,
            content=p.content,
            author=p.author,
            comments_count=p.comments_count,
            reactions_count=p.reactions_count,
            target_group_id=p.target_group_id,
            status=p.status,
            created_at=p.created_at,
        )
        for p in posts
    ]


@router.patch("/posts/{post_id}/status", response_model=ScrapedPostPublic)
def update_post_status(
    post_id: int,
    body: PostStatusUpdate,
    session: Session = Depends(get_session),
    _admin: dict = Depends(get_current_admin),
) -> ScrapedPostPublic:
    """Approve or reject a scraped post."""
    post = session.get(ScrapedPost, post_id)
    if not post:
        raise HTTPException(status_code=404, detail=f"Post {post_id} not found")
    post.status = body.status
    session.add(post)
    session.commit()
    session.refresh(post)
    return ScrapedPostPublic(
        id=post.id,
        original_url=post.original_url,
        content=post.content,
        author=post.author,
        comments_count=post.comments_count,
        reactions_count=post.reactions_count,
        target_group_id=post.target_group_id,
        status=post.status,
        created_at=post.created_at,
    )


# ---------- Session upload ----------


from fastapi import UploadFile, File
from pydantic import BaseModel
import json as _json


class SessionUploadResponse(BaseModel):
    saved_to: str
    message: str


@router.post("/session", response_model=SessionUploadResponse)
async def upload_fb_session(
    file: UploadFile = File(...),
    _admin: dict = Depends(get_current_admin),
) -> SessionUploadResponse:
    """
    Upload Facebook session cookies to enable Playwright scraping.

    Accepted formats:
    - **Cookie-Editor JSON** (flat array): Export All → JSON from the Cookie-Editor browser extension
      while logged into facebook.com
    - **Playwright storage_state JSON**: {"cookies": [...], "origins": [...]}

    After upload, use the 'Scrape Now' button or wait for the scheduler to run.
    """
    from pathlib import Path
    from app.core.config import settings

    content = await file.read()
    try:
        parsed = _json.loads(content)
        if not isinstance(parsed, (dict, list)):
            raise ValueError("Session file must be a JSON object or array")
    except (ValueError, _json.JSONDecodeError) as e:
        raise HTTPException(status_code=422, detail=f"Invalid JSON: {e}")

    state_path = Path(settings.FB_SESSION_FILE)
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_bytes(content)

    count = len(parsed) if isinstance(parsed, list) else len(parsed.get("cookies", []))
    return SessionUploadResponse(
        saved_to=str(state_path.resolve()),
        message=f"Session saved ({count} cookies). You can now run 'Scrape Now' on a group.",
    )


# ---------- Manual scrape trigger ----------


from pydantic import BaseModel as _BaseModel


class ScrapeResponse(_BaseModel):
    task_id: str
    message: str


@router.post("/{group_id}/scrape", response_model=ScrapeResponse)
def trigger_group_scrape(
    group_id: int,
    session: Session = Depends(get_session),
    _admin: dict = Depends(get_current_admin),
) -> ScrapeResponse:
    """
    Manually trigger a scrape for a specific target group.
    Dispatches the Celery scrape_facebook_group task immediately.
    """
    from app.domains.target_groups.tasks import scrape_facebook_group

    group = session.get(TargetGroup, group_id)
    if not group:
        raise HTTPException(status_code=404, detail=f"Group {group_id} not found")
    if not group.is_active:
        raise HTTPException(status_code=400, detail="Group is inactive")

    task = scrape_facebook_group.delay(group_id)
    return ScrapeResponse(
        task_id=task.id,
        message=f"Scrape task dispatched for group '{group.name or group.url}'. Check posts tab in a few seconds.",
    )
