
# Simple Moving Average Crossover Strategy

import MetaTrader5 as mt5  # install using 'pip install MetaTrader5'
import pandas as pd  # install using 'pip install pandas'
from datetime import datetime
import time
     
# function to send a market order
def market_order(symbol, volume, order_type, **kwargs):
    tick = mt5.symbol_info_tick(symbol)
    TAKEPROFIT = 25 
    STOPLOSS = 10
    point = mt5.symbol_info(symbol).point
    price = mt5.symbol_info_tick(symbol).ask
    type_execution = ""
    if order_type == "buy":
        tp = price+TAKEPROFIT*point
        sl = price-STOPLOSS*point
        type_execution = mt5.ORDER_TYPE_BUY_STOP
    elif order_type == "sell":
        type_execution = mt5.ORDER_TYPE_SELL_STOP
        tp = price-TAKEPROFIT*point
        sl = price+STOPLOSS*point
    else:
        type_execution = "neutral"

    price_dict = {'buy': tick.ask, 'sell': tick.bid}

    request = {
        "action": mt5.TRADE_ACTION_PENDING,
        "symbol": symbol,
        "volume": volume,
        "type":  type_execution,
        "price": price_dict[order_type],
        "tp": tp,
        "sl": sl,
        "deviation": DEVIATION,
        "magic": 100,
        "comment": "python market order",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }

    order_result = mt5.order_send(request)
    print(order_result)

    return order_result

# function to close an order base don ticket id
def close_order(ticket):
    positions = mt5.positions_get()

    for pos in positions:
        tick = mt5.symbol_info_tick(pos.symbol)
        type_dict = {0: 1, 1: 0}  # 0 represents buy, 1 represents sell - inverting order_type to close the position
        price_dict = {0: tick.ask, 1: tick.bid}
        type_execution = ""
        if type_dict == 0:
            type_execution = mt5.ORDER_TYPE_BUY_STOP
        elif type_dict == 1:
            type_execution = mt5.ORDER_TYPE_SELL_STOP
        else:
            type_execution = ""

        if pos.ticket == ticket:
            request = {
                "action": mt5.TRADE_ACTION_PENDING,
                "position": pos.ticket,
                "symbol": pos.symbol,
                "volume": pos.volume,
                "type": type_execution,
                "price": price_dict[pos.type],
                "deviation": DEVIATION,
                "magic": 100,
                "comment": "python close order",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_IOC,
            }

            order_result = mt5.order_send(request)
            print(order_result)

            return order_result

    return 'Ticket does not exist'


# function to get the exposure of a symbol
def get_exposure(symbol):
    positions = mt5.positions_get(symbol=symbol)
    if positions:
        pos_df = pd.DataFrame(positions, columns=positions[0]._asdict().keys())
        exposure = pos_df['volume'].sum()

        return exposure

# function to look for trading signals
def signal(symbol, timeframe, sma_period):
    bars = mt5.copy_rates_from_pos(symbol, timeframe, 1, sma_period)
    bars_df = pd.DataFrame(bars)
    last_close = bars_df.iloc[-1].close
    
    # SMA indicator
    sma = bars_df.close.mean()

    #Fractals
    
    # Evaluate buy and sell signals based on RSI, SMA, ATR and Fractals
    direction = 'flat'

    for index, row in bars_df.iterrows():
        if  sma > last_close:
            direction = 'buy'
        elif sma < last_close:
            direction = 'sell'
        else:
            direction = 'neutral'



    return last_close, sma, direction


if __name__ == '__main__':

    # strategy parameters
    SYMBOL = "EURUSD"
    VOLUME = 1.0
    TIMEFRAME = mt5.TIMEFRAME_M1
    SMA_PERIOD = 10
    DEVIATION = 20

    mt5.initialize(login=1051954145, server='FTMO-Demo',password='5NBFHWNLPV')

    while True:
        # calculating account exposure
        exposure = get_exposure(SYMBOL)
         # calculating last candle close and simple moving average and checking for trading signal
        last_close, sma, direction = signal(SYMBOL, TIMEFRAME, SMA_PERIOD)
        for pos in mt5.positions_get():
                TICKET = pos.ticket
                #trail_sl()
        # trading logic
        if direction == 'buy':
            # if we have a BUY signal, close all short positions
            for pos in mt5.positions_get():
                TICKET = pos.ticket
                #trail_sl()
                if pos.type == 1:  # pos.type == 1 represent a sell order
                   close_order(pos.ticket)

            # if there are no open positions, open a new long position
            if not mt5.positions_total():
                 # if we have a BUY signal, close all short positions
                market_order(SYMBOL, VOLUME, direction)

        elif direction == 'sell':
            # if we have a SELL signal, close all short positions
            for pos in mt5.positions_get():
                TICKET = pos.ticket
                #trail_sl()
                if pos.type == 0:  # pos.type == 0 represent a buy order
                   close_order(pos.ticket)

            # if there are no open positions, open a new short position
            if not mt5.positions_total():
                market_order(SYMBOL, VOLUME, direction)

        print('time: ', datetime.now())
        print('exposure: ', exposure)
        print('last_close: ', last_close)
        print('sma: ', sma)
        print('signal: ', direction)
        print('-------\n')

        # update every 1 second
        time.sleep(1)



