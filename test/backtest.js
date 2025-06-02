import http from 'k6/http';
import { check, group } from 'k6';

export const options = {
  vus: 5,
  duration: '10s',
};

const BASE_URL = 'http://localhost:8000'; // 실제 주소로 변경

export default function () {
  group("✅ 정상적인 백테스트 요청", () => {
    const payload = JSON.stringify({
      initial_cash: 10000,
      start_date: "2021-01-01",
      end_date: "2023-01-01",
      commission: 0.001,
      portfolio: [
        { ticker: "AAPL", weight: 50 },
        { ticker: "AA", weight: 50 }
      ]
    });

    const res = http.post(`${BASE_URL}/backtest/`, payload, {
      headers: { 'Content-Type': 'application/json' },
    });

    check(res, {
      'Status is 200': (r) => r.status === 200,
      '결과에 수익률 포함': (r) => {
        try {
          const data = JSON.parse(r.body);
          return data.results[0].total_return !== undefined || data.results[0].max_drawdown !== undefined;
        } catch {
          return false;
        }
      }
    });
  });

  group("🚫 weight 합이 1이 아닌 경우", () => {
    const payload = JSON.stringify({
      initial_cash: 10000,
      start_date: "2021-01-01",
      end_date: "2023-01-01",
      commission: 0.001,
      portfolio: [
        { ticker: "AAPL", weight: 0.7 },
        { ticker: "MSFT", weight: 0.5 }
      ]
    });

    const res = http.post(`${BASE_URL}/backtest/`, payload, {
      headers: { 'Content-Type': 'application/json' },
    });

    check(res, {
      'Status is 400 또는 422': (r) => r.status >= 400,
    });
  });

  group("❌ 필수 필드 누락 (portfolio 없음)", () => {
    const payload = JSON.stringify({
      initial_cash: 10000,
      start_date: "2021-01-01",
      end_date: "2023-01-01",
      commission: 0.001
    });

    const res = http.post(`${BASE_URL}/backtest/`, payload, {
      headers: { 'Content-Type': 'application/json' },
    });

    check(res, {
      'Status is 422': (r) => r.status === 422,
    });
  });
}