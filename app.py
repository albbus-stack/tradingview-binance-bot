import json
import time

from telepot.api import download
import config
from flask import Flask, request, render_template
from binance.client import Client
from binance.enums import *
import math
import cryptocompare
import telepot


# Function that truncates a [number] to a certain amount of [digits]
def truncate(number, digits) -> float:
    stepper = 10.0 ** digits
    return math.trunc(stepper * number) / stepper


# Executes an order, by default a market one
def order(side, quantity, symbol, order_type=ORDER_TYPE_MARKET):
    try:
        order = client.create_order(
            symbol=symbol, side=side, type=order_type, quantity=quantity)
    except Exception as e:
        err = "{}".format(e)
        bot.sendMessage(
            config.USER_ID, f"⛔ *{side}* order on *{symbol}* failed\n\n\
                *error*: {err}", parse_mode='Markdown')
        return False

    return order


# Flask setup
app = Flask(__name__)

# Binance API setup
client = Client(config.API_KEY, config.API_SECRET, tld='com')

# Telepot telegram API setup
bot = telepot.Bot(config.TOKEN)


# A placeholder homepage
@app.route('/')
def welcome():
    return render_template('index.html')


# The actual webhook that TradingView uses
@ app.route('/webhook', methods=['POST'])
def webhook():
    data = json.loads(request.data)

    if data['passphrase'] != config.WEBHOOK_PASSPHRASE:
        bot.sendMessage(
            config.USER_ID, "⚠ *Unauthorized request warning* ⚠\n\n\
                Someone has just tried to execute an order via your bot,\
                but he doesn't know the passphrase. Consider changing it.",\
                parse_mode='Markdown')
        return {
            "code": "error",
            "message": "Nice try, invalid passphrase"
        }

    activeSymbol = data["strategy"]["symbol"].upper()
    pair = activeSymbol.split(" ")
    activeSymbol = pair[0]+pair[1]

    doubleOrder = bool(data["strategy"]["doubleorder"])

    balances = [float(client.get_asset_balance(asset=pair[0])['free']),
                float(client.get_asset_balance(asset=pair[1])['free'])]

    price = cryptocompare.get_price(pair[0], pair[1])[pair[0]][pair[1]]

    minNotional = float(client.get_symbol_info(
        activeSymbol)['filters'][3]['minNotional'])

    side = data['strategy']['order_action'].upper()

    if doubleOrder:
        priceUp = float(client.get_avg_price(symbol=pair[0]+"UPUSDT")["price"])
        priceDown = float(client.get_avg_price(symbol=pair[0]+"DOWNUSDT")["price"])
        balanceDown = float(client.get_asset_balance(asset=pair[0]+"DOWN")['free'])
        usdtBalance = float(client.get_asset_balance(asset="USDT")['free'])
        balanceUp = float(client.get_asset_balance(asset=pair[0]+"UP")['free'])

        if side == "SELL":
            quantity = str(truncate(balanceUp/1.05, 2))
            order_response = order(side, quantity, pair[0]+"UPUSDT")
            time.sleep(1)
            side = "BUY"
            usdtBalance = float(client.get_asset_balance(asset="USDT")['free'])
            quantity = str(truncate(usdtBalance/priceDown/1.05, 1))
            order_response2 = order(side, quantity, pair[0]+"DOWNUSDT")
        elif side == "BUY":
            side = "SELL"
            quantity = str(truncate(balanceDown/1.05, 1))
            order_response = order(side, quantity, pair[0]+"DOWNUSDT")
            time.sleep(1)
            side = "BUY"
            usdtBalance = float(client.get_asset_balance(asset="USDT")['free'])
            quantity = str(truncate(usdtBalance/priceUp/1.05, 2))
            order_response2 = order(side, quantity, pair[0]+"UPUSDT")
        if side == "SELLHALF":
            quantity = str(truncate(balanceUp/2/1.05, 2))
            order_response = order(side, quantity, pair[0]+"UPUSDT")
            time.sleep(1)
            side = "BUY"
            usdtBalance = float(client.get_asset_balance(asset="USDT")['free'])
            quantity = str(truncate(usdtBalance/priceDown/1.05, 1))
            order_response2 = order(side, quantity, pair[0]+"DOWNUSDT")
        elif side == "BUYHALF":
            side = "SELL"
            quantity = str(truncate(balanceDown/2/1.05, 1))
            order_response = order(side, quantity, pair[0]+"DOWNUSDT")
            time.sleep(1)
            side = "BUY"
            usdtBalance = float(client.get_asset_balance(asset="USDT")['free'])
            quantity = str(truncate(usdtBalance/priceUp/1.05, 2))
            order_response2 = order(side, quantity, pair[0]+"UPUSDT")
        if side == "SELLTHIRD":
            quantity = str(truncate(balanceUp/3/1.05, 2))
            order_response = order(side, quantity, pair[0]+"UPUSDT")
            time.sleep(1)
            side = "BUY"
            usdtBalance = float(client.get_asset_balance(asset="USDT")['free'])
            quantity = str(truncate(usdtBalance/priceDown/1.05, 1))
            order_response2 = order(side, quantity, pair[0]+"DOWNUSDT")
        elif side == "BUYTHIRD":
            side = "SELL"
            quantity = str(truncate(balanceDown/3/1.05, 1))
            order_response = order(side, quantity, pair[0]+"DOWNUSDT")
            time.sleep(1)
            side = "BUY"
            usdtBalance = float(client.get_asset_balance(asset="USDT")['free'])
            quantity = str(truncate(usdtBalance/priceUp/1.05, 2))
            order_response2 = order(side, quantity, pair[0]+"UPUSDT")
    elif side == "SELL":
        quantity = str(truncate(balances[0], 3))
    elif side == "BUY":
        quantity = str(truncate(balances[1]/price, 3))
    elif side == "SELLHALF":
        side = "SELL"
        quantity = str(truncate(balances[0]/2, 3))
    elif side == "BUYHALF":
        side = "BUY"
        quantity = str(truncate(balances[1]/price/2, 3))
    elif side == "SELLTHIRD":
        side = "SELL"
        quantity = str(truncate(balances[0]/3, 3))
    elif side == "BUYTHIRD":
        side = "BUY"
        quantity = str(truncate(balances[1]/price/3, 3))

    if float(quantity) <= minNotional:
        quantity = minNotional + \
            truncate(minNotional/5, len(str(minNotional).split('.')[1]))

    if not doubleOrder:
        order_response = order(side, quantity, activeSymbol)

    if order_response:
        if order_response2 & doubleOrder:
            bot.sendMessage(config.USER_ID,\
                f"💹 *{side}* double order on *{pair[0]}* of {quantity}\n\
                    from the _{data['time']}m trigger_", parse_mode='Markdown')
        else:
            bot.sendMessage(config.USER_ID,\
                f"✅ *{side}* order on *{activeSymbol}* of {quantity} {pair[1]}\n\
                    from the _{data['time']}m trigger_", parse_mode='Markdown')

        return {
            "code": "success",
            "message": "order executed"
        }

    else:
        return {
            "code": "error",
            "message": "order failed"
        }


if __name__ == '__main__':
    app.run()
