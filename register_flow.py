import os
from prefect import Client
from stock_flow import flow

PREFECT_API_URL = os.environ.get('PREFECT_API_URL')

client = Client(api_server=PREFECT_API_URL)
client.create_project(project_name='StockDataProject', create_if_not_exists=True)
flow.register(project_name='StockDataProject')
