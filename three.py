from iqoptionapi.stable_api import IQ_Option
import logging
import pandas as pd
import iqoptionapi
import time
import sys
import requests

def telegram_bot_sendtext(bot_message):
    bot_token = '5936883139:AAEUscW6GqEbwTyW0KZbQ3nSu_phhbytHTM'
    bot_chatID = '1155462778'
    send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chatID + \
                '&parse_mode=MarkdownV2&text=' + str(bot_message).replace('.', '\\.')  # Escape the dot character
    response = requests.get(send_text)
    return response.json()


logging.basicConfig(level=logging.DEBUG,format='%(asctime)s %(message)s')
I_want_money=IQ_Option("twotest@twotest.com","twotest@twotest.com")
#Default is "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36"
header={"User-Agent":r"Mozilla/5.0 (X11; Linux x86_64; rv:70.0) Gecko/20100101 Firefox/70.0"}
cookie={"I_want_money":"GOOD"}
MODE="PRACTICE"
I_want_money.set_session(header,cookie)
I_want_money.connect()#connect to iqoption
#print(I_want_money.check_connect())
I_want_money.connect()
I_want_money.get_server_timestamp()
I_want_money.change_balance(MODE)
                        #MODE: "PRACTICE"/"REAL"
I_want_money.get_balance()

API = IQ_Option("twotest@twotest.com", "twotest@twotest.com")
check, reason = API.connect()
if not check:
    telegram_bot_sendtext("Connection failed.")
    exit()
telegram_bot_sendtext("Connection successful")
k = I_want_money.get_balance()
telegram_bot_sendtext(k)
#parameters
bollinger_length = 20  #std length
bollinger_deviation = 2.4
EMA_length = 30
HMA1_length = 20 
HMA2_length = 25
x = 5
trade_placed = False

start_time = time.time()

def get_remaining_seconds(x):
    current_time = time.localtime()
    current_minute = current_time.tm_min
    remaining_seconds = (x - (current_minute % x)) * 60 - current_time.tm_sec
    return remaining_seconds
while True:
        current_price = API.get_candles("EURUSD", 60 * x, 1, time.time())[0]["close"]
        bot_seconds = get_remaining_seconds(30)
        if 25<bot_seconds<28:
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
           
        candles = API.get_candles("EURUSD", 60 * x, 100, time.time())
        close_prices = [candle["close"] for candle in candles]
        df = pd.DataFrame(candles)
        df['wma_half_length'] = df['close'].rolling(window=HMA1_length // 2).mean()
        df['wma_full_length'] = df['close'].rolling(window=HMA1_length).mean()
        df['diff'] = 2 * df['wma_half_length'] - df['wma_full_length']
        df['hma'] = df['diff'].rolling(window=int(HMA1_length ** 0.5)).mean()

        df['ema'] = df['close'].ewm(span=EMA_length, adjust=False).mean()

        df['wma_half_length2'] = df['close'].rolling(window=HMA2_length // 2).mean()
        df['wma_full_length2'] = df['close'].rolling(window=HMA2_length).mean()
        df['diff2'] = 2 * df['wma_half_length2'] - df['wma_full_length2']
        df['hma2'] = df['diff2'].rolling(window=int(HMA2_length ** 0.5)).mean()

        
        df['sma'] = (df['hma']+df['ema']+df['hma2'])/3
        df['std_dev'] = df['close'].rolling(window=bollinger_length).std()
        df['lower_band'] = df['sma'] - bollinger_deviation * df['std_dev']
        df['upper_band'] = df['sma'] + bollinger_deviation * df['std_dev']
        upper_band = df['upper_band'].iloc[-1]
        lower_band = df['lower_band'].iloc[-1]
        #balance_before = I_want_money.get_balance()
        if (current_price <= lower_band ) :
            if not trade_placed:
                now = time.time()
                remaining_seconds = get_remaining_seconds(x)
                entry_price = current_price
                telegram_bot_sendtext("CALL Trade placed successfully " )
                trade_placed = True
                trade_direction = "call"
            else:
                telegram_bot_sendtext("Error placing trade:")
        if (current_price >= upper_band ) :
            if not trade_placed:
                now = time.time()
                remaining_seconds = get_remaining_seconds(x)
                entry_price = current_price
                telegram_bot_sendtext("PUT Trade placed successfully")
                trade_placed = True
                trade_direction = "put"
            else:
                telegram_bot_sendtext("Error placing trade:")
        if trade_placed and time.time() > now + remaining_seconds-1:

            exit_price = API.get_candles("EURUSD", 60 * x, 1, time.time())[0]["close"]
            if (trade_direction == "call"):
                if(exit_price > entry_price):
                    profit_result = profit_result+1
                    telegram_bot_sendtext("Win")
                    trade_placed = False
                else:
                    telegram_bot_sendtext("loss")

            elif (trade_direction == "put") :
                if (exit_price < entry_price) :
                    loss_result = loss_result + 1
                    telegram_bot_sendtext("Win")
                    trade_placed = False
                else:
                    telegram_bot_sendtext("loss")

            else :
                telegram_bot_sendtext("Result Unknown")
                trade_placed = False
                

            balance_before = I_want_money.get_balance()
        time.sleep(0.5)
