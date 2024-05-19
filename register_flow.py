import os
from prefect.client.orion import OrionClient
from stock_flow import flow

PREFECT_API_URL = os.environ.get('PREFECT_API_URL')


client = OrionClient(api_url=PREFECT_API_URL)
flow.register(project_name='StockDataProject')
