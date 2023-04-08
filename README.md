# OK, GPT
OK, GPT is a simple telegram bot to send voice messages to ChatGPT and get outputs. Requires your own API keys (and hence a paid subscription) to work

## Installation
### Set up Python environment
```
make env
source venv/bin/activate
```

### Set up API keys
The app requires some API keys to run. It is supposed to be stored in `.env` file in the project root which you should manually create. My file is not provided because of security reasons, but I put `template.env` as a template for the keys required.

OpenAI key is not used yet.

#### OpenAI API key
To get your Tinder API key, log in into Tinder from Chrome web browser. The key is here:
`Google Chrome -> burger menu top right corner -> More Tools -> Developer Tools -> Network -> find any profile request -> Headers -> x-auth-token`

Note it expires after a few days.

#### Create a new Telegram bot with BotFather
- Start a new conversation with the BotFather.
- Send /newbot to create a new Telegram bot.
- When asked, enter a name for the bot.
- Give the Telegram bot a unique username. ...
- Copy and save the Telegram bot's access token for later steps.

## Use
