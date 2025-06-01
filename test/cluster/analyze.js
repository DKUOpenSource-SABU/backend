import http from 'k6/http';
import { check, group } from 'k6';

export const options = {
  vus: 5,
  duration: '10s',
};

const BASE_URL = 'http://localhost:8000'; // 실제 주소로 교체

export default function () {
  group("✅ 정상 요청 (유효한 티커)", () => {
    const payload = JSON.stringify({
      tickers: ["AAPL", "MSFT"]
    });

    const res = http.post(`${BASE_URL}/cluster/analyze?pre=default`, payload, {
      headers: { 'Content-Type': 'application/json' },
    });

    check(res, {
      'Status is 200': (r) => r.status === 200,
      'nodes 포함': (r) => JSON.parse(r.body).nodes !== undefined,
      'hull_coords 포함': (r) => JSON.parse(r.body).hull_coords !== undefined,
    });
  });

  group("🚫 빈 티커 리스트", () => {
    const payload = JSON.stringify({
      tickers: []
    });

    const res = http.post(`${BASE_URL}/cluster/analyze?pre=default`, payload, {
      headers: { 'Content-Type': 'application/json' },
    });

    check(res, {
      'Status는 200이거나 204/400 여부 확인': (r) =>
        [200, 204, 400].includes(r.status),
    });
  });

  group("❌ pre 파라미터 누락", () => {
    const payload = JSON.stringify({
      tickers: ["AAPL"]
    });

    const res = http.post(`${BASE_URL}/cluster/analyze`, payload, {
      headers: { 'Content-Type': 'application/json' },
    });

    check(res, {
      'Status는 422 또는 400 여부 확인': (r) =>
        [400, 422].includes(r.status),
    });
  });
}
