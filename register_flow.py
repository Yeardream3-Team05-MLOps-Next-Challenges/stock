import os
from dotenv import load_dotenv  # 추가
from prefect.deployments import Deployment
from stock import fetch_and_send_stock_data

# .env 파일 로드
load_dotenv()  # 추가

PREFECT_API_URL = os.getenv('PREFECT_API_URL')

if not PREFECT_API_URL:
    raise ValueError("PREFECT_API_URL 환경 변수가 설정되지 않았습니다.")
else:
    print("PREFECT_API_URL is set")

deployment = Deployment.build_from_flow(
    flow=fetch_and_send_stock_data,
    name="fetch-and-send-stock-data-deployment"
)

deployment.apply()

print("Deployment created and applied successfully.")
