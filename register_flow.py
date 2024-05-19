import os
from prefect import Client
from stock_flow import flow

PREFECT_API_URL = os.environ.get('PREFECT_API_URL')

client = Client(api=PREFECT_API_URL)

flow.register(project_name='StockDataProject')
