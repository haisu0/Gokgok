# ========== BAGIAN 1 ==========
# IMPORT, KONFIG, ACCOUNTS, SETUP DASAR

import asyncio
import os
import re
import mimetypes
import aiohttp
import speech_recognition as sr
from pydub import AudioSegment
from telethon import types
from datetime import datetime
from zoneinfo import ZoneInfo

from telethon import TelegramClient, events
from telethon.sessions import StringSession
from flask import Flask
from threading import Thread

from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.functions.messages import GetCommonChatsRequest

import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs, urlencode, unquote, quote
from telethon.tl.functions.account import UpdateProfileRequest
from telethon.tl.types import InputPhoto
from telethon.tl.functions.photos import DeletePhotosRequest, UploadProfilePhotoRequest

from telethon.tl.functions.account import GetPrivacyRequest, SetPrivacyRequest
from telethon.tl.types import (
    InputPrivacyKeyProfilePhoto, InputPrivacyKeyAbout,
    InputPrivacyValueAllowUsers, InputPrivacyValueDisallowAll
)

import os, mimetypes
from telethon import events
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.functions.photos import UploadProfilePhotoRequest, DeletePhotosRequest
from telethon.tl.functions.account import UpdateProfileRequest, GetPrivacyRequest, SetPrivacyRequest
from telethon.tl.types import (
    InputPrivacyKeyProfilePhoto, InputPrivacyKeyAbout,
    InputPrivacyValueDisallowAll, InputPrivacyValueAllowUsers,
    InputPhoto
)




# === KONFIGURASI UTAMA ===
API_ID = 20958475
API_HASH = '1cfb28ef51c138a027786e43a27a8225'

# === DAFTAR AKUN ===
ACCOUNTS = [
    {
        "session": "1BVtsOHUBuyP0TX5bq30qFUifUXh2tZgNsa31H7T0j9wpx_23OF2zutQYaQFU-9cdY1r6poU_kXwMM12dG3MJbdo3cEtiGSoapYwD2PahQ1kq8J2Fy00LZKEtzgtQLrJ7LLvL8xHk5gRMi26tyagCq_F9d6yy7hc8JfHejESJBExvytIiNm4oAIrL0GAFwjNQ8_9Uw_5Iqa0pQz2qBu21d4IV6ULC8t23_fNwm6zl0008ci1I2uTIBHxvhXBcdAuNv0WyAgxc8tigiJ1QtURfEMKobZkMoTWuVKipdYO8x9ed59_ICd_NpGos-W160Fbmy3mnTXijCVgTCQplvY49CpZ6oZp0RJ8=",
        "log_channel": None,
        "log_admin": 7828063345,
        "features": [
            "anti_view_once",
            "ping",
            "heartbeat",
            "save_media",
            "whois",
            "downloader",
            "hilih",
            "vn_to_text",
            "ai",
            "dongeng",
            "brat",
            "cecan",
            "blurface",
            "hd",
            "uguu",
            "catbox",
            "pomf2",
            "edit",
        ],
    },
    {
        "session": "1BVtsOKgBu0RyB8nXk6rWu_0WSYnv09yshY88SJhJ1ryY8V5blcjJaNjacZflwUwwqL2L2-4FhJYFELbWNnPPooaH3hSrPY9FwgtH1T5nD1K8n4WZSVUYMcPTfoWamHQd1FyeGhuHS4RLs26QvfK6q90YnH7eN3pSucwc3A_pqX1XzyTjWdn1P7DNjIpXAZYqCK5IX1XQXIT9R7rM2PoVF7K8B-tj45oGVZNECBSlY1Y9QWjE8tK9fTnQjQRVpnn_KTH3Z5zge7x-vpCFiDH3jU4hGCPUPypWimzTWWVAiLh9d_ZDEuARzUnTpG_yCSCmRKF6G3xiyUlzhP_DWedq-wQvlvIHxSU=",
        "log_channel": None,
        "log_admin": 8229706287,
        "features": [
            "anti_view_once",
            "ping",
            "heartbeat",
            "save_media",
            "whois",
            "downloader",
            "hilih",
            "vn_to_text",
            "ai",
            "dongeng",
            "brat",
            "cecan",
            "blurface",
            "hd",
            "uguu",
            "catbox",
            "pomf2",
            "edit",
        ],
    }
]

# list global client (diisi di main)
clients = []

# waktu start untuk /ping uptime
start_time_global = datetime.now()













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








async def edit1_handler(event, client):
    if not event.is_private:
        return

    me = await client.get_me()
    if event.sender_id != me.id:
        return

    args = event.raw_text.strip().split(maxsplit=1)
    prompt = None
    image_url = None

    # Case 1: Reply foto
    if event.is_reply:
        reply_msg = await event.get_reply_message()
        if reply_msg.photo:
            path = await client.download_media(reply_msg)
            image_url = await upload_to_uguu(path)
            os.remove(path)

            if reply_msg.text and not (len(args) > 1):
                prompt = reply_msg.text.strip()
            elif len(args) > 1:
                prompt = args[1]
            else:
                await event.respond("❌ Reply foto harus ada caption atau tambahkan teks setelah /edit1.")
                return

        elif reply_msg.text and ("http://" in reply_msg.text or "https://" in reply_msg.text):
            image_url = reply_msg.text.strip()
            if len(args) > 1:
                prompt = args[1]
            else:
                await event.respond("❌ Harus ada teks setelah /edit1 untuk prompt.")
                return
        else:
            await event.respond("❌ Reply hanya bisa ke foto atau teks berisi link gambar.")
            return

    # Case 2: Kirim foto dengan caption /edit <text>
    elif event.photo and event.raw_text.startswith("/edit1"):
        path = await client.download_media(event.message)
        image_url = await upload_to_uguu(path)
        os.remove(path)

        if len(args) > 1:
            prompt = args[1]
        else:
            await event.respond("❌ Harus ada teks setelah /edit1 untuk prompt.")
            return

    else:
        await event.respond("❌ Gunakan `/edit1 <text>` dengan reply foto/link, atau kirim foto dengan caption `/edit1 <text>`.")
        return

    if not image_url or not prompt:
        await event.respond("❌ Tidak ada gambar atau prompt yang valid.")
        return

    await event.respond("🖌️ Sedang mengedit foto...")

    try:
        # Encode URL agar spasi dan simbol aman
        encoded_url = quote(image_url, safe='')
        encoded_prompt = quote(prompt, safe='')
        
        api_url = f"https://api-faa.my.id/faa/editfoto?url={encoded_url}&prompt={encoded_prompt}"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url) as resp:
                if resp.status != 200:
                    text_error = await resp.text()
                    await event.respond(f"❌ Edit foto API gagal")
                    return
                
                # Cek apakah responnya JSON atau Gambar Langsung
                content_type = resp.headers.get('Content-Type', '')
                
                # Gunakan nama file unik berdasarkan waktu agar tidak bentrok
                output_path = f"edit1_result_{int(datetime.now().timestamp())}.png"

                if 'application/json' in content_type:
                    # Jika API return JSON (biasanya berisi url result)
                    data = await resp.json()
                    # Sesuaikan key ini dengan struktur JSON dari api-faa (biasanya 'url' atau 'result')
                    result_link = data.get("url") or data.get("result") or data.get("link")
                    
                    if result_link:
                        # Download gambar dari link yang diberikan API
                        async with session.get(result_link) as img_resp:
                            if img_resp.status == 200:
                                with open(output_path, "wb") as f:
                                    f.write(await img_resp.read())
                            else:
                                raise Exception("Gagal download hasil dari API")
                    else:
                        await event.respond(f"❌ API merespon JSON tapi tidak ada link gambar")
                        return
                else:
                    # Jika API return gambar langsung (binary)
                    with open(output_path, "wb") as f:
                        f.write(await resp.read())

        uguu_url = await upload_to_uguu(output_path)

        await client.send_file(
            event.chat_id,
            output_path,
            caption=f"🖌️ Edit foto selesai!\nPrompt: {prompt}\n🔗 {uguu_url}"
        )
        os.remove(output_path)

    except Exception as e:
        await event.respond(f"❌ Error edit foto")
        
        
        
async def edit2_handler(event, client):
    if not event.is_private:
        return

    me = await client.get_me()
    if event.sender_id != me.id:
        return

    args = event.raw_text.strip().split(maxsplit=1)
    prompt = None
    image_url = None

    # Case 1: Reply foto
    if event.is_reply:
        reply_msg = await event.get_reply_message()
        if reply_msg.photo:
            path = await client.download_media(reply_msg)
            image_url = await upload_to_uguu(path)
            os.remove(path)

            if reply_msg.text and not (len(args) > 1):
                prompt = reply_msg.text.strip()
            elif len(args) > 1:
                prompt = args[1]
            else:
                await event.respond("❌ Reply foto harus ada caption atau tambahkan teks setelah /edit2.")
                return

        elif reply_msg.text and ("http://" in reply_msg.text or "https://" in reply_msg.text):
            image_url = reply_msg.text.strip()
            if len(args) > 1:
                prompt = args[1]
            else:
                await event.respond("❌ Harus ada teks setelah /edit2 untuk prompt.")
                return
        else:
            await event.respond("❌ Reply hanya bisa ke foto atau teks berisi link gambar.")
            return

    # Case 2: Kirim foto dengan caption /edit2 <text>
    elif event.photo and event.raw_text.startswith("/edit2"):
        path = await client.download_media(event.message)
        image_url = await upload_to_uguu(path)
        os.remove(path)

        if len(args) > 1:
            prompt = args[1]
        else:
            await event.respond("❌ Harus ada teks setelah /edit2 untuk prompt.")
            return

    else:
        await event.respond("❌ Gunakan `/edit2 <text>` dengan reply foto/link, atau kirim foto dengan caption `/edit2 <text>`.")
        return

    if not image_url or not prompt:
        await event.respond("❌ Tidak ada gambar atau prompt yang valid.")
        return

    await event.respond("🖌️ Sedang mengedit foto (Nano Banana)...")

    try:
        # Encode URL
        encoded_url = quote(image_url, safe='')
        encoded_prompt = quote(prompt, safe='')
        
        api_url = f"https://api-faa.my.id/faa/nano-banana?url={encoded_url}&prompt={encoded_prompt}"
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url) as resp:
                if resp.status != 200:
                    await event.respond("❌ Edit foto API gagal.")
                    return
                
                content_type = resp.headers.get('Content-Type', '')
                output_path = f"edit2_result_{int(datetime.now().timestamp())}.png"

                if 'application/json' in content_type:
                    # Handle JSON response
                    data = await resp.json()
                    result_link = data.get("url") or data.get("result") or data.get("link")
                    
                    if result_link:
                        async with session.get(result_link) as img_resp:
                            if img_resp.status == 200:
                                with open(output_path, "wb") as f:
                                    f.write(await img_resp.read())
                            else:
                                raise Exception("Gagal download hasil dari API")
                    else:
                        await event.respond(f"❌ API merespon JSON tapi tidak ada link gambar")
                        return
                else:
                    # Handle Binary response
                    with open(output_path, "wb") as f:
                        f.write(await resp.read())

        uguu_url = await upload_to_uguu(output_path)

        await client.send_file(
            event.chat_id,
            output_path,
            caption=f"🖌️ Edit foto (Nano Banana) selesai!\nPrompt: {prompt}\n🔗 {uguu_url}"
        )
        os.remove(output_path)

    except Exception as e:
        await event.respond(f"❌ Error edit foto")





import random

VALID_EXT = (".jpg", ".jpeg", ".png", ".gif", ".webp")

async def hd_handler(event, client):
    if not event.is_private:
        return

    me = await client.get_me()
    if event.sender_id != me.id:
        return

    args = event.raw_text.strip().split()
    scale = None
    image_url = None

    if len(args) > 1 and args[1] in ["2", "4"]:
        scale = int(args[1])
        if len(args) > 2:
            image_url = args[2]
    elif len(args) > 1:
        image_url = args[1]

    if scale is None:
        scale = random.choice([2, 4])

    # ambil sumber gambar
    if not image_url:
        if event.is_reply:
            reply_msg = await event.get_reply_message()
            if reply_msg.photo:
                path = await client.download_media(reply_msg)
                image_url = await upload_to_uguu(path)
                os.remove(path)
            elif reply_msg.text and ("http://" in reply_msg.text or "https://" in reply_msg.text):
                image_url = reply_msg.text.strip()
            else:
                await event.respond("❌ Reply hanya bisa ke foto atau teks berisi link gambar.")
                return
        elif event.photo and args[0] == "/hd":
            path = await client.download_media(event.message)
            image_url = await upload_to_uguu(path)
            os.remove(path)
        else:
            await event.respond("❌ Gunakan `/hd`, `/hd 2`, `/hd 4` dengan reply foto, reply teks berisi link gambar, kirim foto dengan caption `/hd`, atau `/hd <link>`.")
            return

    if isinstance(image_url, str):
        if not image_url.lower().endswith(VALID_EXT):
            await event.respond("❌ Link bukan gambar valid. Harus berakhiran .jpg, .jpeg, .png, .gif, atau .webp.")
            return

    await event.respond(f"🔍 Sedang meng-upscale gambar dengan scale {scale}x...")

    try:
        # 1. Panggil API untuk hasil upscale
        api_url = f"https://api.siputzx.my.id/api/iloveimg/upscale?image={image_url}&scale={scale}"
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url) as resp:
                if resp.status != 200:
                    await event.respond("❌ Upscale API gagal.")
                    return
                path = "upscale_result.png"
                with open(path, "wb") as f:
                    f.write(await resp.read())

        # 2. Upload hasil ke Uguu
        uguu_url = await upload_to_uguu(path)

        # 3. Kirim foto langsung + link Uguu
        await client.send_file(
            event.chat_id,
            path,
            caption=f"✨ HD Upscale {scale}x selesai!\n🔗 {uguu_url}"
        )

        # 4. Hapus file lokal
        os.remove(path)

    except Exception as e:
        await event.respond(f"❌ Error HD")



VALID_EXT = (".jpg", ".jpeg", ".png", ".gif", ".webp")

async def blurface_handler(event, client):
    if not event.is_private:
        return

    me = await client.get_me()
    if event.sender_id != me.id:
        return

    image_url = None
    args = event.raw_text.strip().split(maxsplit=1)

    # 1. /blurface <link gambar>
    if len(args) > 1:
        image_url = args[1]

    # 2. Reply pesan
    elif event.is_reply:
        reply_msg = await event.get_reply_message()
        if reply_msg.photo:
            path = await client.download_media(reply_msg)
            image_url = await upload_to_uguu(path)
            os.remove(path)
        elif reply_msg.text and ("http://" in reply_msg.text or "https://" in reply_msg.text):
            image_url = reply_msg.text.strip()
        else:
            await event.respond("❌ Reply hanya bisa ke foto atau teks berisi link gambar.")
            return

    # 3. Kirim foto dengan caption /blurface
    elif event.photo and event.raw_text.strip() == "/blurface":
        path = await client.download_media(event.message)
        image_url = await upload_to_uguu(path)
        os.remove(path)

    else:
        await event.respond("❌ Gunakan `/blurface <link gambar>`, reply foto, reply teks berisi link gambar, atau kirim foto dengan caption `/blurface`.")
        return

    # Validasi link gambar
    if isinstance(image_url, str):
        if not image_url.lower().endswith(VALID_EXT):
            await event.respond("❌ Link bukan gambar valid. Harus berakhiran .jpg, .jpeg, .png, .gif, atau .webp.")
            return

    await event.respond("🔍 Sedang memproses blur face...")

    try:
        # 1. Panggil API blur face
        api_url = f"https://api.siputzx.my.id/api/iloveimg/blurface?image={image_url}"
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url) as resp:
                if resp.status != 200:
                    await event.respond("❌ Blur face API gagal.")
                    return
                path = "blurface_result.png"
                with open(path, "wb") as f:
                    f.write(await resp.read())

        # 2. Upload hasil ke Uguu
        uguu_url = await upload_to_uguu(path)

        # 3. Kirim hasil blur dengan caption + link
        await client.send_file(
            event.chat_id,
            path,
            caption=f"😎 Blur face selesai!\n🔗 {uguu_url}"
        )

        os.remove(path)

    except Exception as e:
        await event.respond(f"❌ Error blur face")



import html

async def brat_handler(event, client):
    if not event.is_private:
        return

    me = await client.get_me()
    if event.sender_id != me.id:
        return

    args = event.raw_text.strip().split(maxsplit=1)
    text = None

    if len(args) > 1:
        text = args[1]
    elif event.is_reply:
        reply_msg = await event.get_reply_message()
        if reply_msg.text:
            text = reply_msg.text
        else:
            await event.respond("❌ Fitur brat hanya bisa digunakan untuk reply pesan teks.")
            return
    else:
        await event.respond("❌ Gunakan `/brat <text>` atau reply pesan teks.")
        return

    await event.respond("🎀 Sedang membuat brat...")

    try:
        api_url = f"https://aqul-brat.hf.space/?text={text}"
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url) as resp:
                if resp.status != 200:
                    await event.respond("❌ API brat gagal.")
                    return
                path = "brat_result.png"
                with open(path, "wb") as f:
                    f.write(await resp.read())

        # Upload ke Uguu
        uguu_url = await upload_to_uguu(path)
        caption = f"🎀 Brat untuk teks: {html.escape(text)}\n🔗 {uguu_url}"

        # Kirim sebagai foto
        await client.send_file(event.chat_id, path, caption=caption)
        
        os.remove(path)

    except Exception as e:
        await event.respond(f"❌ Error brat")




# === FITUR: AI CHAT ===

async def ai_handler(event, client):
    # hanya aktif di private chat
    if not event.is_private:
        return

    me = await client.get_me()
    if event.sender_id != me.id:
        return

    # Ambil teks dari argumen
    input_text = (event.pattern_match.group(1) or "").strip()

    # Jika reply ke pesan lain
    if event.is_reply:
        reply = await event.get_reply_message()
        if reply:
            # Jika reply adalah media (foto, video, audio, dokumen), tolak
            if reply.media:
                return

            # Ambil isi text dari reply
            if reply.message:
                if input_text:
                    input_text = f"{input_text}\n\n{reply.message.strip()}"
                else:
                    input_text = reply.message.strip()

    if not input_text:
        await event.reply("❌ Harus ada teks atau reply pesan.")
        return

    # 🔄 pesan loading keren
    loading_msg = await event.reply("🤖✨ AI sedang berpikir keras...")

    try:
        # panggil API
        url = f"https://api.siputzx.my.id/api/ai/metaai?query={input_text}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=60) as resp:
                data = await resp.json()

        if data.get("status") and "data" in data:
            output = data["data"]
        else:
            output = "⚠ AI tidak memberikan respon."

        await loading_msg.edit(f"{output}", parse_mode="markdown")

    except Exception as e:
        await loading_msg.edit(f"⚠ Error AI")



async def ai2_handler(event, client):
    # hanya aktif di private chat
    if not event.is_private:
        return

    me = await client.get_me()
    if event.sender_id != me.id:
        return

    # Ambil teks dari argumen
    input_text = (event.pattern_match.group(1) or "").strip()

    # Jika reply ke pesan lain
    if event.is_reply:
        reply = await event.get_reply_message()
        if reply:
            # Jika reply adalah media (foto, video, audio, dokumen), tolak
            if reply.media:
                return

            # Ambil isi text dari reply
            if reply.message:
                if input_text:
                    input_text = f"{input_text}\n\n{reply.message.strip()}"
                else:
                    input_text = reply.message.strip()

    if not input_text:
        await event.reply("❌ Harus ada teks atau reply pesan.")
        return

    # 🔄 pesan loading keren
    loading_msg = await event.reply("🤖✨ AI sedang berpikir keras...")

    try:
        # panggil API
        url = f"https://zelapioffciall.koyeb.app/ai/castorice?text={input_text}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=60) as resp:
                data = await resp.json()

        if data.get("status") and "answer" in data:
            output = data["answer"]
        else:
            output = "⚠ AI tidak memberikan respon."

        await loading_msg.edit(f"{output}", parse_mode="markdown")

    except Exception as e:
        await loading_msg.edit(f"⚠ Error AI")


async def ai3_handler(event, client):
    # hanya aktif di private chat
    if not event.is_private:
        return

    me = await client.get_me()
    if event.sender_id != me.id:
        return

    # Ambil teks dari argumen
    input_text = (event.pattern_match.group(1) or "").strip()

    # Jika reply ke pesan lain
    if event.is_reply:
        reply = await event.get_reply_message()
        if reply:
            # Jika reply adalah media (foto, video, audio, dokumen), tolak
            if reply.media:
                return

            # Ambil isi text dari reply
            if reply.message:
                if input_text:
                    input_text = f"{input_text}\n\n{reply.message.strip()}"
                else:
                    input_text = reply.message.strip()

    if not input_text:
        await event.reply("❌ Harus ada teks atau reply pesan.")
        return

    # 🔄 pesan loading keren
    loading_msg = await event.reply("🤖✨ AI sedang berpikir keras...")

    try:
        # panggil API
        url = f"https://zelapioffciall.koyeb.app/ai/felo?q={input_text}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=60) as resp:
                data = await resp.json()

        if data.get("status") and "result" in data:
            output = data["result"]
            answer = output["answer"]
            
        else:
            answer = "⚠ AI tidak memberikan respon."

        await loading_msg.edit(f"{answer}", parse_mode="markdown")

    except Exception as e:
        await loading_msg.edit(f"⚠ Error AI")


async def ai4_handler(event, client):
    # hanya aktif di private chat
    if not event.is_private:
        return

    me = await client.get_me()
    if event.sender_id != me.id:
        return

    # Ambil teks dari argumen
    input_text = (event.pattern_match.group(1) or "").strip()

    # Jika reply ke pesan lain
    if event.is_reply:
        reply = await event.get_reply_message()
        if reply:
            # Jika reply adalah media (foto, video, audio, dokumen), tolak
            if reply.media:
                return

            # Ambil isi text dari reply
            if reply.message:
                if input_text:
                    input_text = f"{input_text}\n\n{reply.message.strip()}"
                else:
                    input_text = reply.message.strip()

    if not input_text:
        await event.reply("❌ Harus ada teks atau reply pesan.")
        return

    # 🔄 pesan loading keren
    loading_msg = await event.reply("🤖✨ AI sedang berpikir keras...")

    try:
        # panggil API
        url = f"https://zelapioffciall.koyeb.app/ai/kimi?text={input_text}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=60) as resp:
                data = await resp.json()

        if data.get("status") and "result" in data:
            output = data["result"]
            answer = output["response"]
            
        else:
            answer = "⚠ AI tidak memberikan respon."

        await loading_msg.edit(f"{answer}", parse_mode="markdown")

    except Exception as e:
        await loading_msg.edit(f"⚠ Error AI")


async def ai5_handler(event, client):
    # hanya aktif di private chat
    if not event.is_private:
        return

    me = await client.get_me()
    if event.sender_id != me.id:
        return

    # Ambil teks dari argumen
    input_text = (event.pattern_match.group(1) or "").strip()

    # Jika reply ke pesan lain
    if event.is_reply:
        reply = await event.get_reply_message()
        if reply:
            # Jika reply adalah media (foto, video, audio, dokumen), tolak
            if reply.media:
                return

            # Ambil isi text dari reply
            if reply.message:
                if input_text:
                    input_text = f"{input_text}\n\n{reply.message.strip()}"
                else:
                    input_text = reply.message.strip()

    if not input_text:
        await event.reply("❌ Harus ada teks atau reply pesan.")
        return

    # 🔄 pesan loading keren
    loading_msg = await event.reply("🤖✨ AI sedang berpikir keras...")

    try:
        # panggil API
        url = f"https://zelapioffciall.koyeb.app/ai/luminai?text={input_text}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=60) as resp:
                data = await resp.json()

        if data.get("status") and "result" in data:
            output = data["result"]
            
        else:
            output = "⚠ AI tidak memberikan respon."

        await loading_msg.edit(f"{output}", parse_mode="markdown")

    except Exception as e:
        await loading_msg.edit(f"⚠ Error AI")



async def simsimi_handler(event, client):
    

    # Ambil teks dari argumen
    input_text = (event.pattern_match.group(1) or "").strip()

    # Jika reply ke pesan lain
    if event.is_reply:
        reply = await event.get_reply_message()
        if reply:
            # Jika reply adalah media (foto, video, audio, dokumen), tolak
            if reply.media:
                return

            # Ambil isi text dari reply
            if reply.message:
                if input_text:
                    input_text = f"{input_text}\n\n{reply.message.strip()}"
                else:
                    input_text = reply.message.strip()

    if not input_text:
        await event.reply("❌ Harus ada teks atau reply pesan.")
        return

    # 🔄 pesan loading keren
    loading_msg = await event.reply("🤖✨ AI sedang berpikir keras...")

    try:
        # panggil API
        url = f"https://api.nekolabs.web.id/text.gen/simisimi?text={input_text}&lang=id"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=60) as resp:
                data = await resp.json()

        if data.get("success") and "result" in data:
            output = data["result"]
            
        else:
            output = "⚠ AI tidak memberikan respon."

        await loading_msg.edit(f"{output}", parse_mode="markdown")

    except Exception as e:
        await loading_msg.edit(f"⚠ Error AI")




# === FITUR: VN TO TEXT (Reply Only, SpeechRecognition) === 
import os
import speech_recognition as sr
from pydub import AudioSegment
import asyncio

async def vn_to_text_handler(event, client, log_channel=None, log_admin=None):
    if not event.is_private:
        return

    if not event.is_reply:
        await event.reply("❌ Harus reply ke VN/audio dengan `/stt`")
        return

    reply = await event.get_reply_message()
    if not reply.voice and not reply.audio:
        await event.reply("❌ Reply harus ke voice note/audio")
        return

    # 🔄 kirim pesan loading
    loading_msg = await event.reply("🎙 Sedang mengubah VN ke teks...")

    try:
        folder = "111VNtoText"
        os.makedirs(folder, exist_ok=True)
        file_path = await reply.download_media(file=folder)

        wav_path = file_path + ".wav"

        # Jalankan konversi audio di thread terpisah
        await asyncio.to_thread(AudioSegment.from_file(file_path).export, wav_path, format="wav")

        # Jalankan speech recognition di thread terpisah
        recognizer = sr.Recognizer()
        def recognize():
            with sr.AudioFile(wav_path) as source:
                audio_data = recognizer.record(source)
            try:
                return recognizer.recognize_google(audio_data, language="id-ID")
            except sr.UnknownValueError:
                return "Tidak bisa mengenali suara"
            except sr.RequestError as e:
                return f"Error API: {e}"

        text = await asyncio.to_thread(recognize)

        caption = (
            "🎙 **VN → Text**\n\n"
            f"📝 {text}"
        )
        await loading_msg.edit(caption, parse_mode="markdown")

        # Bersihkan file
        for f in [file_path, wav_path]:
            if f and os.path.exists(f):
                os.remove(f)

    except Exception as e:
        await loading_msg.edit(f"⚠ Error VN→Text", parse_mode="markdown")
        






# === FITUR: HILIH ===
async def hilih_handler(event, client):
    if not event.is_private:
        return
    me = await client.get_me()
    if event.sender_id != me.id:
        return

    # Ambil teks dari argumen atau reply
    input_text = event.pattern_match.group(2).strip() if event.pattern_match.group(2) else ''
    if event.is_reply and not input_text:
        reply = await event.get_reply_message()
        if reply and reply.message:
            input_text = reply.message.strip()

    if not input_text:
        await event.reply("❌ Harus ada teks atau reply pesan.")
        return

    target = event.pattern_match.group(1).lower() if event.pattern_match.group(1) else 'i'

    def replace_vowels(text, t):
        vokal = "aiueo"
        res = []
        for ch in text:
            if ch.lower() in vokal:
                res.append(t.upper() if ch.isupper() else t)
            else:
                res.append(ch)
        return "".join(res)

    output = replace_vowels(input_text, target)
    await event.reply(output)



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
            f"👤 **Pengirim:** [{sender_name}](tg://user?id={sender_id})\n"
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

# === FITUR: PING ===
async def ping_handler(event, client):
    if not event.is_private:
        return

    try:
        start = datetime.now()
        msg = await event.reply("⏳ Pinging...")
        end = datetime.now()

        ms = (end - start).microseconds // 1000
        uptime = datetime.now() - start_time_global
        uptime_str = str(uptime).split('.')[0]

        me = await client.get_me()
        akun_nama = me.first_name or "Akun"

        # Status emoji
        if ms < 30:
            status = "⚡️ Ultra Instan" 
        elif ms < 75:
            status = "💨 Super Cepat"
        elif ms < 150:
            status = "🟢 Cepat Stabil"
        elif ms < 250:
            status = "🟡 Cukup Lancar"
        elif ms < 400:
            status = "🟠 Agak Berat"
        elif ms < 700:
            status = "🔴 Sangat Lambat"
        else:
            status = "⚫️ Nyaris Down"

        text = (
            f"🏓 **PONG!** 🏓\n\n"
            f"⚡ Latency: `{ms} ms`\n"
            f"👤 **Akun:** {akun_nama}\n"
            f"⏱ **Uptime:** `{uptime_str}`\n"
            f"📡 **Status:** {status}\n"
            f"🕒 **Server:** {datetime.now(ZoneInfo('Asia/Jakarta')).strftime('%H:%M:%S || %d-%m-%Y')}"
        )

        await msg.edit(text)

    except Exception as e:
        await event.reply(f"⚠ Error /ping")


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

# === FITUR SAVE MEDIA ===
link_regex = re.compile(
    r'(?:https?://)?t\.me/(c/\d+|[a-zA-Z0-9_]+)/(\d+)(?:\?.*?)?',
    re.IGNORECASE
)

async def process_link(event, client, chat_part, msg_id, target_chat=None):
    if not event.is_private:
        return
    
    me = await client.get_me()
    if event.sender_id != me.id:
        return

    from telethon.errors import (
        RPCError,
        ChannelPrivateError,
        ChannelInvalidError,
        MessageIdInvalidError,
        UserNotParticipantError
    )

    try:
        # Proses chat ID
        if chat_part.startswith("c/"):
            internal_id = chat_part[2:]
            chat_id = int(f"-100{internal_id}")

            try:
                await client.get_permissions(chat_id, 'me')
            except:
                await event.reply(f"🚫 Ubot belum join channel `{chat_part}`.")
                return

        else:
            try:
                entity = await client.get_entity(chat_part)
                chat_id = entity.id
            except:
                await event.reply(f"❌ Channel/grup `{chat_part}` tidak ditemukan.")
                return

        message = await client.get_messages(chat_id, ids=msg_id)
        if not message:
            await event.reply(f"❌ Pesan {msg_id} tidak ditemukan.")
            return

        send_to = target_chat or event.chat_id  # Tentukan chat target atau chat tempat command digunakan
        
        # === PATCH: cek kalau media adalah sticker ===
        if message.media and message.sticker:
            await client.send_file(
                send_to,
                message.media,
                force_document=False  # penting agar tetap sticker (termasuk .tgs animasi)
            )
            return  # selesai, jangan lanjut ke grouped_id

        grouped_id = message.grouped_id
        if grouped_id:
            all_msgs = await client.get_messages(chat_id, limit=200)
            same_group = [m for m in all_msgs if m.grouped_id == grouped_id]
            same_group.sort(key=lambda m: m.id)

            files = []
            first_caption = None
            first_buttons = None

            for m in same_group:
                if first_caption is None and (m.message or m.raw_text):
                    first_caption = m.message or m.raw_text

                if first_buttons is None:
                    first_buttons = getattr(m, "buttons", None)

                if m.media:
                    fpath = await client.download_media(m.media)
                    files.append(fpath)
                else:
                    if m.message:
                        await client.send_message(send_to, m.message)

            if files:
                await client.send_file(
                    send_to,
                    files,
                    caption=first_caption or "",
                    buttons=first_buttons,
                    link_preview=False
                )
                for f in files:
                    try:
                        os.remove(f)
                    except:
                        pass

        else:
            buttons = getattr(message, "buttons", None)
            text = message.message or ""

            if message.media:
                fpath = await client.download_media(message.media)
                await client.send_file(
                    send_to,
                    fpath,
                    caption=text,
                    buttons=buttons,
                    link_preview=False
                )
                try:
                    os.remove(fpath)
                except:
                    pass
            else:
                await client.send_message(send_to, text, buttons=buttons)

    except Exception as e:
        await event.reply(f"🚨 Error")


async def handle_save_command(event, client):
    if not event.is_private:
        return
    
    me = await client.get_me()
    if event.sender_id != me.id:
        return
    
    input_text = event.pattern_match.group(2).strip() if event.pattern_match.group(2) else ''
    reply = await event.get_reply_message() if event.is_reply else None

    target_chat = event.chat_id  # Default: chat tempat command digunakan
    links_part = input_text

    # === Cek input yang hanya chat target ===
    if input_text and (re.match(r'^@?[a-zA-Z0-9_]+$', input_text) or re.match(r'^-?\d+$', input_text)):
        target_chat_raw = input_text
        target_chat = int(target_chat_raw) if target_chat_raw.lstrip("-").isdigit() else target_chat_raw
        
        # Ambil link dari reply, bukan dari input_text
        if reply and reply.message:
            links_part = reply.message.strip()
        else:
            await event.reply("❌ Harus reply pesan berisi link kalau cuma kasih target chat.")
            return

    # === Kalau input kosong tapi ada reply ===
    if not links_part and reply and reply.message:
        links_part = reply.message.strip()

    # === Ambil semua link ===
    matches = link_regex.findall(links_part)
    if not matches:
        await event.reply("❌ Tidak ada link valid.")
        return

    loading = await event.reply(f"⏳ Memproses {len(matches)} link...")

    for chat_part, msg_id in matches:
        # Cek apakah ada target chat, jika ada, kirim ke sana
        if target_chat and chat_part and msg_id:
            await process_link(event, client, chat_part, int(msg_id), target_chat)
        else:
            await process_link(event, client, chat_part, int(msg_id), target_chat)

    try:
        await loading.delete()
    except:
        pass
        
# === FITUR: WHOIS ===
async def whois_handler(event, client):
    if not event.is_private:
        return
      
    me = await client.get_me()

    if not event.is_reply:
        await event.reply("❌ Reply pesan user yang ingin kamu cek.")
        return

    reply = await event.get_reply_message()
    user = await client.get_entity(reply.sender_id)

    try:
        full = await client(GetFullUserRequest(user.id))
        bio = full.full_user.about or "-"
    except Exception as e:
        bio = f"⚠ Tidak bisa ambil bio"

    # Informasi dasar
    if user.id == me.id:
        # Jika yang dicek adalah akun sendiri (bot), kosongkan nomor
        phone = "-" 
    else:
        # Jika orang lain, tampilkan nomor sesuai kode asli
        phone = getattr(user, "phone", None)
        phone = f"+{phone}" if phone and not phone.startswith("+") else (phone or "-")
    #
    dc_id = getattr(user, "dc_id", "-")
    verified = "Ya" if getattr(user, "verified", False) else "Tidak"
    scam = "Ya" if getattr(user, "scam", False) else "Tidak"
    restricted = "Ya" if getattr(user, "restricted", False) else "Tidak"
    premium = "Ya" if getattr(user, "premium", False) else "Tidak"
    fullname = f"{user.first_name or '-'} {user.last_name or ''}".strip()
    username = f"@{user.username}" if user.username else "-"

    # Status / Last Seen
    status_text = "-"
    if hasattr(user, "status") and user.status:
        cname = user.status.__class__.__name__
        if cname == "UserStatusOffline":
            last_seen = user.status.was_online
            if last_seen:
                local_time = last_seen.astimezone(ZoneInfo("Asia/Jakarta"))
                status_text = local_time.strftime("%H:%M:%S || %d-%m-%Y")
        elif cname == "UserStatusOnline":
            status_text = "Sedang online"
        elif cname == "UserStatusRecently":
            status_text = "Baru saja online"
        elif cname == "UserStatusLastWeek":
            status_text = "Online minggu lalu"
        elif cname == "UserStatusLastMonth":
            status_text = "Online bulan lalu"
        else:
            status_text = cname.replace("UserStatus", "")

    # Grup bersama
    try:
        common = await client(GetCommonChatsRequest(user_id=user.id, max_id=0, limit=100))
        common_count = len(common.chats)
    except Exception as e:
        common_count = f"⚠ Error ambil grup bersama"

    # Format teks
    text = (
        f"👤 **WHOIS USER**\n\n"
        f"🆔 ID: `{user.id}`\n"
        f"👥 Nama: {fullname}\n"
        f"🔗 Username: {username}\n"
        f"📞 Phone: {phone}\n"
        f"📖 Bio: {bio}\n"
        f"🏛️ DC ID: {dc_id}\n"
        f"🤖 Bot: {'Ya' if user.bot else 'Tidak'}\n"
        f"🚷 Scam: {scam}\n"
        f"🚫 Restricted: {restricted}\n"
        f"✅ Verified: {verified}\n"
        f"⭐ Premium: {premium}\n"
        f"👁️ Last Seen: {status_text}\n"
        f"👀 Same Groups: {common_count}\n"
        f"🔗 Permanent Link: [Klik di sini](tg://user?id={user.id})\n"
    )


    # Ambil foto profil
    try:
        photos = await client.get_profile_photos(user.id, limit=10)
        files = []
        for p in photos:
            fpath = await client.download_media(p)
            files.append(fpath)

        if files:
            await client.send_file(
                event.chat_id,
                files,
                caption=text,
                link_preview=False
            )
            for f in files:
                try:
                    os.remove(f)
                except:
                    pass
        else:
            await event.reply(text, link_preview=False)
    except Exception as e:
        await event.reply(f"{text}\n\n⚠ Error ambil foto profil")


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
        
        try:
            await loading.delete()
        except:
            pass
        
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
        
    except Exception as e:
        try:
            await loading.delete()
        except:
            pass
        await event.reply(f"❌ Terjadi error: {str(e)}")





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

        # === PING ===
        if "ping" in acc["features"]:
            @client.on(events.NewMessage(pattern=r"^/ping$"))
            async def ping_event(event, c=client):
                await ping_handler(event, c)

        # === HEARTBEAT ===
        if "heartbeat" in acc["features"]:
            asyncio.create_task(heartbeat(client, acc["log_admin"], acc["log_channel"], akun_nama))

        # === SAVE MEDIA / COLONG MEDIA ===
        if "save_media" in acc["features"]:
            @client.on(events.NewMessage(pattern=r'^/(save|s)(?:\s+|$)(.*)'))
            async def save_event(event, c=client):
                await handle_save_command(event, c)
        
        # === DOWNLOADER ===
        if "downloader" in acc["features"]:
            @client.on(events.NewMessage(pattern=r'^/(d|download)(?:\s+|$)(.*)'))
            async def downloader_event(event, c=client):
                await handle_downloader(event, c)
        
        # === WHOIS (KHUSUS PRIVATE) ===
        if "whois" in acc["features"]:
            @client.on(events.NewMessage(pattern=r"^/whois$"))
            async def whois_event(event, c=client):
                await whois_handler(event, c)

        # === HILIH ===
        if "hilih" in acc["features"]:
            @client.on(events.NewMessage(pattern=r"^/h([aiueo])l\1h(?: (.+))?"))
            async def hilih_event(event, c=client):
                await hilih_handler(event, c)
                
        # === VN TO TEXT (Reply Only) ===
        if "vn_to_text" in acc["features"]:
            @client.on(events.NewMessage(pattern=r"^/stt$"))
            async def stt(event, c=client):
                await vn_to_text_handler(event, c)


        
                
            
        if "ai" in acc["features"]:
            @client.on(events.NewMessage(pattern=r'^/ai(?:\s+(.*))?$'))
            async def ai_command_handler(event, c=client):
                await ai_handler(event, c)

        if "ai" in acc["features"]:
            @client.on(events.NewMessage(pattern=r'^/ai2(?:\s+(.*))?$'))
            async def ai2_command_handler(event, c=client):
                await ai2_handler(event, c)

        if "ai" in acc["features"]:
            @client.on(events.NewMessage(pattern=r'^/ai3(?:\s+(.*))?$'))
            async def ai3_command_handler(event, c=client):
                await ai3_handler(event, c)

        if "ai" in acc["features"]:
            @client.on(events.NewMessage(pattern=r'^/ai4(?:\s+(.*))?$'))
            async def ai4_command_handler(event, c=client):
                await ai4_handler(event, c)

        if "ai" in acc["features"]:
            @client.on(events.NewMessage(pattern=r'^/ai5(?:\s+(.*))?$'))
            async def ai5_command_handler(event, c=client):
                await ai5_handler(event, c)

        if "ai" in acc["features"]:
            @client.on(events.NewMessage(pattern=r'^/simi(?:\s+(.*))?$'))
            async def simsimi_command_handler(event, c=client):
                await simsimi_handler(event, c)


        

        if "dongeng" in acc["features"]:
            @client.on(events.NewMessage(pattern=r"^/dongeng$"))
            async def dongeng_event(event, c=client):
                await dongeng_handler(event, c)

        if "brat" in acc["features"]:
            @client.on(events.NewMessage(pattern=r"^/brat(?:\s+.+)?$"))
            async def brat_event(event, c=client):
                await brat_handler(event, c)


        if "cecan" in acc["features"]:
            @client.on(events.NewMessage(pattern=r"^/cecan(?:\s+\w+)?$"))
            async def cecan_event(event, c=client):
                await cecan_handler(event, c)

        if "blurface" in acc["features"]:
            @client.on(events.NewMessage(pattern=r"^/blurface(?:\s+.+)?$"))
            async def blurface_event(event, c=client):
                await blurface_handler(event, c)

        if "hd" in acc["features"]:
            @client.on(events.NewMessage(pattern=r"^/hd(?:\s+.+)?$"))
            async def hd_event(event, c=client):
                await hd_handler(event, c)

        if "edit" in acc["features"]:
            @client.on(events.NewMessage(pattern=r"^/edit1"))
            async def edit1_event(event, c=client):
                await edit1_handler(event, c)
                
        if "edit" in acc["features"]:
            @client.on(events.NewMessage(pattern=r"^/edit2"))
            async def edit2_event(event, c=client):
                await edit2_handler(event, c)
            

        



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
