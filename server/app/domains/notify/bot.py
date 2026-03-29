import os
import logging
import discord
from discord import app_commands
from sqlmodel import Session
from app.core.database import engine
from app.domains.shopee_crawler.models import ShopeeProduct, ProductStatus

from discord.ext import commands
from app.core.config import settings

logger = logging.getLogger(__name__)

DISCORD_BOT_TOKEN = settings.DISCORD_BOT_TOKEN

# Intents setup
intents = discord.Intents.default()
# KHÔNG BẬT message_content để tránh lỗi Crash nếu chưa mở Privileged Intents trên web
# intents.message_content = True

# Khởi tạo bot bằng commands.Bot gọn nhẹ hơn
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.tree.command(name="approve", description="Phê duyệt một video/post bằng ID")
@app_commands.describe(post_id="ID của bản ghi cần duyệt")
async def cmd_approve(interaction: discord.Interaction, post_id: int):
    with Session(engine) as session:
        try:
            if post_id in [999, 1000]:
                await interaction.response.send_message(f"Đã duyệt UI mock ID {post_id}!")
                return
                
            product = session.get(ShopeeProduct, post_id)
            if not product:
                await interaction.response.send_message(f"Không tìm thấy bản ghi với ID: {post_id}", ephemeral=True)
                return
                
            product.status = ProductStatus.CONVERTED
            session.add(product)
            session.commit()
            await interaction.response.send_message(f"✅ Đã duyệt thành công ID {post_id}!")
        except Exception as e:
            logger.error(f"Error approving {post_id}: {e}")
            await interaction.response.send_message(f"Lỗi xử lý duyệt ID {post_id}", ephemeral=True)

@bot.event
async def on_ready():
    print(f"✅ [Discord] Logged in as {bot.user} (ID: {bot.user.id})")
    
    # Ép đồng bộ Slash Command LẬP TỨC cho tất cả Server bot đang tham gia
    # để tránh bị Discord cache 1 tiếng
    try:
        synced_count = 0
        for guild in bot.guilds:
            try:
                bot.tree.copy_global_to(guild=guild)
                await bot.tree.sync(guild=guild)
                synced_count += 1
                print(f"✅ [Discord] Synced /approve command to Server '{guild.name}'!")
            except discord.Forbidden:
                print(f"❌ [Discord] Forbidden on '{guild.name}' (Thiếu quyền 'applications.commands' lúc invite!)")
            except discord.HTTPException as e:
                print(f"❌ [Discord] HTTP error syncing on '{guild.name}': {e}")
                
        if len(bot.guilds) == 0:
            print("⚠️ [Discord] Bot chưa được mời vào bất kỳ Server nào!")
            
    except Exception as e:
        print(f"❌ [Discord] Error in on_ready: {e}")
