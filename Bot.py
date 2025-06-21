import os
import re
import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.types import InputFile
from yt_dlp import YoutubeDL
from aiogram.utils import executor

TOKEN = '7620109906:AAGuAXtKYWPDRWj62eOj2vwZrxNnTr75Ngo'

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

ydl_opts = {
    'format': 'bv*+ba/best',
    'outtmpl': 'downloads/%(title)s.%(ext)s',
    'merge_output_format': 'mp4',
    'noplaylist': False,
    'postprocessors': [{
        'key': 'FFmpegVideoRemuxer',
        'preferedformat': 'mp4',
    }],
    'quiet': True,
}

def is_url(text):
    return re.match(r'^https?://', text)

@dp.message_handler(commands=['start'])
async def cmd_start(msg: types.Message):
    await msg.answer("👋 أرسل لي أي رابط من السوشيال ميديا وسأقوم بتحميله لك بأعلى جودة ممكنة 🎥📥")

@dp.message_handler()
async def handle_links(msg: types.Message):
    if not is_url(msg.text):
        await msg.reply("❌ هذا ليس رابطاً صحيحاً.")
        return

    await msg.reply("🔄 جاري التحميل، انتظر قليلاً...")

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(msg.text, download=True)
            file_path = ydl.prepare_filename(info)

        if os.path.exists(file_path):
            if file_path.endswith(('.mp4', '.mkv', '.webm')):
                await msg.reply_video(InputFile(file_path), caption=info.get("title", "📽 تم التحميل"))
            elif file_path.endswith(('.mp3', '.wav', '.m4a')):
                await msg.reply_audio(InputFile(file_path), caption=info.get("title", "🎵 تم التحميل"))
            else:
                await msg.reply_document(InputFile(file_path), caption="📄 تم التحميل")
            os.remove(file_path)
        else:
            await msg.reply("⚠️ لم يتم العثور على الملف بعد التحميل.")

    except Exception as e:
        await msg.reply(f"❌ حدث خطأ أثناء التحميل:\n{str(e)}")

if __name__ == "__main__":
    os.makedirs("downloads", exist_ok=True)
    executor.start_polling(dp, skip_updates=True)
