import os
import sys
import openai
import requests
from telegram import Update, Voice, MessageEntity
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import dotenv
import json
import logging
from datadog_api_client import ApiClient, Configuration
from datadog_api_client.v2.api.logs_api import LogsApi
from datadog_api_client.v2.model.content_encoding import ContentEncoding
from datadog_api_client.v2.model.http_log import HTTPLog
from datadog_api_client.v2.model.http_log_item import HTTPLogItem

dotenv.load_dotenv()

TELEGRAM_API_TOKEN=os.environ["TELEGRAM_API_TOKEN"]
OPENAI_API_KEY=os.environ["OPENAI_API_KEY"]

# Set up logging
file_handler = logging.FileHandler(filename="logs/bot.log", mode="a")
stdout_handler = logging.StreamHandler(stream=sys.stdout)
handlers = [file_handler, stdout_handler]
logging.basicConfig(
    level=logging.INFO, 
    format="[%(asctime)s] %(message)s",
    handlers=handlers,
)

# Set up remote logging with DataDog
def log_to_datadog(message: str) -> str:
    body = HTTPLog(
        [
            HTTPLogItem(
                ddsource="nginx",
                ddtags="env:prod,version:0.1.1",
                hostname="railway-okgpt-prod",
                message=message,
                service="bot",
            ),
        ]
    )

    configuration = Configuration()
    with ApiClient(configuration) as api_client:
        api_instance = LogsApi(api_client)
        response = api_instance.submit_log(content_encoding=ContentEncoding.DEFLATE, body=body)
        print(response)

    return response

# Set up OpenAI API
openai.api_key = OPENAI_API_KEY

def start(update: Update, context: CallbackContext):
    update.message.reply_text("Hello! Send me a voice message, and I'll transcribe it and send the result to ChatGPT.\n\nNote it may take up to a minute to get a response, because ChatGPT itself is pretty slow.")

def process_voice_message(update: Update, context: CallbackContext):
    voice: Voice = update.message.voice
    file_id = voice.file_id
    user_id = update.message.from_user.id
    user_name = update.message.from_user.username or update.message.from_user.first_name

    # Download the voice message
    logging.info(f"User: {user_name} (ID: {user_id}) - Voice message received")
    log_to_datadog(f"User: {user_name} (ID: {user_id}) - Voice message received")
    voice_file = context.bot.get_file(file_id)
    voice_file.download(f"audio/voice_{user_id}.ogg")

    # Convert Ogg to WAV
    os.system(f"yes | ffmpeg -i audio/voice_{user_id}.ogg -acodec pcm_s16le -ac 1 -ar 16000 audio/voice_{user_id}.wav")

    # Transcribe the voice message using Whisper ASR
    with open(f"audio/voice_{user_id}.wav", "rb") as audio_file:
        response = openai.Audio.transcribe("whisper-1", audio_file)
    
    transcribed_text = response["text"]
    logging.info(f"User: {user_name} (ID: {user_id}) - Transcribed text:\n{transcribed_text}")
    log_to_datadog(f"User: {user_name} (ID: {user_id}) - Transcribed text:\n{transcribed_text}")

    # Send the transcribed text to ChatGPT
    chatgpt_response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": transcribed_text},
            ],
        max_tokens=1000,
        n=1,
        stop=None,
        temperature=0.5,
    )
        
    assistant_reply = chatgpt_response.choices[0].message["content"]
    logging.info(f"User: {user_name} (ID: {user_id}) - ChatGPT response:\n{assistant_reply}")
    log_to_datadog(f"User: {user_name} (ID: {user_id}) - ChatGPT response:\n{assistant_reply}")

    update.message.reply_text(assistant_reply)

def main():
    updater = Updater(TELEGRAM_API_TOKEN)

    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.voice, process_voice_message))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()