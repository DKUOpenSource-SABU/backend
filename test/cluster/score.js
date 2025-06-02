import http from 'k6/http';
import { check, group } from 'k6';

export const options = {
  vus: 5,
  duration: '10s',
};

const BASE_URL = 'http://localhost:8000'; // 실제 주소로 교체

export default function () {
  group("✅ 정상 요청 (4개 종목)", () => {
    const payload = JSON.stringify({
      ratios: [
        { ticker: "AAPL", ratio: 25 },
        { ticker: "MSFT", ratio: 25 },
        { ticker: "GOOGL", ratio: 25 },
        { ticker: "TSLA", ratio: 25 }
      ]
    });

    const res = http.post(`${BASE_URL}/cluster/score`, payload, {
      headers: { 'Content-Type': 'application/json' },
    });

    check(res, {
      'Status is 200': (r) => r.status === 200,
      'cluster_score 필드 존재': (r) => JSON.parse(r.body).cluster_score !== undefined,
    });
  });

  group("🚫 종목 부족 (3개 이하)", () => {
    const payload = JSON.stringify({
      ratios: [
        { ticker: "AAPL", ratio: 50 },
        { ticker: "MSFT", ratio: 50 },
        { ticker: "TSLA", ratio: 0 }
      ]
    });

    const res = http.post(`${BASE_URL}/cluster/score`, payload, {
      headers: { 'Content-Type': 'application/json' },
    });

    check(res, {
      'Status is 400 또는 422': (r) => [400, 422].includes(r.status),
    });
  });

  group("❌ 잘못된 데이터 (ratio 생략)", () => {
    const payload = JSON.stringify({
      ratios: [
        { ticker: "AAPL" },
        { ticker: "MSFT" },
        { ticker: "GOOGL" },
        { ticker: "TSLA" }
      ]
    });

    const res = http.post(`${BASE_URL}/cluster/score`, payload, {
      headers: { 'Content-Type': 'application/json' },
    });

    check(res, {
      'Status is 422 또는 400': (r) => r.status >= 400,
    });
  });
}
