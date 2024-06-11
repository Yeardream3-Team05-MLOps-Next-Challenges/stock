import os
from dotenv import load_dotenv
from prefect.deployments import Deployment
from prefect.infrastructure.docker import DockerContainer
from prefect.agent import Agent  # 수정된 부분
from stock import fetch_and_send_stock_data

# .env 파일 로드
load_dotenv()

PREFECT_API_URL = os.getenv('PREFECT_API_URL')

if not PREFECT_API_URL:
    raise ValueError("PREFECT_API_URL 환경 변수가 설정되지 않았습니다.")
else:
    print("PREFECT_API_URL is set")

# Docker 컨테이너 설정
docker_block = DockerContainer(
    image="docker_image_stock:tag",
    image_pull_policy="ALWAYS",
    auto_remove=True
)

docker_block.save("stock-data-container", overwrite=True)

# Flow와 Deployment 정의 및 적용
deployment = Deployment.build_from_flow(
    flow=fetch_and_send_stock_data,
    name="fetch-and-send-stock-data-deployment",
    infrastructure=docker_block,
    tags=["stock", "data"]
)

deployment.apply()

print("Deployment created and applied successfully.")

# 에이전트 설정 및 실행
agent = Agent(
    work_queue="default",
    show_flow_logs=True
)

agent.start()
