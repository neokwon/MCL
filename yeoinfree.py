import time
import pyupbit
import datetime
import requests  # requests 모듈 추가

access = "your-access"
secret = "your-secret"
telegram_token = "your-telegram-token"
chat_id = "your-chat-id"

def get_target_price(ticker, k):
    """변동성 돌파 전략으로 매수 목표가 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=2)
    target_price = df.iloc[0]['close'] + (df.iloc[0]['high'] - df.iloc[0]['low']) * k
    return target_price

def get_start_time(ticker):
    """시작 시간 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=1)
    start_time = df.index[0]
    return start_time

def get_ma5(ticker):  # 5일 이동평균선 함수로 변경
    """5일 이동 평균선 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=5)
    ma5 = df['close'].rolling(5).mean().iloc[-1]
    return ma5

def get_balance(ticker):
    """잔고 조회"""
    balances = upbit.get_balances()
    for b in balances:
        if b['currency'] == ticker:
            if b['balance'] is not None:
                return float(b['balance'])
            else:
                return 0
    return 0

def get_current_price(ticker):
    """현재가 조회"""
    return pyupbit.get_orderbook(ticker=ticker)["orderbook_units"][0]["ask_price"]

def send_telegram_message(message):
    """텔레그램으로 메시지 전송"""
    url = f"https://api.telegram.org/bot{telegram_token}/sendMessage"
    params = {
        "chat_id": chat_id,
        "text": message
    }
    response = requests.post(url, params=params)
    return response.json()

# 로그인
upbit = pyupbit.Upbit(access, secret)
print("autotrade start")
send_telegram_message("자동매매 프로그램이 시작되었습니다.")

# 자동매매 시작
while True:
    try:
        now = datetime.datetime.now()
        start_time = get_start_time("KRW-BTC")  # 비트코인으로 변경
        end_time = start_time + datetime.timedelta(days=1)

        if start_time < now < end_time - datetime.timedelta(seconds=10):
            target_price = get_target_price("KRW-BTC", 0.5)
            ma5 = get_ma5("KRW-BTC")  # 5일 이동평균선으로 변경
            current_price = get_current_price("KRW-BTC")
            if target_price < current_price and ma5 < current_price:
                krw = get_balance("KRW")
                if krw > 5000:
                    upbit.buy_market_order("KRW-BTC", krw*0.9995)
                    send_telegram_message("비트코인을 구매하였습니다.")
        else:
            btc = get_balance("BTC")  # 비트코인으로 변경
            if btc > 0.00008:
                upbit.sell_market_order("KRW-BTC", btc*0.9995)
                send_telegram_message("비트코인을 판매하였습니다.")
        time.sleep(1)
    except Exception as e:
        print(e)
        time.sleep(1)
