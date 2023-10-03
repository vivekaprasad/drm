import os
import subprocess
from pyrogram import Client, filters
import xml.etree.ElementTree as ET 
import json
import asyncio
import logging
import aiohttp
import time
import requests
from moviepy.editor import VideoFileClip
from PIL import Image
import numpy as np
# Initialize your Pyrogram bot
# Initialize your Pyrogram bot
api_id = '17810412'
api_hash = 'bd9cd7df354fb74e2f9ec88f6ee4de48'
bot_token = '6089614727:AAFZCXJ0PYtDn9f56QvfVpWx0n23JAsM54I'
allowed_chats = [5441346943,-1001562024039,6204387702,5877917640,-1001862375832] 
log_channel_id = -1001767473604


app = Client('my_bot', api_id=api_id, api_hash=api_hash, bot_token=bot_token)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize your download queue
download_queue = asyncio.Queue()

# Your other functions and handlers here
def is_allowed_chat(chat_id):
    return chat_id in allowed_chats

@app.on_message(filters.command('ping3'))
async def start_command(client, message):
    await message.reply("Hello! I'm Science Edu Drm Downloader Bot.\n\n Powered By @BioVideoFullSyllubus")


@app.on_message(filters.command('vimeo', prefixes='/') & filters.group)
async def handle_text_message(client, message):
        if is_allowed_chat(message.chat.id):
            command_args = message.text.split(' | ')
            if len(command_args) >= 4 and command_args[0] == "/vimeo":
                tex = command_args[0]
                mpd_url = command_args[1]
                select = command_args[2]
                custom_name = ' '.join(command_args[3:]) if len(command_args) > 3 else "default_custom_name"
                if is_allowed_chat(message.chat.id):
                    text = message.text
                    tex = None
                    mpd_url = None
                    select = None
                    custom_name = None
                    if "|" in text:
                        tex, mpd_url,select,*name_parts = text.split(" | ")
                        custom_name = ' '.join(name_parts) if name_parts else "default_custom_name"
                        await download_worker2(client, message, mpd_url,select,custom_name)
                else:
                    await message.reply("Please provide a m3u8 URL,  and a custom name separated by '|'.")
            else:
                await message.reply("Please provide a m3u8 URL,  and a custom name separated by '|'.")
        else: 
            await message.reply("You are not allowed. Please contact my owner @ScienceEduAdmin")
async def download_worker2(client, message, mpd_url,select,custom_name):
    try:
        # Send a status message indicating that the bot is downloading the video
        status_message = await message.reply("Please Wait \n\nDownloading video with {select} quality ...\n\n Powered By @BioVideoFullSyllubus")
        # Your video download and processing logic here...
        

                # Example code for downloading a video using subprocess (modify as needed)
        subprocess_args = [
                    './N_m3u8DL-RE',mpd_url,
                    '--save-name', custom_name,
                    '-sv', select,
                    '-sa', 'best',
                    '--mux-after-done', 'mkv',
                    '--thread-count', '100'
                ]

        subprocess.run(subprocess_args)

                # Check if the final video file exists
        final_video_path = f"{custom_name}.mkv"
        if os.path.exists(final_video_path):
                    video_clip = VideoFileClip(final_video_path)
                    video_duration = int(video_clip.duration)
                    # Send a status message indicating that the bot is uploading the final video
                    await message.reply(f"Uploading video: {custom_name}\n\n Powered By @BioVideoFullSyllubus")

                    # Send the decrypted and merged video to the user with the custom name as caption
                    await send_video_with_duration(
                              message.chat.id,
                              final_video_path,
                              video_duration,  # Replace with the actual duration
                              custom_name,
        )

                    # Cleanup: Delete temporary files
                    os.remove(final_video_path)
        
        else:
                await message.reply("Try Another Link")
    except Exception as e:
        await message.reply(f"An error occurred: {str(e)}")

async def send_video_with_duration2(chat_id, video_path, duration, caption):
    try:
        await app.send_video(
            chat_id,
            video=video_path,
            duration=duration,  # Provide the duration in seconds
            caption=caption,
        )
    except Exception as e:
        logger.error(f"An error occurred while sending the video: {str(e)}")

# Define a function to process the download queue
async def process_download_queue():
    while True:
        message, mpd_url, select, custom_name = await download_queue.get()
        await download_worker2(message, mpd_url, select, custom_name)
        download_queue.task_done()

@app.on_message(filters.command('drm', prefixes='/') & filters.group)
async def handle_text_message(client, message):
    if is_allowed_chat(message.chat.id):
        # Remove "/drm" from the command string
        command_args = message.text.split(' | ')
        if len(command_args) >= 3 and command_args[0] == "/drm":
            tex = command_args[0]
            mpd_url = command_args[1]
            xdrm = command_args[2]
            
            # Join any remaining parts of the message after the third '|'
            custom_name = ' '.join(command_args[3:]) if len(command_args) > 3 else "default_custom_name"

            if is_allowed_chat(message.chat.id):
                text = message.text
                tex = None
                mpd_url = None
                xdrm = None
                custom_name = None
                if "|" in text:
                    tex, mpd_url, xdrm, *name_parts = text.split(" | ")

                    # Process the video download in a separate coroutine
                    custom_name = ' '.join(name_parts) if name_parts else "default_custom_name"
                    await download_worker(client, message, mpd_url, xdrm, custom_name)
            else:
                await message.reply("Please provide an MPD URL, headers, and a custom name separated by '|'.")
        else:
            await message.reply("Please provide an MPD URL, headers, and a custom name separated by '|'.")
    else:
        await message.reply("You are not allowed. Please contact my owner @ScienceEduAdmin")

async def download_worker(client, message, mpd_url, xdrm, custom_name):
    try:
        # Send a status message indicating that the bot is downloading the video
        status_message = await message.reply("Please Wait \n\nDownloading video...\n\n Powered By @BioVideoFullSyllubus")

        # Your video download and processing logic here...
        async with aiohttp.ClientSession() as session:
            mpd_response = await session.get(mpd_url)
            if mpd_response.status == 200:
                mpd_content = await mpd_response.text()
                # Extract PSSH from MPD content using the ElementTree module
                pssh_data = extract_pssh_from_mpd(mpd_content)
                xdrm='''{"X-Axdrm-Message":"'''+xdrm+'''"}'''

                # Integrate the simplified API request using the requests library
                api_url = "https://keysdb.net/api"
                license_url = "https://3bc812e0.drm-widevine-licensing.axprod.net/AcquireLicense"
                headers = {
                    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (Ktesttemp, like Gecko) Chrome/90.0.4430.85 Safari/537.36",
                    "Content-Type": "application/json",
                    "X-API-Key": 'd1fb82ba6ba9e321e48aae4eef62dc606baff4f1e98f206cbcb9de68ebb21ba1',
                }
                payload = {
                    "license_url": license_url,
                    "pssh": pssh_data,
                    "headers": xdrm,
                }

                # Make the API request
                response = requests.post(api_url, headers=headers, json=payload)
                
                try:
                        response_data = response.json()  # Parse JSON response
                        keys = response_data.get("keys")  # Use get() to safely retrieve the "keys" value
                        if keys and isinstance(keys, list):
                            if keys:
                                # Extract the "key" value from the first item in the list (assuming there's only one)
                                key_value = keys[0].get("key")
                            else:
                                logger.error("No 'keys' found. Try Another Link")
                        else:
                            logger.error("No 'keys' found. Try Another Link")
                except json.JSONDecodeError:
                        logger.error("JSON data is not valid. Try Another Link")
                

                # Example code for downloading a video using subprocess (modify as needed)
                subprocess_args = [
                    './N_m3u8DL-RE',
                    mpd_url,
                    '--save-name', custom_name,
                    '-sv', 'best',
                    '-sa', 'best',
                    '--mux-after-done', 'mkv',
                    '--key', key_value if 'key_value' in locals() else '',  # Check if key_value is defined
                    '--write-meta-json', 'True',
                    '--thread-count', '100'
                ]

                subprocess.run(subprocess_args)

                # Check if the final video file exists
                final_video_path = f"{custom_name}.mkv"
                if os.path.exists(final_video_path):
                    video_clip = VideoFileClip(final_video_path)
                    video_duration = int(video_clip.duration)
                    # Send a status message indicating that the bot is uploading the final video
                    await message.reply(f"Uploading video: {custom_name}\n\n Powered By @BioVideoFullSyllubus")

                    # Send the decrypted and merged video to the user with the custom name as caption
                    await send_video_with_duration(
                              message.chat.id,
                              final_video_path,
                              video_duration,  # Replace with the actual duration
                              custom_name,
        )

                    # Cleanup: Delete temporary files
                    os.remove(final_video_path)
                else:
                    await message.reply("Error during video processing.")
            else:
                await message.reply("Try Another Link")
    except Exception as e:
        await message.reply(f"An error occurred: {str(e)}")


# Define a function to process the download queue
async def process_download_queue():
    while True:
        message, mpd_url, custom_name = await download_queue.get()
        await download_worker(message, mpd_url, custom_name)
        download_queue.task_done()

async def send_video_with_duration(chat_id, video_path, duration, caption):
    try:
        # Generate a thumbnail from the video (e.g., taking a screenshot at a specific time)
        thumbnail_path = generate_thumbnail(video_path)

        # Define the width and height for the video message
        width = 320  # Adjust this as needed
        height = 180# Adjust this as needed

        # Send the video with the generated thumbnail, width, height, and caption
        await app.send_video(
            chat_id,
            video=video_path,
            thumb=thumbnail_path,
            duration=duration,  # Provide the duration in seconds
            width=width,
            height=height,
            caption=caption,
        )

        # Cleanup: Delete the generated thumbnail
        if os.path.exists(thumbnail_path):
            os.remove(thumbnail_path)
    except Exception as e:
        logger.error(f"An error occurred while sending the video: {str(e)}")


def generate_thumbnail(video_path, time_offset=5):
    thumbnail_path = video_path.replace(".mkv", ".jpg")  # Change the extension if necessary
    try:
        video_clip = VideoFileClip(video_path)
        thumbnail_frame = video_clip.get_frame(time_offset)  # Capture a frame at the specified time

        # Convert the NumPy array to a Pillow image
        thumbnail_image = Image.fromarray(np.uint8(thumbnail_frame))

        # Save the image as a JPEG thumbnail
        thumbnail_image.save(thumbnail_path, format="JPEG")

        return thumbnail_path
    except Exception as e:
        logger.error(f"Error generating thumbnail: {str(e)}")
        return None

# Your log_to_channel function and other handlers here...
def extract_pssh_from_mpd(mpd_content):
    ns = {"mpd": "urn:mpeg:dash:schema:mpd:2011", "cenc": "urn:mpeg:cenc:2013"}
    root = ET.fromstring(mpd_content)
    content_protection_elements = root.findall(".//mpd:ContentProtection", namespaces=ns)

    for content_protection in content_protection_elements:
        pssh_element = content_protection.find("cenc:pssh", namespaces=ns)
        if pssh_element is not None:
            pssh_data = pssh_element.text.strip()
            return pssh_data

    return None


# Start the Pyrogram bot
print("Bot Started")
if __name__ == "__main__":
    app.run()

