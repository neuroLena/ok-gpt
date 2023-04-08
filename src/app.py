import os
import openai
import requests
from telegram import Update, Voice, MessageEntity
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import dotenv

dotenv.load_dotenv()

TELEGRAM_API_TOKEN=os.environ["TELEGRAM_API_TOKEN"]
WHISPER_API_KEY=os.environ["WHISPER_API_KEY"]
OPENAI_API_KEY=os.environ["CHATGPT_API_KEY"]

# Set up OpenAI API
openai.api_key = OPENAI_API_KEY

def start(update: Update, context: CallbackContext):
    update.message.reply_text("Hello! Send me a voice message, and I'll transcribe it and send the result to ChatGPT.")

def process_voice_message(update: Update, context: CallbackContext):
    voice: Voice = update.message.voice
    file_id = voice.file_id

    # Download the voice message
    voice_file = context.bot.get_file(file_id)
    voice_file.download("audio/voice.ogg")

    # Convert Ogg to WAV
    os.system("ffmpeg -i audio/voice.ogg -acodec pcm_s16le -ac 1 -ar 16000 audio/voice.wav")

    # Transcribe the voice message using Whisper ASR
    with open("audio/voice.wav", "rb") as audio_file:
        response = requests.post(
            "https://api.openai.com/v1/engines/whisper/asr",
            headers={"Authorization": f"Bearer {WHISPER_API_KEY}"},
            files={"file": audio_file}
        )

    response_json = response.json()
    if response.status_code != 200:
        update.message.reply_text(f"Error transcribing voice message: {response_json['error']}")
        return

    transcribed_text = response_json["choices"][0]["text"]
    print(transcribed_text)

    # Send the transcribed text to ChatGPT
    chatgpt_response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=transcribed_text,
        max_tokens=50,
        n=1,
        stop=None,
        temperature=0.5,
    )

    generated_text = chatgpt_response.choices[0].text.strip()
    update.message.reply_text(generated_text)

def main():
    updater = Updater(TELEGRAM_API_TOKEN)

    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.voice, process_voice_message))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
