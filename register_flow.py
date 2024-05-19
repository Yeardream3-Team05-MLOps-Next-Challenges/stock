import os
from prefect.deployments import Deployment
from stock import fetch_and_send_stock_data

PREFECT_API_URL = os.environ.get('PREFECT_API_URL')

if not PREFECT_API_URL:
    raise ValueError("PREFECT_API_URL 환경 변수가 설정되지 않았습니다.")

print("PREFECT_API_URL is set")  # 환경 변수가 설정되었음을 확인

deployment = Deployment.build_from_flow(
    flow=fetch_and_send_stock_data,
    name="fetch-and-send-stock-data-deployment"
)

deployment.apply()

print("Deployment created and applied successfully.")
