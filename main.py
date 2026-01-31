# ========== BAGIAN 1 ==========
# IMPORT, KONFIG, ACCOUNTS, SETUP DASAR

import asyncio
import os
import re
import random
import aiohttp
from telethon import types
from datetime import datetime
from zoneinfo import ZoneInfo

from telethon import TelegramClient, events
from telethon.sessions import StringSession
from flask import Flask
from threading import Thread

import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs, urlencode

# === KONFIGURASI UTAMA ===
API_ID = 20958475
API_HASH = '1cfb28ef51c138a027786e43a27a8225'

# === DAFTAR AKUN ===
ACCOUNTS = [
    {
        "session": "1BVtsOLEBu2sKGiucJdjVpu-yCdSeZfGNx_83A_Ycv4f5hKCPROda5fzwUrhanA-9kRrgzB7-Umze9JWdyAQDZdOLNFzd5IRF4gVs9HOuZ_aTlC7uD82NOfJK57dinjhpWWQG-JGWIhsjsqAYLblruPebQ8hQqllzuy0A2Z2WIXb0-rMEd1V2HMORRxPkCNxB_gvtDw-zWRQ_oJWrjtkSqXvP2L5eGf3NGyaeFsrR_zGyMVriZkFcwxfQ0XBRG1hcITZR4UsILV5MdxfRN6QnXve59vlmDbnLN7ORZh5j3d8I-VcDzAhQPzlEmM9Lf24H2SSKGpYgYXqIR3NLDX6wZ0wXHC8I7wQ=",
        "log_channel": None,
        "log_admin": 7828063345,
        "features": [
            "anti_view_once",
            "heartbeat",
            "downloader",
            "uguu",
            "catbox",
            "pomf2",
            "quax",
            "litterbox",
            "offshore",
        ],
    },
]

# list global client (diisi di main)
clients = []

# waktu start untuk /ping uptime
start_time_global = datetime.now()







async def upload_to_offshore(path: str) -> str:
    # Daftar kemungkinan endpoint
    endpoints = [
        "api/upload",
        "upload",
        "api.php",
        "index.php",
        "u",
        "upload.php"
    ]

    # Daftar kemungkinan nama field
    field_names = [
        "files[]",
        "file",
        "fileToUpload",
        "data"
    ]

    filename = os.path.basename(path)

    # Baca file ke memory agar cepat
    with open(path, "rb") as f:
        file_content = f.read()

    async with aiohttp.ClientSession() as session:
        # Loop semua kombinasi endpoint dan field
        for ep in endpoints:
            for field in field_names:
                try:
                    form = aiohttp.FormData()
                    form.add_field(field, file_content, filename=filename)

                    async with session.post(f"https://files.offshore.cat/{ep}", data=form) as resp:
                        
                        # Jika server merespon 200 OK
                        if resp.status == 200:
                            try:
                                data = await resp.json()

                                # Struktur JSON 1 (Standar Lolisafe)
                                if "files" in data:
                                    raw_url = data["files"][0]["url"]
                                # Struktur JSON 2
                                elif "file" in data and "url" in data["file"]:
                                    raw_url = data["file"]["url"]
                                # Struktur JSON 3 (Simple)
                                elif "url" in data:
                                    raw_url = data["url"]
                                else:
                                    continue # Struktur salah, lanjut coba lagi

                                # Perbaikan Link (Jika relative path)
                                if raw_url.startswith("/"):
                                    return "https://files.offshore.cat" + raw_url
                                return raw_url

                            except:
                                # Coba Parse sebagai Plain Text
                                text = (await resp.text()).strip()
                                if text.startswith("http"):
                                    return text
                                if text.startswith("/api/file/"):
                                    return "https://files.offshore.cat" + text

                except Exception:
                    # Jika error (404, timeout), lanjut ke kombinasi berikutnya
                    continue

    # Jika semua percobaan gagal
    raise Exception(
        "⚠️ Gagal upload ke Offshore.cat.\n"
        "Tidak ditemukan endpoint upload publik.\n"
        "Kemungkinan upload hanya via JavaScript browser."
    )

async def offshore_handler(event, client):
    if not event.is_private:
        return

    me = await client.get_me()
    if event.sender_id != me.id:
        return

    # Case 1: Reply ke media/file
    if event.is_reply:
        reply_msg = await event.get_reply_message()
        if not (reply_msg.media or reply_msg.document):
            await event.respond("❌ Reply harus ke media/file.")
            return

        await event.respond("📤 Sedang upload ke Offshore.cat (Mencoba Endpoint)...")
        try:
            path = await client.download_media(reply_msg)
            offshore_url = await upload_to_offshore(path)
            os.remove(path)
            await event.respond(f"✅ File berhasil diupload!\n🔗 {offshore_url}")
        except Exception as e:
            await event.respond(f"❌ Error upload ke Offshore.cat: `{e}`")
        return

    # Case 2: Kirim media dengan caption /offshore
    if event.media and event.raw_text.strip() == "/offshore":
        await event.respond("📤 Sedang upload ke Offshore.cat (Mencoba Endpoint)...")
        try:
            path = await client.download_media(event.message)
            offshore_url = await upload_to_offshore(path)
            os.remove(path)
            await event.respond(f"✅ File berhasil diupload!\n🔗 {offshore_url}")
        except Exception as e:
            await event.respond(f"❌ Error upload ke Offshore.cat: `{e}`")
        return

    await event.respond("❌ Gunakan `/offshore` dengan reply ke file/media, atau kirim media dengan caption `/offshore`.")



async def upload_to_litterbox(path: str, time_str: str = "1h") -> str:
    # Acak panjang nama file antara 6 atau 16 sesuai permintaan
    name_length = random.choice([6, 16])
    
    async with aiohttp.ClientSession() as session:
        with open(path, "rb") as f:
            form = aiohttp.FormData()
            # Parameter wajib sesuai HTML Litterbox
            form.add_field("reqtype", "fileupload")
            form.add_field("time", time_str) 
            form.add_field("fileNameLength", str(name_length))
            form.add_field("fileToUpload", f, filename=os.path.basename(path))
            
            # Endpoint API Litterbox
            async with session.post("https://litterbox.catbox.moe/resources/internals/api.php", data=form) as resp:
                if resp.status != 200:
                    raise Exception(f"Upload gagal dengan status code {resp.status}")
                # Litterbox mengembalikan plain text URL, bukan JSON
                return (await resp.text()).strip()

async def litterbox_handler(event, client):
    if not event.is_private:
        return

    me = await client.get_me()
    if event.sender_id != me.id:
        return

    # === PARSING DURASI ===
    # Default di website adalah 1 Jam
    time_code = "1h"
    time_text = "1 Jam"

    # Ambil argumen durasi
    text_args = event.pattern_match.group(1).strip().lower() if event.pattern_match.group(1) else ""
    
    if text_args:
        if text_args in ["1h", "1", "1hour", "hour"]:
            time_code = "1h"
            time_text = "1 Jam"
        elif text_args in ["12h", "12", "12hour"]:
            time_code = "12h"
            time_text = "12 Jam"
        elif text_args in ["1d", "24h", "1day", "24"]:
            time_code = "24h"
            time_text = "1 Hari"
        elif text_args in ["3d", "72h", "3day", "72"]:
            time_code = "72h"
            time_text = "3 Hari"

    # Case 1: Reply ke media/file
    if event.is_reply:
        reply_msg = await event.get_reply_message()
        if not (reply_msg.media or reply_msg.document):
            await event.respond("❌ Reply harus ke media/file.")
            return

        await event.respond(f"📤 Sedang upload ke Litterbox ({time_text}, Random Chars)...")
        try:
            path = await client.download_media(reply_msg)
            # Nama file akan diacak 6 atau 16 karakter otomatis di fungsi upload
            litter_url = await upload_to_litterbox(path, time_str=time_code)
            os.remove(path)
            await event.respond(f"✅ File berhasil diupload! ({time_text})\n🔗 {litter_url}")
        except Exception as e:
            await event.respond(f"❌ Error upload ke Litterbox: `{e}`")
        return

    # Case 2: Kirim media dengan caption /litterbox
    if event.media:
        await event.respond(f"📤 Sedang upload ke Litterbox ({time_text}, Random Chars)...")
        try:
            path = await client.download_media(event.message)
            litter_url = await upload_to_litterbox(path, time_str=time_code)
            os.remove(path)
            await event.respond(f"✅ File berhasil diupload! ({time_text})\n🔗 {litter_url}")
        except Exception as e:
            await event.respond(f"❌ Error upload ke Litterbox: `{e}`")
        return

    # Bantuan
    help_text = (
        "❌ Gunakan `/litterbox` dengan reply ke file/media.\n\n"
        "⏱️ **Set Durasi:**\n"
        "• `/litterbox 1h` -> 1 Jam (Default)\n"
        "• `/litterbox 12h` -> 12 Jam\n"
        "• `/litterbox 24h` -> 1 Hari\n"
        "• `/litterbox 72h` -> 3 Hari\n\n"
        "🎲 **Panjang Nama File:**\n"
        "Otomatis diacak antara 6 atau 16 karakter."
    )
    await event.respond(help_text)


async def upload_to_quax(path: str, expiry: str = "-1") -> str:
    # expiry = "-1" (Permanent), "1", "7", "30", atau "365"
    async with aiohttp.ClientSession() as session:
        with open(path, "rb") as f:
            form = aiohttp.FormData()
            form.add_field("files[]", f, filename=os.path.basename(path))
            # Tambahkan parameter expiry sesuai request website qu.ax
            form.add_field("expiry", expiry)
            
            async with session.post("https://qu.ax/upload", data=form) as resp:
                if resp.status != 200:
                    raise Exception(f"Upload gagal dengan status code {resp.status}")
                
                data = await resp.json()
                
                # Validasi respons JSON
                if not data.get("success") or not data.get("files"):
                    raise Exception("Format respons tidak valid")
                    
                return data["files"][0]["url"]

async def quax_handler(event, client):
    if not event.is_private:
        return

    me = await client.get_me()
    if event.sender_id != me.id:
        return

    # === PARSING DURASI ===
    # Default ke 1 Hari (1)
    expiry_code = "1"
    expiry_text = "1 Hari"

    # Ambil argumen dari command (misal: /quax 7d atau /quax 1h)
    text_args = event.pattern_match.group(1).strip().lower() if event.pattern_match.group(1) else ""
    
    if text_args:
        # Mapping teks user ke kode API qu.ax
        if text_args in ["1d", "1", "1day", "daily"]:
            expiry_code = "1"
            expiry_text = "1 Hari"
        elif text_args in ["7d", "7", "1w", "weekly", "7days"]:
            expiry_code = "7"
            expiry_text = "7 Hari"
        elif text_args in ["30d", "30", "1m", "monthly", "30days"]:
            expiry_code = "30"
            expiry_text = "30 Hari"
        elif text_args in ["365d", "365", "1y", "yearly", "1year"]:
            expiry_code = "365"
            expiry_text = "1 Tahun"
        elif text_args in ["perm", "-1", "forever", "permanent"]:
            expiry_code = "-1"
            expiry_text = "Permanen"

    # Case 1: Reply ke media/file
    if event.is_reply:
        reply_msg = await event.get_reply_message()
        if not (reply_msg.media or reply_msg.document):
            await event.respond("❌ Reply harus ke media/file.")
            return

        await event.respond(f"📤 Sedang upload ke Qu.ax ({expiry_text})...")
        try:
            path = await client.download_media(reply_msg)
            quax_url = await upload_to_quax(path, expiry=expiry_code)
            os.remove(path)
            await event.respond(f"✅ File berhasil diupload! ({expiry_text})\n🔗 {quax_url}")
        except Exception as e:
            await event.respond(f"❌ Error upload ke Qu.ax: `{e}`")
        return

    # Case 2: Kirim media dengan caption /quax
    if event.media:
        # Cek apakah ada teks durasi setelah command, jika tidak pakai default
        await event.respond(f"📤 Sedang upload ke Qu.ax ({expiry_text})...")
        try:
            path = await client.download_media(event.message)
            quax_url = await upload_to_quax(path, expiry=expiry_code)
            os.remove(path)
            await event.respond(f"✅ File berhasil diupload! ({expiry_text})\n🔗 {quax_url}")
        except Exception as e:
            await event.respond(f"❌ Error upload ke Qu.ax: `{e}`")
        return

    # Bantuan penggunaan
    help_text = (
        "❌ Gunakan `/quax` dengan reply ke file/media.\n\n"
        "⏱️ **Set Durasi:**\n"
        "• `/quax 1d` -> 1 Hari (Default)\n"
        "• `/quax 7d` -> 7 Hari\n"
        "• `/quax 30d` -> 30 Hari\n"
        "• `/quax 1y` -> 1 Tahun\n"
        "• `/quax perm` -> Permanen"
    )
    await event.respond(help_text)


async def upload_to_pomf2(path: str) -> str:
    async with aiohttp.ClientSession() as session:
        with open(path, "rb") as f:
            form = aiohttp.FormData()
            form.add_field("files[]", f, filename=os.path.basename(path))
            resp = await session.post("https://pomf2.lain.la/upload.php", data=form)
            data = await resp.json()
            return data["files"][0]["url"]

async def pomf2_handler(event, client):
    if not event.is_private:
        return

    me = await client.get_me()
    if event.sender_id != me.id:
        return

    # Case 1: Reply ke media/file
    if event.is_reply:
        reply_msg = await event.get_reply_message()
        if not (reply_msg.media or reply_msg.document):
            await event.respond("❌ Reply harus ke media/file.")
            return

        await event.respond("📤 Sedang upload ke Pomf2...")
        try:
            path = await client.download_media(reply_msg)
            pomf_url = await upload_to_pomf2(path)
            os.remove(path)
            await event.respond(f"✅ File berhasil diupload!\n🔗 {pomf_url}")
        except Exception as e:
            await event.respond(f"❌ Error upload ke Pomf2")
        return

    # Case 2: Kirim media dengan caption /pomf
    if event.media and event.raw_text.strip() == "/pomf":
        await event.respond("📤 Sedang upload ke Pomf2...")
        try:
            path = await client.download_media(event.message)
            pomf_url = await upload_to_pomf2(path)
            os.remove(path)
            await event.respond(f"✅ File berhasil diupload!\n🔗 {pomf_url}")
        except Exception as e:
            await event.respond(f"❌ Error upload ke Pomf2")
        return

    await event.respond("❌ Gunakan `/pomf` dengan reply ke file/media, atau kirim media dengan caption `/pomf`.")

async def upload_to_uguu(path):
    async with aiohttp.ClientSession() as session:
        with open(path, "rb") as f:
            form = aiohttp.FormData()
            form.add_field("files[]", f, filename=os.path.basename(path))
            resp = await session.post("https://uguu.se/upload.php", data=form)
            json_resp = await resp.json()
            if isinstance(json_resp, dict) and "files" in json_resp:
                return json_resp["files"][0]["url"]
            raise ValueError(f"Unexpected response")

async def uguu_handler(event, client):
    if not event.is_private:
        return

    me = await client.get_me()
    if event.sender_id != me.id:
        return

    # Case 1: Reply ke media/file
    if event.is_reply:
        reply_msg = await event.get_reply_message()
        if not (reply_msg.media or reply_msg.document):
            await event.respond("❌ Reply harus ke media/file.")
            return

        await event.respond("📤 Sedang upload ke Uguu...")
        try:
            path = await client.download_media(reply_msg)
            uguu_url = await upload_to_uguu(path)
            os.remove(path)
            await event.respond(f"✅ File berhasil diupload!\n🔗 {uguu_url}")
        except Exception as e:
            await event.respond(f"❌ Error upload ke Uguu")
        return

    # Case 2: Kirim media dengan caption /uguu
    if event.media and event.raw_text.strip() == "/uguu":
        await event.respond("📤 Sedang upload ke Uguu...")
        try:
            path = await client.download_media(event.message)
            uguu_url = await upload_to_uguu(path)
            os.remove(path)
            await event.respond(f"✅ File berhasil diupload!\n🔗 {uguu_url}")
        except Exception as e:
            await event.respond(f"❌ Error upload ke Uguu")
        return

    await event.respond("❌ Gunakan `/uguu` dengan reply ke file/media, atau kirim media dengan caption `/uguu`.")

async def upload_to_catbox(path):
    async with aiohttp.ClientSession() as session:
        with open(path, "rb") as f:
            form = aiohttp.FormData()
            form.add_field("reqtype", "fileupload")
            form.add_field("fileToUpload", f, filename=os.path.basename(path))
            resp = await session.post("https://catbox.moe/user/api.php", data=form)
            return (await resp.text()).strip()

async def catbox_handler(event, client):
    if not event.is_private:
        return

    me = await client.get_me()
    if event.sender_id != me.id:
        return

    # Case 1: Reply ke media/file
    if event.is_reply:
        reply_msg = await event.get_reply_message()
        if not (reply_msg.media or reply_msg.document):
            await event.respond("❌ Reply harus ke media/file.")
            return

        await event.respond("📤 Sedang upload ke Catbox...")
        try:
            path = await client.download_media(reply_msg)
            catbox_url = await upload_to_catbox(path)
            os.remove(path)
            await event.respond(f"✅ File berhasil diupload!\n🔗 {catbox_url}")
        except Exception as e:
            await event.respond(f"❌ Error upload ke Catbox")
        return

    # Case 2: Kirim media dengan caption /catbox
    if event.media and event.raw_text.strip() == "/catbox":
        await event.respond("📤 Sedang upload ke Catbox...")
        try:
            path = await client.download_media(event.message)
            catbox_url = await upload_to_catbox(path)
            os.remove(path)
            await event.respond(f"✅ File berhasil diupload!\n🔗 {catbox_url}")
        except Exception as e:
            await event.respond(f"❌ Error upload ke Catbox")
        return

    await event.respond("❌ Gunakan `/catbox` dengan reply ke file/media, atau kirim media dengan caption `/catbox`.")

# === FITUR: ANTI VIEW-ONCE ===
async def anti_view_once_and_ttl(event, client, log_channel, log_admin):
    if not event.is_private:
        return

    msg = event.message
    ttl = getattr(msg.media, "ttl_seconds", None)

    if not msg.media or not ttl:
        return

    try:
        sender = await msg.get_sender()
        sender_name = sender.first_name or "Unknown"
        sender_username = f"@{sender.username}" if sender.username else "-"
        sender_id = sender.id

        chat = await event.get_chat()
        chat_title = getattr(chat, "title", "Private Chat")
        chat_id = chat.id

        caption = (
            "🔓 **MEDIA VIEW-ONCE / TIMER TERTANGKAP**\n\n"
            f"👤 **Pengirim:** `{sender_name}`\n"
            f"🔗 **Username:** {sender_username}\n"
            f"🆔 **User ID:** `{sender_id}`\n\n"
            f"💬 **Dari Chat:** `{chat_title}`\n"
            f"🆔 **Chat ID:** `{chat_id}`\n\n"
            f"⏱ **Timer:** `{ttl} detik`\n"
            f"📥 **Status:** Berhasil disalin ✅"
        )

        folder = "111AntiViewOnce"
        os.makedirs(folder, exist_ok=True)
        file = await msg.download_media(file=folder)

        if log_channel:
            await client.send_file(log_channel, file, caption=caption)
        if log_admin:
            await client.send_file(log_admin, file, caption=caption)

        if file and os.path.exists(file):
            os.remove(file)

    except Exception as e:
        if log_admin:
            await client.send_message(log_admin, f"⚠ Error anti-viewonce")

# === FITUR: HEARTBEAT ===
async def heartbeat(client, log_admin, log_channel, akun_nama):
    last_msg_id = None
    start_time = datetime.now()

    while True:
        try:
            uptime = datetime.now() - start_time
            uptime_str = str(uptime).split('.')[0]
            server_time = datetime.now(ZoneInfo("Asia/Jakarta")).strftime("%H:%M:%S || %d-%m-%Y")

            start = datetime.now()
            end = datetime.now()
            ms = (end - start).microseconds // 1000
            

            if last_msg_id:
                try:
                    if log_admin:
                        await client.delete_messages(log_admin, last_msg_id)
                except:
                    pass

            text = (
                f"💓 **HEARTBEAT CHECK** 💓\n\n"
                f"👤 Akun: {akun_nama}\n"
                f"⏱ Uptime: `{uptime_str}`\n"
                f"📡 **Status:** 🟢 Online\n"
                f"🕒 Server: {server_time}\n"
            )

            msg = None
            if log_admin:
                msg = await client.send_message(log_admin, text)

            if msg:
                last_msg_id = msg.id

        except Exception as e:
            if log_admin:
                await client.send_message(log_admin, f"⚠ Heartbeat Error")

        await asyncio.sleep(300)

# === FITUR: DOWNLOADER ===
def is_valid_url(url):
    """Validasi apakah string adalah URL yang valid"""
    try:
        result = urlparse(url)
        return all([result.scheme in ['http', 'https'], result.netloc])
    except:
        return False

def sanitize_url(url):
    """Membersihkan URL dari tracking parameters"""
    try:
        parsed = urlparse(url)
        tracking_params = ["utm_source", "utm_medium", "utm_campaign", "fbclid", "gclid", "_gl"]
        query_params = parse_qs(parsed.query)
        for param in tracking_params:
            query_params.pop(param, None)
        
        clean_query = urlencode(query_params, doseq=True)
        clean_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        if clean_query:
            clean_url += f"?{clean_query}"
        return clean_url.strip()
    except:
        return url.strip()

PLATFORM_PATTERNS = {
    'tiktok': re.compile(r'(?:^|\.)tiktok\.com', re.IGNORECASE),
    'instagram': re.compile(r'(?:^|\.)instagram\.com|instagr\.am', re.IGNORECASE),
}

def detect_platform(url):
    """Deteksi platform dari URL dengan regex yang lebih akurat"""
    for platform, pattern in PLATFORM_PATTERNS.items():
        if pattern.search(url):
            return platform
    return None

def get_best_video_url(video_data, platform='tiktok'):
    """Memilih URL video dengan kualitas terbaik berdasarkan prioritas"""
    if platform == 'tiktok':
        # Prioritas: nowatermark_hd > nowatermark > watermark
        if video_data.get('nowatermark_hd'):
            return video_data['nowatermark_hd']
        elif video_data.get('nowatermark'):
            return video_data['nowatermark']
        elif video_data.get('watermark'):
            return video_data['watermark']
    return None

async def download_tiktok(url, quality='best'):
    """Handler untuk download TikTok - updated to match parse-duration.ts"""
    try:
        headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Origin': 'https://www.tikwm.com',
            'Referer': 'https://www.tikwm.com/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        params = {
            'url': url,
            'hd': '1' if quality == 'best' else '0'
        }
        
        response = requests.post('https://www.tikwm.com/api/', headers=headers, params=params, timeout=15)
        response.raise_for_status()
        
        json_data = response.json()
        res = json_data.get('data')
        
        if not res:
            return {'success': False, 'message': 'Gagal mengambil data dari TikTok'}
        
        # Format data sesuai parse-duration.ts
        data = []
        if not res.get('size') and not res.get('wm_size') and not res.get('hd_size'):
            # TikTok slideshow/images
            for img_url in res.get('images', []):
                data.append({'type': 'photo', 'url': img_url})
        else:
            # TikTok video
            if res.get('wmplay'):
                data.append({'type': 'watermark', 'url': res['wmplay']})
            if res.get('play'):
                data.append({'type': 'nowatermark', 'url': res['play']})
            if res.get('hdplay'):
                data.append({'type': 'nowatermark_hd', 'url': res['hdplay']})
        
        result = {
            'success': True,
            'platform': 'TikTok',
            'type': 'images' if res.get('images') else 'video',
            'data': data,
            'images': res.get('images', []),
            'video': {
                'watermark': res.get('wmplay', ''),
                'nowatermark': res.get('play', ''),
                'nowatermark_hd': res.get('hdplay', '')
            },
            'author': {
                'id': res.get('author', {}).get('id', ''),
                'username': res.get('author', {}).get('unique_id', ''),
                'nickname': res.get('author', {}).get('nickname', ''),
                'avatar': res.get('author', {}).get('avatar', ''),
            },
            'title': res.get('title', ''),
            'duration': res.get('duration', 0),
            'cover': res.get('cover', ''),
            'music_info': {
                'id': res.get('music_info', {}).get('id', ''),
                'title': res.get('music_info', {}).get('title', ''),
                'author': res.get('music_info', {}).get('author', ''),
                'album': res.get('music_info', {}).get('album'),
                'url': res.get('music') or res.get('music_info', {}).get('play', ''),
            },
            'stats': {
                'views': res.get('play_count', 0),
                'likes': res.get('digg_count', 0),
                'comments': res.get('comment_count', 0),
                'shares': res.get('share_count', 0),
                'downloads': res.get('download_count', 0),
            }
        }
        
        return result
        
    except Exception as e:
        return {'success': False, 'message': f'Error TikTok'}

async def download_instagram(url, quality='best'):
    """Handler untuk download Instagram - updated to return better data"""
    try:
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Origin': 'https://yt1s.io',
            'Referer': 'https://yt1s.io/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        data = {
            'q': url,
            'w': '',
            'p': 'home',
            'lang': 'en'
        }
        
        response = requests.post('https://yt1s.io/api/ajaxSearch', headers=headers, data=data, timeout=15)
        response.raise_for_status()
        
        json_data = response.json()
        html = json_data.get('data', '')
        
        if not html:
            return {'success': False, 'message': 'Tidak ada data dari Instagram'}
        
        soup = BeautifulSoup(html, 'html.parser')
        links = soup.find_all('a', href=True, title=True)
        
        videos = []
        images = []
        thumb = ''
        
        for link in links:
            href = link['href']
            title = link['title'].lower()
            
            # Skip invalid URLs
            if not href.startswith('http') or href == '/en/home':
                continue
            
            if 'thumbnail' in title:
                thumb = href
            elif 'video' in title or 'mp4' in title:
                videos.append({'type': 'video', 'url': href})
            elif 'foto' in title or 'image' in title or 'photo' in title or 'jpg' in title:
                images.append({'type': 'photo', 'url': href})
        
        # Determine media type
        has_videos = len(videos) > 0
        has_images = len(images) > 0
        
        if has_videos and has_images:
            media_type = 'mixed'
        elif has_videos:
            media_type = 'video'
        elif has_images:
            media_type = 'images'
        else:
            media_type = 'unknown'
        
        result = {
            'success': True,
            'platform': 'Instagram',
            'type': media_type,
            'data': videos + images,  # Combined list
            'videos': videos,
            'images': images,
            'thumb': thumb
        }
        
        return result
        
    except Exception as e:
        return {'success': False, 'message': f'Error Instagram'}

async def handle_downloader(event, client):
    """Handler utama untuk command /d dan /download"""
    if not event.is_private:
        return
    
    me = await client.get_me()
    if event.sender_id != me.id:
        return
    
    input_text = event.pattern_match.group(2).strip() if event.pattern_match.group(2) else ''
    
    if not input_text:
        if event.is_reply:
            reply = await event.get_reply_message()
            if reply and reply.message:
                input_text = reply.message.strip()
            else:
                await event.reply("❌ Pesan balasan tidak berisi link.")
                return
        else:
            await event.reply(
                "❌ **Cara pakai:**\n"
                "`/d <link>` atau `/download <link>`\n"
                "atau reply pesan yang berisi link\n\n"
                "**Platform support:**\n"
                "• TikTok (video, images, audio)\n"
                "• Instagram (video, images, mixed)"
            )
            return
    
    if not is_valid_url(input_text):
        await event.reply("❌ Input bukan link yang valid!")
        return
    
    clean_url = sanitize_url(input_text)
    platform = detect_platform(clean_url)
    
    if not platform:
        await event.reply("❌ Platform tidak didukung. Gunakan link dari TikTok atau Instagram.")
        return
    
    loading = await event.reply(f"⏳ Mengunduh dari **{platform.title()}**...")
    
    try:
        if platform == 'tiktok':
            result = await download_tiktok(clean_url)
        elif platform == 'instagram':
            result = await download_instagram(clean_url)
        else:
            await loading.edit("❌ Platform belum didukung")
            return
        
        
        if not result.get('success'):
            await event.reply(f"❌ {result.get('message', 'Gagal mengunduh')}")
            return
        
        # ===== TIKTOK HANDLER =====
        if platform == 'tiktok':
            if result['type'] == 'video':
                # Get best quality video
                video_url = get_best_video_url(result['video'], 'tiktok')
                
                if not video_url:
                    await event.reply("❌ Tidak ada URL video yang valid")
                    return
                
                caption = (
                    f"📹 **TikTok Video**\n\n"
                    f"👤 **Author:** @{result['author']['username']}\n"
                    f"📝 **Title:** {result['title']}\n"
                    f"⏱ **Duration:** {result['duration']}s\n"
                    f"👁 **Views:** {result['stats']['views']:,}\n"
                    f"❤️ **Likes:** {result['stats']['likes']:,}\n"
                    f"💬 **Comments:** {result['stats']['comments']:,}"
                )
                
                # Download and send video
                try:
                    video_res = requests.get(video_url, timeout=60, stream=True)
                    if video_res.status_code == 200:
                        video_filename = f"tiktok_{int(datetime.now().timestamp())}.mp4"
                        with open(video_filename, 'wb') as f:
                            for chunk in video_res.iter_content(chunk_size=8192):
                                f.write(chunk)
                        
                        await client.send_file(event.chat_id, video_filename, caption=caption)
                        os.remove(video_filename)
                    else:
                        await event.reply(f"{caption}\n\n🔗 [Download Video]({video_url})")
                except Exception as e:
                    await event.reply(f"{caption}\n\n🔗 [Download Video]({video_url})\n\n⚠️ Error")
                
                # Download and send audio/music if available
                music_url = result.get('music_info', {}).get('url')
                if music_url:
                    try:
                        music_caption = (
                            f"🎵 **TikTok Audio**\n\n"
                            f"🎼 **Title:** {result['music_info']['title']}\n"
                            f"👤 **Artist:** {result['music_info']['author']}"
                        )
                        
                        audio_res = requests.get(music_url, timeout=30, stream=True)
                        if audio_res.status_code == 200:
                            audio_filename = f"tiktok_audio_{int(datetime.now().timestamp())}.mp3"
                            with open(audio_filename, 'wb') as f:
                                for chunk in audio_res.iter_content(chunk_size=8192):
                                    f.write(chunk)
                            
                            await client.send_file(
                                event.chat_id, 
                                audio_filename, 
                                caption=music_caption,
                                voice_note=False,
                                attributes=[types.DocumentAttributeAudio(
                                    duration=result['duration'],
                                    title=result['music_info']['title'],
                                    performer=result['music_info']['author']
                                )]
                            )
                            os.remove(audio_filename)
                    except Exception as e:
                        pass  # Silent fail for audio
                        
            elif result['type'] == 'images':
                total_images = len(result['images'])
                caption = (
                    f"🖼 **TikTok Slideshow** ({total_images} foto)\n\n"
                    f"👤 **Author:** @{result['author']['username']}\n"
                    f"📝 **Title:** {result['title'][:100]}{'...' if len(result['title']) > 100 else ''}\n"
                    f"👁 **Views:** {result['stats']['views']:,}\n"
                    f"❤️ **Likes:** {result['stats']['likes']:,}\n"
                    f"💬 **Comments:** {result['stats']['comments']:,}"
                )
                
                # Download semua gambar
                all_files = []
                for idx, img_url in enumerate(result['images'], 1):
                    try:
                        img_res = requests.get(img_url, timeout=20)
                        if img_res.status_code == 200:
                            filename = f"tiktok_img_{int(datetime.now().timestamp())}_{idx}.jpg"
                            with open(filename, 'wb') as f:
                                f.write(img_res.content)
                            all_files.append(filename)
                    except:
                        pass
                
                if all_files:
                    # Split files menjadi chunks of 10
                    for i in range(0, len(all_files), 10):
                        chunk = all_files[i:i+10]
                        is_last_chunk = (i + 10 >= len(all_files))
                        
                        # Caption hanya di chunk terakhir
                        chunk_caption = caption if is_last_chunk else None
                        
                        await client.send_file(event.chat_id, chunk, caption=chunk_caption)
                    
                    # Hapus semua file
                    for f in all_files:
                        try:
                            os.remove(f)
                        except:
                            pass
                else:
                    await event.reply(f"{caption}\n\n⚠️ Gagal mengunduh gambar")
                
                # Send audio for slideshow too
                music_url = result.get('music_info', {}).get('url')
                if music_url:
                    try:
                        music_caption = (
                            f"🎵 **TikTok Audio**\n\n"
                            f"🎼 **Title:** {result['music_info']['title']}\n"
                            f"👤 **Artist:** {result['music_info']['author']}"
                        )
                        
                        audio_res = requests.get(music_url, timeout=30, stream=True)
                        if audio_res.status_code == 200:
                            audio_filename = f"tiktok_audio_{int(datetime.now().timestamp())}.mp3"
                            with open(audio_filename, 'wb') as f:
                                for chunk in audio_res.iter_content(chunk_size=8192):
                                    f.write(chunk)
                            
                            await client.send_file(
                                event.chat_id, 
                                audio_filename, 
                                caption=music_caption,
                                voice_note=False,
                                attributes=[types.DocumentAttributeAudio(
                                    duration=result.get('duration', 0),
                                    title=result['music_info']['title'],
                                    performer=result['music_info']['author']
                                )]
                            )
                            os.remove(audio_filename)
                    except Exception as e:
                        pass  # Silent fail for audio
                      
            try:
              await loading.delete()
            except:
              pass
        
        # ===== INSTAGRAM HANDLER =====
        elif platform == 'instagram':
            if result['type'] == 'video':
                video_items = result['videos']
                total_videos = len(video_items)
                
                if total_videos == 1:
                    # Single video - send directly
                    video_url = video_items[0]['url']
                    caption = f"📹 **Instagram Video**"
                    
                    try:
                        video_res = requests.get(video_url, timeout=60, stream=True)
                        if video_res.status_code == 200:
                            video_filename = f"instagram_{int(datetime.now().timestamp())}.mp4"
                            with open(video_filename, 'wb') as f:
                                for chunk in video_res.iter_content(chunk_size=8192):
                                    f.write(chunk)
                            
                            await client.send_file(event.chat_id, video_filename, caption=caption)
                            os.remove(video_filename)
                        else:
                            await event.reply(f"{caption}\n\n🔗 [Download]({video_url})")
                    except Exception as e:
                        await event.reply(f"{caption}\n\n🔗 [Download]({video_url})")
                else:
                    # Multiple videos - download semua
                    all_files = []
                    for idx, video_item in enumerate(video_items, 1):
                        try:
                            video_url = video_item['url']
                            video_res = requests.get(video_url, timeout=60, stream=True)
                            if video_res.status_code == 200:
                                filename = f"instagram_video_{int(datetime.now().timestamp())}_{idx}.mp4"
                                with open(filename, 'wb') as f:
                                    for chunk in video_res.iter_content(chunk_size=8192):
                                        f.write(chunk)
                                all_files.append(filename)
                        except:
                            pass
                    
                    if all_files:
                        # Split files menjadi chunks of 10
                        for i in range(0, len(all_files), 10):
                            chunk = all_files[i:i+10]
                            is_last_chunk = (i + 10 >= len(all_files))
                            
                            # Caption hanya di chunk terakhir
                            chunk_caption = f"📹 **Instagram Videos** ({len(all_files)} videos)" if is_last_chunk else None
                            
                            await client.send_file(event.chat_id, chunk, caption=chunk_caption)
                        
                        # Hapus semua file
                        for f in all_files:
                            try:
                                os.remove(f)
                            except:
                                pass
                    else:
                        # Fallback to links
                        for idx, video_item in enumerate(video_items[:5], 1):
                            await event.reply(f"📹 **Instagram Video {idx}**\n\n🔗 [Download]({video_item['url']})")
                            
            elif result['type'] == 'images':
                image_items = result['images']
                total_images = len(image_items)
                
                if total_images == 1:
                    # Single image
                    img_url = image_items[0]['url']
                    caption = f"🖼 **Instagram Image**"
                    
                    try:
                        img_res = requests.get(img_url, timeout=20)
                        if img_res.status_code == 200:
                            filename = f"instagram_{int(datetime.now().timestamp())}.jpg"
                            with open(filename, 'wb') as f:
                                f.write(img_res.content)
                            
                            await client.send_file(event.chat_id, filename, caption=caption)
                            os.remove(filename)
                        else:
                            await event.reply(f"{caption}\n\n🔗 [Download]({img_url})")
                    except:
                        await event.reply(f"{caption}\n\n🔗 [Download]({img_url})")
                else:
                    # Multiple images - download semua
                    all_files = []
                    for idx, img_item in enumerate(image_items, 1):
                        try:
                            img_url = img_item['url']
                            img_res = requests.get(img_url, timeout=20)
                            if img_res.status_code == 200:
                                filename = f"instagram_img_{int(datetime.now().timestamp())}_{idx}.jpg"
                                with open(filename, 'wb') as f:
                                    f.write(img_res.content)
                                all_files.append(filename)
                        except:
                            pass
                    
                    if all_files:
                        # Split files menjadi chunks of 10
                        for i in range(0, len(all_files), 10):
                            chunk = all_files[i:i+10]
                            is_last_chunk = (i + 10 >= len(all_files))
                            
                            # Caption hanya di chunk terakhir
                            chunk_caption = f"🖼 **Instagram Images** ({len(all_files)} photos)" if is_last_chunk else None
                            
                            await client.send_file(event.chat_id, chunk, caption=chunk_caption)
                        
                        # Hapus semua file
                        for f in all_files:
                            try:
                                os.remove(f)
                            except:
                                pass
                    else:
                        # Fallback to links
                        for idx, img_item in enumerate(image_items[:10], 1):
                            await event.reply(f"🖼 **Instagram Image {idx}**\n\n🔗 [Download]({img_item['url']})")
                            
            elif result['type'] == 'mixed':
                all_media = result['data']
                total_media = len(all_media)
                
                # Download semua media
                all_files = []
                for idx, media_item in enumerate(all_media, 1):
                    try:
                        media_url = media_item['url']
                        media_type = media_item['type']
                        
                        media_res = requests.get(media_url, timeout=60, stream=True)
                        if media_res.status_code == 200:
                            ext = 'mp4' if media_type == 'video' else 'jpg'
                            filename = f"instagram_mixed_{int(datetime.now().timestamp())}_{idx}.{ext}"
                            
                            with open(filename, 'wb') as f:
                                if media_type == 'video':
                                    for chunk in media_res.iter_content(chunk_size=8192):
                                        f.write(chunk)
                                else:
                                    f.write(media_res.content)
                            
                            all_files.append(filename)
                    except:
                        pass
                
                if all_files:
                    # Hitung total video dan foto
                    video_count = len([m for m in all_media[:len(all_files)] if m['type'] == 'video'])
                    photo_count = len(all_files) - video_count
                    caption = f"📸 **Instagram Media** ({photo_count} photos, {video_count} videos)"
                    
                    # Split files menjadi chunks of 10
                    for i in range(0, len(all_files), 10):
                        chunk = all_files[i:i+10]
                        is_last_chunk = (i + 10 >= len(all_files))
                        
                        # Caption hanya di chunk terakhir
                        chunk_caption = caption if is_last_chunk else None
                        
                        await client.send_file(event.chat_id, chunk, caption=chunk_caption)
                    
                    # Hapus semua file
                    for f in all_files:
                        try:
                            os.remove(f)
                        except:
                            pass
                else:
                    # Fallback to links
                    for idx, media_item in enumerate(all_media[:5], 1):
                        media_type_emoji = "📹" if media_item['type'] == 'video' else "🖼"
                        media_type_text = "Video" if media_item['type'] == 'video' else "Image"
                        await event.reply(f"{media_type_emoji} **Instagram {media_type_text} {idx}**\n\n🔗 [Download]({media_item['url']})")
            else:
                await event.reply("❌ Tidak ada media yang ditemukan")
                
            try:
              await loading.delete()
            except:
              pass
        
    except Exception as e:
        try:
            await loading.delete()
        except:
            pass
        await event.reply(f"❌ Terjadi error")

# ========== BAGIAN 3 ==========
# WEB SERVER, RESTART LOOP, MAIN + HANDLER

# === RAILWAY WEB SERVER ===
app = Flask('')

@app.route('/')
def home():
    return "Ubot aktif di Railway!", 200

def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    Thread(target=run).start()

# === AUTO RESTART LOOP ===
async def run_clients_forever():
    while True:
        tasks = []
        for client, _, _ in clients:
            tasks.append(asyncio.create_task(client.run_until_disconnected()))
        await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
        print("⚠ Client disconnect, restart 5 detik...")
        await asyncio.sleep(5)

# === MAIN ===
async def main():
    keep_alive()

    for index, acc in enumerate(ACCOUNTS, start=1):
        client = TelegramClient(StringSession(acc["session"]), API_ID, API_HASH)
        await client.start()
        akun_nama = f"Akun {index}"

        # === ANTI VIEW-ONCE ===
        if "anti_view_once" in acc["features"]:
            @client.on(events.NewMessage(incoming=True))
            async def anti_view_once(event, c=client, lc=acc["log_channel"], la=acc["log_admin"]):
                await anti_view_once_and_ttl(event, c, lc, la)

        # === HEARTBEAT ===
        if "heartbeat" in acc["features"]:
            asyncio.create_task(heartbeat(client, acc["log_admin"], acc["log_channel"], akun_nama))

        # === DOWNLOADER ===
        if "downloader" in acc["features"]:
            @client.on(events.NewMessage(pattern=r'^/(d|download)(?:\s+|$)(.*)'))
            async def downloader_event(event, c=client):
                await handle_downloader(event, c)
        
                

        if "uguu" in acc["features"]:
            @client.on(events.NewMessage(pattern=r"^/uguu$"))
            async def uguu_event(event, c=client):
                await uguu_handler(event, c)

        if "catbox" in acc["features"]:
            @client.on(events.NewMessage(pattern=r"^/catbox$"))
            async def catbox_event(event, c=client):
                await catbox_handler(event, c)
                
        if "pomf2" in acc["features"]:
            @client.on(events.NewMessage(pattern=r"^/pomf"))
            async def pomf2_event(event, c=client):
                await pomf2_handler(event, c)

        if "quax" in acc["features"]:
            @client.on(events.NewMessage(pattern=r"^/quax(?:\s+(.+))?"))
            async def quax_event(event, c=client):
                await quax_handler(event, c)

        if "litterbox" in acc["features"]:
            @client.on(events.NewMessage(pattern=r"^/litterbox(?:\s+(.+))?"))
            async def litterbox_event(event, c=client):
                await litterbox_handler(event, c)

        if "offshore" in acc["features"]:
            @client.on(events.NewMessage(pattern=r"^/offshore$"))
            async def offshore_event(event, c=client):
                await offshore_handler(event, c)

        





                             






          

        # === INFO RESTART ===
        fitur_list = acc.get("features", [])
        fitur_str = " | ".join(fitur_list) if fitur_list else "Tidak ada"
        text = (
            f"♻️ **Ubot Aktif**\n\n"
            f"👤 Akun: {akun_nama}\n"
            f"⚙️ Fitur: [{fitur_str}]\n"
            f"🕒 Waktu: {datetime.now(ZoneInfo('Asia/Jakarta')).strftime('%H:%M:%S || %d-%m-%Y')}\n"
            f"📡 Status: 🟢 Online"
        )
        if acc["log_admin"]:
            await client.send_message(acc["log_admin"], text)

        clients.append((client, acc.get("log_channel"), acc.get("log_admin")))

    print(f"✅ Ubot aktif dengan {len(clients)} akun.")
    await run_clients_forever()

asyncio.run(main())
