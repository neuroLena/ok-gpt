import os
import openai
import requests
from telegram import Update, Voice, MessageEntity
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import dotenv
import json
import logging

dotenv.load_dotenv()

TELEGRAM_API_TOKEN=os.environ["TELEGRAM_API_TOKEN"]
OPENAI_API_KEY=os.environ["CHATGPT_API_KEY"]
WHISPER_API_KEY=os.environ["WHISPER_API_KEY"]

# Set up logging
logging.basicConfig(filename="bot.log", level=logging.INFO, format="%(asctime)s - %(message)s")

# Set up OpenAI API
openai.api_key = OPENAI_API_KEY

def start(update: Update, context: CallbackContext):
    update.message.reply_text("Hello! Send me a voice message, and I'll transcribe it and send the result to ChatGPT.")

def process_voice_message(update: Update, context: CallbackContext):
    voice: Voice = update.message.voice
    file_id = voice.file_id
    user_id = update.message.from_user.id
    user_name = update.message.from_user.username or update.message.from_user.first_name

    # Download the voice message
    logging.info(f"User: {user_name} (ID: {user_id}) - Voice message received")
    voice_file = context.bot.get_file(file_id)
    voice_file.download(f"audio/voice_{user_id}.ogg")

    # Convert Ogg to WAV
    os.system(f"yes | ffmpeg -i audio/voice_{user_id}.ogg -acodec pcm_s16le -ac 1 -ar 16000 audio/voice_{user_id}.wav")

    # Transcribe the voice message using Whisper ASR
    with open(f"audio/voice_{user_id}.wav", "rb") as audio_file:
        response = openai.Audio.transcribe("whisper-1", audio_file)

    # response_json = response.json()
    # if response.status_code != 200:
    #     update.message.reply_text(f"Error transcribing voice message: {response_json['error']}")
    #     return

    #transcribed_text = response_json["choices"][0]["text"]

    # # Speech to text
    # os.system("./whisper.cpp/main -m whisper.cpp/models/ggml-large.bin -f audio/voice_{user_id}.wav -nt -l auto -pp -oj -of audio/voice_{user_id}")
    # with open("audio/voice_{user_id}.json", "r") as f:
    #     transcription_data = json.load(f)

    # transcribed_text = "\n".join([entry["text"].strip() for entry in transcription_data["transcription"]])
    
    transcribed_text = response["text"]
    logging.info(f"User: {user_name} (ID: {user_id}) - Transcribed text: {transcribed_text}")
    print(transcribed_text)

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
    logging.info(f"User: {user_name} (ID: {user_id}) - ChatGPT response: {assistant_reply}")
    print(assistant_reply)

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



