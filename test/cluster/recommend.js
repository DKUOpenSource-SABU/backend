import http from 'k6/http';
import { check, group } from 'k6';

export const options = {
  vus: 60,
  duration: '10s',
};

const BASE_URL = 'http://localhost:8000'; // 실제 주소로 변경

export default function () {
  group("✅ 유효한 티커로 추천 요청", () => {
    const payload = JSON.stringify({
      tickers: ["AAPL", "MSFT", "GOOGL", "TSLA"]
    });

    const res = http.post(`${BASE_URL}/cluster/recommend`, payload, {
      headers: { 'Content-Type': 'application/json' },
    });

    check(res, {
      'Status is 200': (r) => r.status === 200,
      '추천 결과가 배열 형태': (r) => {
        try {
          const parsed = JSON.parse(r.body);
          return Array.isArray(parsed) && parsed.length >= 0;
        } catch {
          return false;
        }
      },
    });
  });

  group("🚫 4개 미만 티커 요청", () => {
    const payload = JSON.stringify({
      tickers: ["AAPL", "MSFT"]
    });

    const res = http.post(`${BASE_URL}/cluster/recommend`, payload, {
      headers: { 'Content-Type': 'application/json' },
    });

    check(res, {
      'Status is 200': (r) => r.status === 200,
      '추천 결과가 배열 형태': (r) => {
        try {
          const parsed = JSON.parse(r.body);
          return Array.isArray(parsed) && parsed.length >= 0;
        } catch {
          return false;
        }
      },
    });
  });

  group("🚫 빈 티커 리스트", () => {
    const payload = JSON.stringify({
      tickers: []
    });

    const res = http.post(`${BASE_URL}/cluster/recommend`, payload, {
      headers: { 'Content-Type': 'application/json' },
    });
    check(res, {
      'Status is 500': (r) => [500].includes(r.status),
    });
  });

  group("❌ 잘못된 요청 형식", () => {
    const payload = JSON.stringify({
      tickers: null
    });

    const res = http.post(`${BASE_URL}/cluster/recommend`, payload, {
      headers: { 'Content-Type': 'application/json' },
    });

    check(res, {
      'Status is 400 이상': (r) => r.status >= 400,
    });
  });
}
