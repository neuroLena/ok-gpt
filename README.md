<img src="https://github.com/dsvolk/ok-gpt/blob/master/images/userpic.png" width="300" height="300">

# OK, GPT
OK, GPT is a simple telegram bot to send voice messages to ChatGPT and get outputs. Requires your own OpenAI API key (and hence a paid subscription) to work.

## Installation
### Create a new Telegram bot with BotFather bot
- Start a new conversation with the BotFather.
- Send /newbot to create a new Telegram bot.
- When asked, enter a name for the bot.
- Give the Telegram bot a unique username. ...
- Copy and save the Telegram bot's access token for later steps.

### Get OpenAI API key
Set up your own OpenAI account. Visit [https://platform.openai.com/account/api-keys](https://platform.openai.com/account/api-keys) in your OpenAI account to create a new API key.

### Set up API keys for the bot
The bot requires some API keys to run. There are two ways of providing them:
- environment variables. Provide the env variables listed in `template.env`. This option is more convenient for a cloud installation.
- `.env` file in the project root. You should manually create it. I do not provide my own `.env` file because of security reasons, but I put `template.env` as a template for the keys required. This option is better suited for a local installation.

### Cloud installation
For most clouds, it should be sufficient to just push the git repo and let them build everything for you. This, for example, works for [Railway](https://railway.app/), [Heroku](https://www.heroku.com/), and others. The repo already has the Dockerfile and Makefile provided.

So all you need is to set up the API keys as described above.

### Local installation

#### Set up Python environment
```
make env
source venv/bin/activate
```

#### Run the bot
```
./venv/bin/python ./src/app.py
```

Use Ctrl+c to stop the bot.

## Enjoy!
