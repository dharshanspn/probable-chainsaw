from iqoptionapi.stable_api import IQ_Option
import logging
import pandas as pd
import iqoptionapi
import time
import sys
import requests
import numpy as np
import math

def telegram_bot_sendtext(bot_message):
    bot_token = '6099125962:AAFMqpPyiL902Dg9ySrRtfnysILH5M_YMr4'
    bot_chatID = '1155462778'
    send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chatID + \
                '&parse_mode=MarkdownV2&text=' + str(bot_message).replace('.', '\\.')  # Escape the dot character
    response = requests.get(send_text)
    return response.json()


def get_remaining_seconds(x):
    current_time = time.localtime()
    current_minute = current_time.tm_min
    remaining_seconds = (x - (current_minute % x)) * 60 - current_time.tm_sec
    return remaining_seconds

def calculate_wma(data, window):
    int_window = int(window)
    weights = pd.Series(range(1, int_window + 1))
    wma = data.rolling(int_window).apply(lambda x: np.dot(x, weights) / weights.sum(), raw=True)
    return wma

y = 5
current_start_time = time.localtime()
current_start_minute = current_start_time.tm_min
remaining_start_seconds = (y - (current_start_minute % 5)) * 60 - current_start_time.tm_sec
z=remaining_start_seconds-30
if remaining_start_seconds>30:
  time.sleep(z)


logging.basicConfig(level=logging.DEBUG,format='%(asctime)s %(message)s')
I_want_money=IQ_Option("custom_bb2@gmail.com","custom_bb2@gmail.com")
#Default is "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36"
header={"User-Agent":r"Mozilla/5.0 (X11; Linux x86_64; rv:70.0) Gecko/20100101 Firefox/70.0"}
cookie={"I_want_money":"GOOD"}
MODE="PRACTICE"
I_want_money.set_session(header,cookie)
I_want_money.connect()#connect to iqoption
#telegram_bot_sendtext(I_want_money.check_connect())
I_want_money.connect()
I_want_money.get_server_timestamp()
I_want_money.change_balance(MODE)
                        #MODE: "PRACTICE"/"REAL"
I_want_money.get_balance()

API = IQ_Option("custom_bb2@gmail.com", "custom_bb2@gmail.com")
check, reason = API.connect()
if not check:
    telegram_bot_sendtext("Connection failed.")
    exit()
telegram_bot_sendtext("Connection successful")
k = I_want_money.get_balance()
telegram_bot_sendtext(k)
#parameters
bollinger_length = 15  #std length and default 20
bollinger_deviation = 3
EMA_length = 30 #default 2.4
window = 20 #HMA1_length
window1 = 25 #HMA2_length
trade_placed = False
amount = 1
x = 5

start_time = time.time()

while True:
        current_price = API.get_candles("EURUSD-OTC", 60 * x, 1, time.time())[0]["close"]
        bot_seconds = get_remaining_seconds(30)
        if 26<bot_seconds<28:
            elapsed_time = time.time() - start_time
            if elapsed_time<60:
              status = f"UP Running...  {elapsed_time:.2f}s"
              telegram_bot_sendtext(status)
            elif 60 < elapsed_time < 3600:
              min = elapsed_time // 60
              status = f"UP Running...  {min:.2f} min"
              telegram_bot_sendtext(status)
            elif 3600 < elapsed_time < 86400 :
              hours = elapsed_time // 3600
              mins = (elapsed_time-hours*3600)//60
              status = f"UP Running...  {hours:.2f} hr {mins:.2f} min"
              telegram_bot_sendtext(status)
        candles = API.get_candles("EURUSD-OTC", 60 * x, 100, time.time())
        close_prices = [candle["close"] for candle in candles]
        df = pd.DataFrame(candles)
        # Calculate HMA1
        df['wma'] = calculate_wma(df['close'], window) #regular wma
        df['wma1'] = calculate_wma(df['close'], window/2) #half length wma
        df['wma2'] = 2*df['wma1']-df['wma']
        result = math.floor(math.sqrt(window))
        df['hma1'] = calculate_wma(df['wma2'], result)
        # Calculate HMA2
        df['wma2'] = calculate_wma(df['close'], window1) #regular wma
        df['wma21'] = calculate_wma(df['close'], window1/2) #half length wma
        df['wma22'] = 2*df['wma21']-df['wma2']
        result = math.floor(math.sqrt(window1))
        df['hma2'] = calculate_wma(df['wma2'], result)
        # Calculate EMA
        df['ema'] = df['close'].ewm(span=EMA_length, adjust=False).mean()
        #Calculate Bollinger
        df['sma'] = (df['hma1']+df['hma2']+df['ema'])/3
        df['std_dev'] = df['close'].rolling(window=bollinger_length).std()
        df['lower_band'] = df['sma'] - bollinger_deviation * df['std_dev']
        df['upper_band'] = df['sma'] + bollinger_deviation * df['std_dev']
        upper_band = df['upper_band'].iloc[-1]
        lower_band = df['lower_band'].iloc[-1]
        if (current_price <= lower_band ) :
            if not trade_placed:
                direction = "call"
                now = time.time()
                value = 6
                result, order_id = API.buy(amount, "EURUSD-OTC", direction, value)
                if result:
                    telegram_bot_sendtext("CALL Trade placed successfully " )
                    trade_placed = True
                else:
                    telegram_bot_sendtext("Error placing trade:")

        if (current_price >= upper_band ) :
            if not trade_placed:
                direction = "put"
                now = time.time()
                value = 6
                result, order_id = API.buy(amount, "EURUSD-OTC", direction, value)
                if result:
                    telegram_bot_sendtext("PUT Trade placed successfully")
                    trade_placed = True
                else:
                    telegram_bot_sendtext("Error placing trade:")
        if trade_placed and time.time() > now + remaining_seconds:
            trade_placed = False
        time.sleep(0.1)
