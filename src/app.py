import os
import sys
import openai
import requests
from telegram import Update, Voice, MessageEntity, ForceReply
from telegram.ext import Application, ContextTypes, CallbackContext, CommandHandler, MessageHandler, filters, Defaults
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
handlers = [file_handler, stdout_handler]

# Add Datadog handler if DD_API_KEY and DD_SITE are provided
if os.environ.get("DD_API_KEY") and os.environ.get("DD_SITE"):
    datadog_handler = DatadogHandler(Configuration())
    formatter = logging.Formatter('%(message)s')
    datadog_handler.setFormatter(formatter)
    handlers.append(datadog_handler)

logging.basicConfig(
    level=logging.INFO, 
    format="[%(asctime)s] %(message)s",
    handlers=handlers,
)

# Set up OpenAI API
openai.api_key = OPENAI_API_KEY


async def start(update: Update, context: CallbackContext):
    start_text = """🤖 Hello\! Send me a *voice message*, and I'll transcribe it and send the result to *ChatGPT*\. Under the hood, I am using OpenAI's *[Whisper ASR](https://openai.com/research/whisper)* for Speech\-To\-Text and the famous *[GPT\-4](https://openai.com/product/gpt-4)*\.

❗️ I am only aware of the information up to year *2021*, so I may have difficulties answering questions about later times\.
❗️ It may take up to a minute to get a response from me, because GPT itself is pretty slow\. Please be patient\.
❗️ So far, I do not maintain the context of the discussion, so every new message starts a new context for me\.
👀 But you can gently ask @denisvolk, and maybe he soon implements memory for me\!

🆕 UPD 2023\-04\-12: Now you can send me text messages, too\!"""

    await update.message.reply_text(start_text, parse_mode="MarkdownV2", disable_web_page_preview=True)


async def start(update: Update, context: CallbackContext):
    start_text = """🤖 Hello\! Send me a *voice message*, and I'll transcribe it and send the result to *ChatGPT*\. Under the hood, I am using OpenAI's *[Whisper ASR](https://openai.com/research/whisper)* for Speech\-To\-Text and the famous *[GPT\-4](https://openai.com/product/gpt-4)*\.

❗️ I am only aware of the information up to year *2021*, so I may have difficulties answering questions about later times\.
❗️ It may take up to a minute to get a response from me, because GPT itself is pretty slow\. Please be patient\.
❗️ So far, I do not maintain the context of the discussion, so every new message starts a new context for me\.
👀 But you can gently ask @denisvolk, and maybe he soon implements memory for me\!

🆕 UPD 2023\-04\-12: Now you can send me text messages, too\!"""

    await update.message.reply_text(start_text, parse_mode="MarkdownV2", disable_web_page_preview=True)


async def not_implemented_command(update: Update, context: CallbackContext):
    await update.message.reply_text("This command is not implemented yet. Stay tuned for updates!")


async def process_voice_message(update: Update, context: CallbackContext):
    voice: Voice = update.message.voice
    file_id = voice.file_id
    user_id = update.message.from_user.id
    user_name = update.message.from_user.username or update.message.from_user.first_name

    # Download the voice message
    logging.info(f"User: {user_name} (ID: {user_id}) - Voice message received")

    voice_file = await update.message.effective_attachment.get_file()
    await voice_file.download_to_drive(f"audio/voice_{user_id}.ogg")

    # Convert Ogg to WAV
    os.system(f"yes | ffmpeg -i audio/voice_{user_id}.ogg -acodec pcm_s16le -ac 1 -ar 16000 audio/voice_{user_id}.wav")

    # Transcribe the voice message using Whisper ASR
    with open(f"audio/voice_{user_id}.wav", "rb") as audio_file:
        response = openai.Audio.transcribe("whisper-1", audio_file)
    
    transcribed_text = response["text"]
    logging.info(f"User: {user_name} (ID: {user_id}) - Transcribed text:\n{transcribed_text}")

    # Send the transcribed text to ChatGPT
    try:
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

    except openai.error.APIError as e:
        logging.error(f"User: {user_name} (ID: {user_id}) - OpenAI API error:\n{e}")
        await update.message.reply_text("Sorry, OpenAI servers are irresponsive at the moment. Please try again in a few minutes (you can just forward me the same message).")


async def process_text_message(update: Update, context: CallbackContext):
    text = update.message.text
    user_id = update.message.from_user.id
    user_name = update.message.from_user.username or update.message.from_user.first_name

    logging.info(f"User: {user_name} (ID: {user_id}) - Text message received:\n{text}")

    # Send the text to ChatGPT
    chatgpt_response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": text},
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
                   # .defaults(Defaults())
                   .build()
    )

    # On different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", not_implemented_command))
    application.add_handler(CommandHandler("examples", not_implemented_command))
    application.add_handler(CommandHandler("options", not_implemented_command))

    # On non command i.e message - echo the message on Telegram
    application.add_handler(MessageHandler(filters.VOICE & ~filters.COMMAND, process_voice_message))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, process_text_message))

    # Run the bot until the user presses Ctrl-C
    application.run_polling()


if __name__ == "__main__":
    main()