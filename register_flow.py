import os
from prefect import flow
from prefect.deployments import Deployment
from stock_flow import flow as stock_flow

PREFECT_API_URL = os.environ.get('PREFECT_API_URL')

deployment = Deployment.build_from_flow(
    flow=stock_flow,
    name="stock-flow-deployment"
)

deployment.apply()
