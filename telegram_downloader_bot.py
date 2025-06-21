import os
import re
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.enums import ParseMode
from aiogram.types import FSInputFile
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties
from yt_dlp import YoutubeDL

API_TOKEN = '7620109906:AAGuAXtKYWPDRWj62eOj2vwZrxNnTr75Ngo'

COOKIES_FILE = "instagram.com_cookies.txt"

# إنشاء ملف الكوكيز تلقائيًا
cookies_content = """# Netscape HTTP Cookie File
# http://curl.haxx.se/rfc/cookie_spec.html
# This is a generated file!  Do not edit.

.instagram.com	TRUE	/	TRUE	1781459223	datr	CZEfaOGeHJ4nhW6oVzm-b_tc
.instagram.com	TRUE	/	TRUE	1778435236	ig_did	06BACD28-2FE5-47D7-B4B6-3F59E2DABD1F
.instagram.com	TRUE	/	TRUE	1781459223	mid	aB-RCQALAAH_n-pdcZo92jjmRVBu
.instagram.com	TRUE	/	TRUE	1783026337	ps_l	1
.instagram.com	TRUE	/	TRUE	1783026337	ps_n	1
.instagram.com	TRUE	/	TRUE	1785091934	csrftoken	a8jAKelYioZ4fnoyHFFd70hAM5B1YT4D
.instagram.com	TRUE	/	TRUE	1758307934	ds_user_id	3275715328
.instagram.com	TRUE	/	TRUE	1751136729	wd	736x1254
.instagram.com	TRUE	/	TRUE	1782067607	sessionid	3275715328%3ANCC75Kjj0vL7RK%3A20%3AAYfzxxPQdxDhoQuArD40FKmPc3LGJmlfME7N24hHKQ
.instagram.com	TRUE	/	TRUE	0	rur	"RVA\0543275715328\0541782067933:01fe89b8c7856056eab79b8606d8148b6a086f4dd40a65e7d2b716898f9b1167e679db67"
"""

with open(COOKIES_FILE, "w", encoding="utf-8") as f:
    f.write(cookies_content)

bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())

# إعداد yt-dlp مع الكوكيز
ydl_opts = {
    'format': 'bv*+ba/best',
    'outtmpl': 'downloads/%(title)s.%(ext)s',
    'merge_output_format': 'mp4',
    'quiet': True,
    'cookiefile': COOKIES_FILE,
}

def is_url(text):
    return re.match(r'^https?://', text)

@dp.message(F.text)
async def handle_message(message: types.Message):
    url = message.text.strip()

    if not is_url(url):
        await message.reply("❌ هذا ليس رابطاً صحيحاً.")
        return

    await message.reply("🔄 جاري التحميل، انتظر قليلاً...")

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)

        if os.path.exists(file_path):
            input_file = FSInputFile(file_path)
            if file_path.endswith(('.mp4', '.mkv', '.webm')):
                await message.reply_video(input_file, caption=info.get("title", "📽 تم التحميل"))
            elif file_path.endswith(('.mp3', '.wav', '.m4a')):
                await message.reply_audio(input_file, caption=info.get("title", "🎵 تم التحميل"))
            else:
                await message.reply_document(input_file, caption="📄 تم التحميل")

            os.remove(file_path)
        else:
            await message.reply("⚠️ لم يتم العثور على الملف بعد التحميل.")
    except Exception as e:
        await message.reply(f"❌ حدث خطأ أثناء التحميل:\n<code>{str(e)}</code>")

async def main():
    os.makedirs("downloads", exist_ok=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
