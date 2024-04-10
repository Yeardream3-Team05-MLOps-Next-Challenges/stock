# pip install websocket-client
# pip install pycryptodome
# pip install kafka-python

# -*- coding: utf-8 -*-
import websockets
import json
import requests
import os
import asyncio
from kafka import KafkaProducer


APP_KEY = os.getenv('APP_KEY', 'default_url')
APP_SECRET = os.getenv('APP_SECRET', 'default_url')
HTS_ID = os.getenv('HTS_ID', 'default_url')
SERVER_HOST = os.getenv('SERVER_HOST', 'default_url')

# Kafka Producer 설정
producer = KafkaProducer(acks=0,
                         compression_type='gzip',
                         bootstrap_servers=[f'{SERVER_HOST}:19094'],
                         value_serializer=lambda x:json.dumps(x).encode('utf-8'),
                          api_version=(2,)
                         )

def get_config():
    return {
        "appkey": APP_KEY,
        "appsecret": APP_SECRET,
        "htsid": HTS_ID,
        "kafka_topic": "stock_data_actions",  # Kafka 토픽 이름
    }



def get_approval(key, secret):
    """웹소켓 접속키 발급"""
    url = 'https://openapivts.koreainvestment.com:29443'  # 모의투자계좌
    headers = {"content-type": "application/json"}
    body = {"grant_type": "client_credentials", "appkey": APP_KEY, "secretkey": APP_SECRET}
    PATH = "oauth2/Approval"
    URL = f"{url}/{PATH}"
    res = requests.post(URL, headers=headers, data=json.dumps(body))
    approval_key = res.json()["approval_key"]
    return approval_key

async def send_to_kafka(data):
    """Kafka로 데이터 전송"""
    producer.send(get_config()["kafka_topic"], value=data)
    print(f"Kafka로 전송된 데이터: {data}")

async def stockhoka(data):
    """실시간 주식호가 데이터 출력 및 Kafka 전송"""
    recvvalue = data.split('^')
    print(f"종목코드: {recvvalue[0]}, 현재가: {recvvalue[3]}, 현재시간: {recvvalue[1]}")
    await send_to_kafka({
        "종목코드": recvvalue[0],
        "현재가": recvvalue[3],
        "현재시간": recvvalue[1],
    })


async def connect():
    config = get_config()
    g_approval_key = get_approval()
    print(f"approval_key: {g_approval_key}")
    
    url = 'ws://ops.koreainvestment.com:31000'  # 모의투자계좌
    
    # 주식호가에 대한 요청
    code_list = [
        ['1', 'H0STASP0', '005930'],  # 삼성전자
        ['1', 'H0STASP0', '051910'],  # LG화학
        ['1', 'H0STASP0', '000660'],  # SK하이닉스
    ]
    
    senddata_list = [json.dumps({"header": {"approval_key": g_approval_key, "custtype": "P", "tr_type": i, "content-type": "utf-8"}, "body": {"input": {"tr_id": j, "tr_key": k}}}) for i, j, k in code_list]

    async with websockets.connect(url, ping_interval=None) as ws:
        for senddata in senddata_list:
            await ws.send(senddata)
            await asyncio.sleep(0.5)
        
        while True:
            try:
                data = await ws.recv()
                if data[0] in ['0', '1']:  # 실시간 데이터일 경우
                    recvstr = data.split('|')
                    trid0 = recvstr[1]
                    if trid0 == "H0STASP0":  # 주식호가 처리
                        await stockhoka(recvstr[3])
            except websockets.ConnectionClosed:
                continue

def main():
    loop = asyncio.get_event_loop()
    if loop.is_running():
        task = loop.create_task(connect())
    else:
        loop.run_until_complete(connect())

if __name__ == "__main__":

    main()
