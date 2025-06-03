# 🌐 SABU API 명세서

## 📋 전체 API 목록 요약

| 분류 | 프로세스 ID | HTTP Method | Endpoint | 설명 |
|------|-------------|-------------|----------|------|
| 클러스터링 | CLU-001 | POST | /cluster/analyze | 종목 클러스터링 분석 |
| 클러스터링 | CLU-002 | POST | /cluster/recommend | 분산투자 종목 추천 |
| 클러스터링 | CLU-003 | POST | /cluster/score | 클러스터 점수 산출 |
| 클러스터링 | CLU-004 | GET  | /cluster/sectors | 섹터별 클러스터링 결과 조회 |
| 백테스트 | BTE-001 | POST | /backtest/ | 백테스트 실행 |
| 백테스트 | BTE-002 | GET  | /backtest/leaderboard | 전략 리더보드 조회 |
| ETF 데이터 | COL-001 | POST | /search/ticker | 키워드 기반 종목 검색 |
| ETF 데이터 | COL-002 | GET  | /search/ticker/daily (외 3종) | 기간별 가격 데이터 조회 |
| ETF 데이터 | COL-003 | GET  | /search/ticker/meta | ETF 메타 정보 조회 |
| ETF 데이터 | COL-004 | GET  | /search/ticker/news | 관련 뉴스 및 감정 분석 |

---
![alt text](image-1.png)
## 📦 클러스터링 기능 (CLU)

### 📍 POST `/cluster/analyze`  
> 선택한 종목에 대해 클러스터링 수행  
**프로세스 ID**: CLU-001

- **요청 Body**:
```json
{
  "tickers": [
    "string"
  ]
}
```

- **응답 예시**:
```json
{
  "clusters": [
    {
      "cluster": 0,
      "hull_coords": [
        { "x": -1.97, "y": 1.31 },
        { "x": -2.28, "y": 0.36 },
        { "x": -2.00, "y": -0.12 },
        ...
      ]
    },
    {
      "cluster": 1,
      "hull_coords": [
        { "x": 0.96, "y": 2.52 },
        { "x": 0.10, "y": 0.93 },
        { "x": -0.21, "y": -0.02 },
        ...
      ]
    },
    {
      "cluster": 2,
      "hull_coords": [
        { "x": 1.73, "y": 17.58 },
        { "x": -1.12, "y": 5.22 },
        { "x": 0.34, "y": 3.26 },
        ...
      ]
    },
    {
      "cluster": 3,
      "hull_coords": [
        { "x": -0.50, "y": -0.28 },
        { "x": 0.07, "y": 0.87 },
        { "x": -0.08, "y": 2.12 },
        ...
      ]
    }
  ]
}

```

### 📍 POST `/cluster/recommend`  
> 클러스터링 기반 유사 종목 추천  
**프로세스 ID**: CLU-002

- **요청 Body**:
```json
{
  "tickers": [
    "string"
  ]
}
```

- **응답 예시**:
```json
[
  {
    "SYMBOL": "ALLR",
    "NAME": "Allarity Therapeutics Inc.",
    "LAST PRICE": "$1.07",
    "% CHANGE": "2.89%",
    "SECTOR": "Health Care",
    "CLUSTER": 2
  },
  {
    "SYMBOL": "AZ",
    "NAME": "A2Z Cust2Mate Solutions Corp.",
    "LAST PRICE": "$9.31",
    "% CHANGE": "-0.21%",
    "SECTOR": "Industrials",
    "CLUSTER": 2
  },
  {
    "SYMBOL": "F",
    "NAME": "Ford Motor Company",
    "LAST PRICE": "$10.75",
    "% CHANGE": "-0.46%",
    "SECTOR": "Consumer Discretionary",
    "CLUSTER": 1
  },
  ...
]
```

### 📍 POST `/cluster/score`  
> 클러스터 평가 점수 계산  
**프로세스 ID**: CLU-003

- **요청 Body**:
```json
{
  "ratios": [
    {
      "ticker": "AAPL",
      "ratio": 30
    },
    {
      "ticker": "AA",
      "ratio": 70
    }
  ]
}
```

- **응답 예시**:
```json
{
  "cluster_score": 0.33533439143925264
}
```
### 📍 GET `/cluster/sectors`  
> 섹터별 클러스터링 결과 조회  
**프로세스 ID**: CLU-004

- **응답 예시**:
```json
{
  "sectors": [
    {
      "sector": "Basic Materials",
      "PC1": -0.81,
      "PC2": -2.68
    },
    {
      "sector": "Consumer Discretionary",
      "PC1": -0.64,
      "PC2": 1.73
    },
    {
      "sector": "Finance",
      "PC1": 3.39,
      "PC2": -1.38
    },
    {
      "sector": "Health Care",
      "PC1": -5.16,
      "PC2": -1.42
    },
    ...
  ]
}
```

## 📦 백테스트 기능 (BTE)

### 📍 POST `/backtest/`  
> 포트폴리오 백테스트 실행  
**프로세스 ID**: BTE-001

- **요청 Body**:
```json
{
  "initial_cash": 0,
  "start_date": "string",
  "end_date": "string",
  "commission": 0,
  "portfolio": [
    {
      "ticker": "string",
      "weight": 0
    }
  ]
}
```

- **응답 예시**:
```json
{
  "results": [
    {
      "strategy": "Buy and Hold",
      "rebalance": "none",
      "initial_balance": 1000000,
      "final_balance": 699627.63,
      "total_return": -30.04,
      "cagr": -59.89,
      "max_drawdown": -33.88,
      "portfolio_growth": [
        { "date": "2025-01", "value": 1000000 },
        { "date": "2025-02", "value": 926008.41 },
        ...
      ],
      "assets": [
        {
          "ticker": "AAPL",
          "weight": 0.3,
          "return_pct": -12.42
        },
        {
          "ticker": "AA",
          "weight": 0.7,
          "return_pct": -35.20
        }
      ]
    },
    {
      "strategy": "RSI",
      "rebalance": "monthly",
      "initial_balance": 1000000,
      "final_balance": 979076.69,
      "total_return": -2.09,
      "cagr": -6.17,
      "max_drawdown": -15.9,
      "portfolio_growth": [
        { "date": "2025-01", "value": 1000000 },
        { "date": "2025-02", "value": 1011738.04 },
        ...
      ],
      "assets": [
        {
          "ticker": "AAPL",
          "weight": 0.3,
          "return_pct": -12.42
        },
        {
          "ticker": "AA",
          "weight": 0.7,
          "return_pct": -35.20
        }
      ]
    },
    ...
  ]
}

```

### 📍 GET `/backtest/leaderboard`  
> 전략 리더보드 조회  
**프로세스 ID**: BTE-002

- **응답 예시**:
```json
{
  "leaderboard": [
    {
      "total_return": 75.59,
      "strategy": {
        "strategy": "RSI",
        "rebalance": "monthly",
        "start_date": "2021-01",
        "end_date": "2022-12",
        "initial_balance": 10000,
        "final_balance": 17559.24,
        "cagr": 48.40,
        "max_drawdown": -17.63,
        "assets": [
          {
            "ticker": "AAPL",
            "weight": 0.5,
            "return_pct": 1.61
          },
          {
            "ticker": "AA",
            "weight": 0.5,
            "return_pct": 97.45
          }
        ]
      }
    },
    ...
  ]
}
```

## 📦 ETF 데이터 수집 기능 (COL)

### 📍 POST `/search/ticker`  
> 키워드 기반 ETF 종목 검색  
**프로세스 ID**: COL-001

- **요청 Body**:
```json
GET /search/ticker/daily?ticker=SPY

{
  "clusters": [
    0
  ]
}
```

- **응답 예시**:
```json
{
  "results": [
    {
      "SYMBOL": "AACT",
      "NAME": "Ares Acquisition Corporation II Class A Ordinary Shares",
      "LAST PRICE": "$11.28",
      "% CHANGE": "0.089%",
      "SECTOR": "Finance",
      "CLUSTER": 0
    },
    {
      "SYMBOL": "AAME",
      "NAME": "Atlantic American Corporation Common Stock",
      "LAST PRICE": "$1.72",
      "% CHANGE": "0.00%",
      "SECTOR": "Finance",
      "CLUSTER": 0
    },
    ...
  ]
}
```

### 📍 GET `/search/ticker/daily`(외 /weekly, /monthly, /annual)  
> 기간별 가격 데이터 조회  
**프로세스 ID**: COL-002

- **요청 Body**:
```
GET /search/ticker/daily?ticker=SPY
```

- **응답 예시**:
```json
[
  {
    "date": "2025-02-13T00:00:00",
    "close": 241.232450604122,
    "high": 242.3399,
    "low": 235.57,
    "open": 236.91,
    "volume": 53614054,
    "adjClose": 241.232450604122,
    "adjHigh": 242.041352859512,
    "adjLow": 235.279792940062,
    "adjOpen": 236.618142146411,
    "adjVolume": 53614054,
    "divCash": 0,
    "splitFactor": 1
  },
  ...
]
```

### 📍 GET `/search/ticker/meta?ticker={ticker}`  
> ETF 메타 정보 조회  
**프로세스 ID**: COL-003

- **응답 예시**:
```json
{
  "ticker": "AAPL",
  "name": "Apple Inc",
  "description": "Apple Inc. (Apple) designs, manufactures and markets mobile communication and media devices, personal computers, and portable digital music players, and a variety of related software, services, peripherals, networking solutions, and third-party digital content and applications. The Company's products and services include iPhone, iPad, Mac, iPod, Apple TV, a portfolio of consumer and professional software applications, the iOS and OS X operating systems, iCloud, and a variety of accessory, service and support offerings. The Company also delivers digital content and applications through the iTunes Store, App StoreSM, iBookstoreSM, and Mac App Store. The Company distributes its products worldwide through its retail stores, online stores, and direct sales force, as well as through third-party cellular network carriers, wholesalers, retailers, and value-added resellers. In February 2012, the Company acquired app-search engine Chomp.",
  "startDate": "1980-12-12",
  "endDate": "2025-06-02",
  "exchangeCode": "NASDAQ"
}
```

### 📍 GET `/search/ticker/news?ticker={ticker}`  
> 관련 뉴스 및 감정 분석 조회  
**프로세스 ID**: COL-004

- **응답 예시**:
```json
{
  "results": [
    {
      "id": 83565095,
      "publishedDate": "2025-06-03T08:11:38.894814Z",
      "title": "Citigroup Reaffirms Buy Rating for Apple (AAPL) Amid WWDC 2025 Expectations",
      "url": "https://www.gurufocus.com/news/2903670/citigroup-reaffirms-buy-rating-for-apple-aapl-amid-wwdc-2025-expectations",
      "description": "Citigroup has maintained its \"buy\" rating for Apple (AAPL), setting a target price of $240. The bank believes that investor expectations for Apple's 2025 Worldw",
      "source": "gurufocus.com",
      "tags": [
        "Aapl",
        "Article",
        "Financial Services",
        "Gurufocus",
        "Gurufocus News",
        "News",
        "Stock",
        "Technology",
        "Unknown Sector"
      ],
      "crawlDate": "2025-06-03T08:11:39.549350Z",
      "tickers": [
        "aapl",
        "c",
        "ne-ws"
      ],
      "sentiment": "neutral"
    },
  ...
  ],
  "sentiment_counts": {
    "positive": 1,
    "negative": 2,
    "neutral": 7
  }
}
```