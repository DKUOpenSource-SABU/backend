import requests
import os

API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY')

# replace the "demo" apikey below with your own key from https://www.alphavantage.co/support/#api-key
url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=QQQ&interval=5min&apikey={API_KEY}&outputsize=full&datatype=csv'
r = requests.get(url)
data = r.json()

print(data)