"""
Content Sourcing API Router — Phase 3
======================================
Endpoints để test và trigger các tính năng:
  - POST /sourcing/scrape      — Cào video metadata theo keyword (không download)
  - POST /sourcing/dedupe      — Lách MD5 deduplicate 1 file video local
  - POST /sourcing/seed/comment — Trigger comment FB qua Appium điện thoại thật (async Celery)
  - GET  /sourcing/sources     — Liệt kê danh sách nguồn cào đang hỗ trợ
"""

from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlmodel import Session, select

from app.core.config import settings
from app.core.database import get_session
from app.domains.admin.dependencies import get_current_admin

router = APIRouter(prefix="/sourcing", tags=["content-sourcing"])


# ─── Schemas ──────────────────────────────────────────────────────────────────


class ScrapeRequest(BaseModel):
    keyword: str = Field(..., min_length=1, max_length=200, description="Từ khoá tìm kiếm video (VD: 'áo thun nam')")
    source: str = Field(default="tiktok", description="Nguồn cào: 'tiktok' hoặc 'douyin'")
    limit: int = Field(default=5, ge=1, le=50, description="Số video tối đa cần lấy")


class VideoMeta(BaseModel):
    url: str | None
    title: str | None
    thumbnail: str | None
    source: str


class ScrapeResponse(BaseModel):
    source: str
    keyword: str
    count: int
    videos: list[VideoMeta]


class DedupeRequest(BaseModel):
    input_path: str = Field(..., description="Đường dẫn tuyệt đối file video input trên server")
    output_path: str = Field(..., description="Đường dẫn tuyệt đối file video output trên server")
    mode: str = Field(default="light", description="'light' = xoá metadata | 'deep' = flip + đổi speed")


class DedupeResponse(BaseModel):
    output_path: str
    mode: str
    message: str


class SeedCommentRequest(BaseModel):
    post_url: str = Field(..., description="URL bài viết Facebook cần comment (VD: https://www.facebook.com/...)")
    comment_text: str = Field(..., min_length=1, max_length=2000, description="Nội dung comment (thường chứa link affiliate)")
    udid: str | None = Field(default=None, description="UDID thiết bị Android. Bỏ trống để dùng từ .env")


class SeedCommentResponse(BaseModel):
    task_id: str
    status: str
    message: str


# ─── Endpoints ────────────────────────────────────────────────────────────────


@router.get("/sources", summary="Liệt kê nguồn cào đang hỗ trợ")
def list_available_sources(
    _admin: dict = Depends(get_current_admin),
) -> dict:
    """
    Trả về danh sách các `source_name` có thể dùng trong POST /scrape.
    """
    from app.domains.content_sourcing.services.scraper import list_sources
    return {"sources": list_sources()}


@router.post("/scrape", response_model=ScrapeResponse, summary="Cào metadata video theo keyword")
def scrape_videos(
    body: ScrapeRequest,
    _admin: dict = Depends(get_current_admin),
) -> ScrapeResponse:
    """
    Tìm kiếm video liên quan đến `keyword` từ nguồn được chỉ định.
    Chỉ lấy **metadata** (URL, title, thumbnail) — không tải file về.

    Dùng để test xem scraper hoạt động không và đánh giá chất lượng kết quả
    trước khi gắn vào pipeline download thật.
    """
    from app.domains.content_sourcing.services.scraper import get_source

    try:
        source = get_source(body.source)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    try:
        results = source.fetch_videos(keyword=body.keyword, limit=body.limit)
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Scraper error: {e}")

    return ScrapeResponse(
        source=body.source,
        keyword=body.keyword,
        count=len(results),
        videos=[VideoMeta(**v) for v in results],
    )


@router.post("/dedupe", response_model=DedupeResponse, summary="Lách MD5 cho video (light/deep mode)")
def deduplicate_video(
    body: DedupeRequest,
    _admin: dict = Depends(get_current_admin),
) -> DedupeResponse:
    """
    Áp dụng deduplication lên file video local trên server.

    - **light**: Xoá toàn bộ metadata/Exif, copy stream nguyên vẹn → thay đổi MD5 hash.
    - **deep**: Lật ngang (hflip) + tăng tốc 1.05x + đồng bộ audio → khó bị detect hơn.

    Cần file input tồn tại trên server. Output sẽ ghi đè nếu đã có.
    """
    from app.domains.content_sourcing.services.ffmpeg_dedupe import apply_dedupe, DEDUPE_MODE_LIGHT, DEDUPE_MODE_DEEP

    if body.mode not in (DEDUPE_MODE_LIGHT, DEDUPE_MODE_DEEP):
        raise HTTPException(status_code=422, detail=f"mode phải là 'light' hoặc 'deep', nhận: '{body.mode}'")

    input_path = Path(body.input_path)
    if not input_path.exists():
        raise HTTPException(status_code=404, detail=f"File không tồn tại: {body.input_path}")

    output_path = Path(body.output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        result = apply_dedupe(str(input_path), str(output_path), mode=body.mode)
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))

    return DedupeResponse(
        output_path=result,
        mode=body.mode,
        message=f"Dedupe ({body.mode}) hoàn tất. Output: {result}",
    )


@router.post("/seed/comment", response_model=SeedCommentResponse, summary="Trigger comment FB qua điện thoại thật")
def trigger_fb_comment(
    body: SeedCommentRequest,
    session: Session = Depends(get_session),
    _admin: dict = Depends(get_current_admin),
) -> SeedCommentResponse:
    """
    Enqueue một Celery task để điều khiển điện thoại Android thật (qua Appium)
    vào comment link Affiliate vào bài Facebook chỉ định.

    **Yêu cầu:**
    - Appium server đang chạy tại `APPIUM_SERVER_URL` (mặc định `localhost:4723`)
    - Thiết bị Android đã kết nối (`adb devices` phải thấy UDID)
    - App Facebook đã đăng nhập trên thiết bị

    Task sẽ chạy **bất đồng bộ** trên queue `appium_phone`.
    Dùng `task_id` trả về để kiểm tra trạng thái qua Celery/Flower.
    """
    from app.domains.sys_worker.seeding_tasks import exec_fb_comment
    from app.domains.devices.models import Device

    # Resolve UDID: body override > first online device in DB
    udid = body.udid
    if not udid:
        online_device = session.exec(
            select(Device).where(Device.status == "online")
        ).first()
        if online_device:
            udid = online_device.udid

    if not udid:
        raise HTTPException(
            status_code=412,
            detail=(
                "Chưa có thiết bị nào đang Online. "
                "Vào trang Thiết Bị → thêm thiết bị và bật trạng thái Online, "
                "hoặc truyền 'udid' trực tiếp trong body."
            ),
        )

    try:
        task = exec_fb_comment.delay(
            udid=udid,
            post_url=body.post_url,
            comment_text=body.comment_text,
        )
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Không thể enqueue task: {e}")

    return SeedCommentResponse(
        task_id=task.id,
        status="queued",
        message=f"Task đã được enqueue. Worker appium_phone sẽ xử lý. Task ID: {task.id}",
    )
