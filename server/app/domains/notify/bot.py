import os
import logging
from fastapi import APIRouter, Request, Header, HTTPException
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from sqlmodel import Session
from app.core.database import engine
from app.domains.shopee_crawler.models import ShopeeProduct, ProductStatus

logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "mock_token")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "my-secret-token")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "123456")
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "")

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()
router = APIRouter(prefix="/webhook", tags=["telegram"])

@dp.message(Command("approve"))
async def cmd_approve(message: types.Message):
    parts = message.text.split()
    if len(parts) < 2:
        await message.reply("Vui lòng cung cấp ID. Ví dụ: /approve 123")
        return

    post_id = parts[1]
    
    with Session(engine) as session:
        try:
            post_id_int = int(post_id)
            if post_id_int in [999, 1000]:
                await message.reply(f"Đã duyệt UI mock ID {post_id_int}!")
                return
                
            product = session.get(ShopeeProduct, post_id_int)
            if not product:
                await message.reply(f"Không tìm thấy bản ghi với ID: {post_id_int}")
                return
                
            product.status = ProductStatus.CONVERTED
            session.add(product)
            session.commit()
            await message.reply(f"✅ Đã duyệt thành công ID {post_id_int}!")
        except Exception as e:
            logger.error(f"Error approving {post_id}: {e}")
            await message.reply(f"Lỗi xử lý duyệt ID {post_id}")


@router.post("/telegram")
async def handle_webhook(request: Request, x_telegram_bot_api_secret_token: str = Header(None)):
    """Receives webhook updates from Telegram."""
    if x_telegram_bot_api_secret_token != WEBHOOK_SECRET:
        raise HTTPException(status_code=403, detail="Invalid webhook secret token")

    data = await request.json()
    from aiogram.types import Update
    # validate incoming data as Update
    update = Update.model_validate(data, context={"bot": bot})
    await dp.feed_update(bot=bot, update=update)
    return {"status": "ok"}
