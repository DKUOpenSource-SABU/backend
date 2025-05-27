import requests

url = "http://localhost:8000/backtest"

payload = {
    "initial_cash": 10000000,
    "start_date": "2020-01-01",
    "end_date": "2023-01-01",
    "commission": 0.001,
    "portfolio": [
        {"ticker": "BIS", "weight": 20},
        {"ticker": "BITS", "weight": 30},
        {"ticker": "BILS", "weight": 50}
    ]
}

response = requests.post(url, json=payload)

if response.status_code == 200:
    print("백테스트 성공")
    print(response.json())
else:
    print(f"실패 - status code: {response.status_code}")
    print(response.text)
