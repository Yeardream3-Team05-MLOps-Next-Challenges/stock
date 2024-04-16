# pip install websockets
# pip install pycryptodome
# pip install kafka-python
# pip install requests

# -*- coding: utf-8 -*-
import websockets
import json
import requests
import os
import asyncio
from kafka import KafkaProducer
import logging
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# 환경 변수
APP_KEY = os.getenv('APP_KEY', 'default_url')
APP_SECRET = os.getenv('APP_SECRET', 'default_url')
HTS_ID = os.getenv('HTS_ID', 'default_url')
SERVER_HOST = os.getenv('SERVER_HOST', 'default_url')

# 로깅 기본 설정: 로그 레벨, 로그 파일 경로 및 형식 설정
logging.basicConfig(level=logging.INFO, filename='app0416.log', filemode='a', format='%(name)s - %(levelname)s - %(message)s')

# Kafka Producer 설정
producer = KafkaProducer(acks=0,
                         compression_type='gzip',
                         bootstrap_servers=[f'{SERVER_HOST}:19094'],
                         value_serializer=lambda x:json.dumps(x).encode('utf-8'),
                         api_version=(2,)
                         )

logging.info('Kafka Producer 설정: acks=0, compression_type=gzip, bootstrap_servers')

def get_config():
    logging.info('get_config 호출됨')
    return {
        "appkey": APP_KEY,
        "appsecret": APP_SECRET,
        "htsid": HTS_ID,
        "kafka_topic": "stock_data_action",
    }

def get_approval(key, secret):
    logging.info('get_approval 호출됨')
    url = 'https://openapivts.koreainvestment.com:29443'
    headers = {"content-type": "application/json"}
    body = {"grant_type": "client_credentials", "appkey": key, "secretkey": secret}
    PATH = "oauth2/Approval"
    URL = f"{url}/{PATH}"
    res = requests.post(URL, headers=headers, data=json.dumps(body))
    approval_key = res.json()["approval_key"]
    return approval_key

async def send_to_kafka(data):
    logging.info('kafka로 전송 시작')
    producer.send(get_config()["kafka_topic"], value=data)
    logging.info('kafka로 데이터 전송 완료')

async def stockhoka(data):
    logging.info('stockhoka 처리 시작')
    recvvalue = data.split('^')
    await send_to_kafka({
        "종목코드": recvvalue[0],
        "현재가": recvvalue[3],
        "현재시간": recvvalue[1],
    })
    logging.info('stockhoka 처리 완료')

async def connect():
    logging.info('websocket 연결 시작')
    config = get_config()
    g_approval_key = get_approval(config["appkey"], config["appsecret"])
    print(f"approval_key: {g_approval_key}")

    url = 'ws://ops.koreainvestment.com:31000'
    code_list = [
        ['1', 'H0STASP0', '005930'],
        ['1', 'H0STASP0', '051910'],
        ['1', 'H0STASP0', '000660'],
    ]
    senddata_list = [json.dumps({"header": {"approval_key": g_approval_key, "custtype": "P", "tr_type": i, "content-type": "utf-8"}, "body": {"input": {"tr_id": j, "tr_key": k}}}) for i, j, k in code_list]

    async with websockets.connect(url, ping_interval=None) as ws:
        for senddata in senddata_list:
            await ws.send(senddata)
            await asyncio.sleep(0.5)

        while True:
            try:
                data = await ws.recv()
                if data[0] in ['0', '1']:
                    recvstr = data.split('|')
                    trid0 = recvstr[1]
                    if trid0 == "H0STASP0":
                        await stockhoka(recvstr[3])
                else:  # 웹소켓 세션 유지를 위한 PINGPONG 메시지 처리
                    jsonObject = json.loads(data)
                    trid = jsonObject["header"]["tr_id"]
                    if trid == "PINGPONG":
                        print(f"### RECV [PINGPONG] [{data}]")
                        print(f"### SEND [PINGPONG] [{data}]")
                        await ws.send(data)  # PINGPONG 메시지 응답
            except websockets.ConnectionClosed:
                continue
    logging.info('websocket 연결 종료')

async def main():
    await asyncio.gather(connect())

if __name__ == "__main__":
    asyncio.run(main())
