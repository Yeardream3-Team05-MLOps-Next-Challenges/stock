import os
import requests
import json
import asyncio

from prefect import flow
from prefect.deployments import DeploymentImage
from prefect.client.schemas.schedules import CronSchedule

# stock.py의 함수와 태스크를 가져옵니다.
from stock import fetch_and_send_stock_data

@flow(name="fetch_and_send_stock_data_flow", log_prints=True)
async def stock_flow():
    await fetch_and_send_stock_data()
    
    # 슬랙 웹훅 URL
    webhook_url = os.getenv("SLACK_WEBHOOK")

    # 전송할 메시지
    message = {
        'text': 'stock이 실행되었습니다'
    }

    # HTTP POST 요청을 통해 메시지 전송
    response = requests.post(
        webhook_url,
        data=json.dumps(message),
        headers={'Content-Type': 'application/json'}
    )

    # 응답 상태 코드 출력
    print('응답 상태 코드:', response.status_code)
    print('응답 내용:', response.text)

if __name__ == "__main__":
    stock_flow.deploy(
        name="stock-data-schedule-deployment",
        work_pool_name="docker-agent-pool",
        work_queue_name="docker-agent",
        image=DeploymentImage(
            name="stock-data-image",
            tag="0.15",
            platform="linux/arm64",
            buildargs={},
        ),
        schedule=(CronSchedule(cron="0 8 * * *", timezone="Asia/Seoul")),
        build=True,
    )
