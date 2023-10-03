import os
import subprocess
import logging
from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv


# Initialize your FastAPI app
app = FastAPI()
load_dotenv()
bot_token = os.getenv('BOT_TOKEN')
# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Your other functions and handlers here
def is_allowed_chat(chat_id):
    return chat_id in allowed_chats

@app.post("/vimeo")
async def vimeo_command(mpd_url: str, select: str, custom_name: str):
    try:
        # Check if the chat ID is allowed
        if not is_allowed_chat(message.chat.id):
            raise HTTPException(status_code=403, detail="You are not allowed.")
        
        # Send a status message indicating that the bot is downloading the video
        status_message = f"Please Wait\n\nDownloading video with {select} quality ...\n\nPowered By @BioVideoFullSyllubus"
        
        # Your video download and processing logic here...
        
        # Example code for downloading a video using subprocess (modify as needed)
        subprocess_args = [
            './N_m3u8DL-RE', mpd_url,
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
            # Video duration calculation
            # Replace this with actual duration calculation
            video_duration = 0
            
            # Send a status message indicating that the bot is uploading the final video
            response_message = f"Uploading video: {custom_name}\n\nPowered By @BioVideoFullSyllubus"
            
            # Cleanup: Delete temporary files
            os.remove(final_video_path)
            
            return {"message": response_message, "duration": video_duration}
        else:
            raise HTTPException(status_code=400, detail="Video download failed. Try another link.")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
