from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from typing import List
from pydantic import BaseModel
from app.core.database import get_session
from app.domains.shopee_crawler.models import ShopeeProduct, ProductStatus
from app.domains.admin.dependencies import get_current_admin

router = APIRouter(prefix="/approval", tags=["approval"])

class PendingPostSchema(BaseModel):
    id: int
    title: str
    caption: str
    thumbnail: str
    status: str

class ApprovalUpdate(BaseModel):
    caption: str
    status: str

@router.get("/queue", response_model=List[PendingPostSchema])
def get_approval_queue(session: Session = Depends(get_session)):
    products = session.exec(select(ShopeeProduct).where(ShopeeProduct.status == ProductStatus.CONVERTED)).all()
    results = []
    for p in products:
        results.append(PendingPostSchema(
            id=p.id,
            title=p.title,
            caption=f"{p.title}\n{p.price}\nBuy now: {p.affiliate_url}",
            thumbnail=p.image_urls[0] if p.image_urls else "https://placehold.co/600x400?text=No+Image",
            status="pending"
        ))
    
    # UI Mock item if empty DB
    if not results:
        results.append(PendingPostSchema(
            id=999,
            title="Sample Facebook Post",
            caption="Check out this amazing keyboard that boosts productivity by 200%. Let me know if you want the link!",
            thumbnail="https://images.unsplash.com/photo-1595225476474-87563907a212?w=500&q=80",
            status="pending"
        ))
        results.append(PendingPostSchema(
            id=1000,
            title="Trending TikTok Video",
            caption="Mind-blowing AI tools! Link in bio. #AI #Tech",
            thumbnail="https://images.unsplash.com/photo-1677442136019-21780ecad995?w=500&q=80",
            status="pending"
        ))
    return results

@router.put("/{post_id}")
def update_approval(post_id: int, payload: ApprovalUpdate, session: Session = Depends(get_session)):
    if post_id not in [999, 1000]:
        product = session.get(ShopeeProduct, post_id)
        if product:
            product.status = ProductStatus.FAILED if payload.status == 'rejected' else ProductStatus.CONVERTED
            session.add(product)
            session.commit()
    return {"message": "Success", "id": post_id, "status": payload.status}
