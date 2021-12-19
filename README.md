# TradingView Binance bot

[![GPLv3 License](https://img.shields.io/badge/%20License-GPL%20v3-yellow?style=flat-square&labelColor=black)](https://opensource.org/licenses/)
[![Python](https://img.shields.io/static/v1?label=&message=Python&color=blue&style=flat-square&logo=python&logoColor=white&logoWidth=17&labelColor=&link=)](https://www.python.org/)
[![Heroku](https://img.shields.io/static/v1?label=&message=Heroku&color=42c5f5&style=flat-square&logo=heroku&logoColor=42c5f5&logoWidth=17&labelColor=black&link=)](https://www.heroku.com/)

A trading bot that follows TradingView [alerts](https://www.tradingview.com/support/solutions/43000520149-about-tradingview-alerts/)
 executing them on you Binance account and providing you constant updates through a Telegram bot.

### Local Setup
Before pushing this to heroku, let's test this in a local environment:

1. Clone this repo.
2. Activate your python venv and run `pip install -r requirements.txt` to install all the necessary dependencies.
3. Setup your API keys in config.py:

    - WEBHOOK_PASSPHRASE is the passphrase that you want to use for your payload.
    - API_KEY and API_SECRET are your Binance API keys, fetch them [here](https://www.binance.com/en/support/faq/360002502072).
    - USER_ID and TOKEN are for your Telegram bot, fetch the TOKEN by creating a new bot with [@BotFather](https://t.me/BotFather) and fetch the USER_ID by sending a message to [@RawDataBot](https://t.me/RawDataBot).
4. Run the app with `python app.py`.
5. Test the `/webhook` endpoint with Insomnia or similar, passing it a
sample request with [this](webhook.txt) format.

### Production Setup

1. Head over to [heroku](https://www.heroku.com) and create an account.
2. Create a new python app and push your local code into it,
simply following the heroku instructions, then open it annotating its URL.
3. Create a new alert on TradingView as explained [here](https://www.tradingview.com/support/solutions/43000595315-how-to-set-up-alerts/).
4. Insert `your-heroku-URL/webhook` as the webhook URL and your payload as the message as explained [here](https://www.tradingview.com/?solution=43000529348).
5. Sit back and relax watching your Telegram bot notifications.

#### Info

This bot supports a "double_order" mode which consists in scalping the UP/DOWN leveraged indexes on Binance: selling a position will result in buying the opposite position, if you want to get the money out of this cycle you have to do it by selling manually.

#### Notes

Use at your own risk, this involves your Binance account.
