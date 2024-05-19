import os
from prefect.deployments import Deployment
from stock import fetch_and_send_stock_data  

PREFECT_API_URL = os.environ.get('PREFECT_API_URL')



deployment = Deployment.build_from_flow(
    flow=fetch_and_send_stock_data,
    name="fetch-and-send-stock-data-deployment"  
)

deployment.apply()
