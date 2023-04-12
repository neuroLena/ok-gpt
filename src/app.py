import os
import sys
import openai
import requests
from telegram import Update, Voice, MessageEntity, ForceReply
from telegram.ext import Application, ContextTypes, CallbackContext, CommandHandler, MessageHandler, filters
import dotenv
import json
import logging
from datadog_api_client import Configuration
from datadog import DatadogHandler

dotenv.load_dotenv()

TELEGRAM_API_TOKEN=os.environ["TELEGRAM_API_TOKEN"]
OPENAI_API_KEY=os.environ["OPENAI_API_KEY"]

# Set up logging
file_handler = logging.FileHandler(filename="logs/bot.log", mode="a")
stdout_handler = logging.StreamHandler(stream=sys.stdout)
datadog_handler = DatadogHandler(Configuration())
formatter = logging.Formatter('%(message)s')
datadog_handler.setFormatter(formatter)

handlers = [file_handler, stdout_handler, datadog_handler]
logging.basicConfig(
    level=logging.INFO, 
    format="[%(asctime)s] %(message)s",
    handlers=handlers,
)

# Set up OpenAI API
openai.api_key = OPENAI_API_KEY


def start(update: Update, context: CallbackContext):
    update.message.reply_text("Hello! Send me a voice message, and I'll transcribe it and send the result to ChatGPT.\n\nNote it may take up to a minute to get a response, because ChatGPT itself is pretty slow.")


async def process_voice_message(update: Update, context: CallbackContext):
    voice: Voice = update.message.voice
    file_id = voice.file_id
    user_id = update.message.from_user.id
    user_name = update.message.from_user.username or update.message.from_user.first_name

    # Download the voice message
    logging.info(f"User: {user_name} (ID: {user_id}) - Voice message received")

    voice_file = await update.message.effective_attachment.get_file()
    await voice_file.download_to_drive(f"audio/voice_{user_id}.ogg")

    # await context.bot.get_file(file_id).download(f"audio/voice_{user_id}.ogg")
    # voice_file = await context.bot.get_file(file_id)
    # await voice_file.download(f"audio/voice_{user_id}.ogg")

    # Convert Ogg to WAV
    os.system(f"yes | ffmpeg -i audio/voice_{user_id}.ogg -acodec pcm_s16le -ac 1 -ar 16000 audio/voice_{user_id}.wav")

    # Transcribe the voice message using Whisper ASR
    with open(f"audio/voice_{user_id}.wav", "rb") as audio_file:
        response = openai.Audio.transcribe("whisper-1", audio_file)
    
    transcribed_text = response["text"]
    logging.info(f"User: {user_name} (ID: {user_id}) - Transcribed text:\n{transcribed_text}")

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

    await update.message.reply_text(assistant_reply)


def main() -> None:
    # Create the Application and pass it your bot's token.
    application = (Application.builder()
                   .token(TELEGRAM_API_TOKEN)
                   .read_timeout(300)
                   .write_timeout(300)
                   .build()
    )

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    # application.add_handler(CommandHandler("help", help_command))

    # on non command i.e message - echo the message on Telegram
    application.add_handler(MessageHandler(filters.VOICE & ~filters.COMMAND, process_voice_message))

    # Run the bot until the user presses Ctrl-C
    application.run_polling()


if __name__ == "__main__":
    main()