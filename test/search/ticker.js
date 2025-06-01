import http from 'k6/http';
import { check, group } from 'k6';

export const options = {
  vus: 5,
  duration: '10s',
};

const BASE_URL = 'http://localhost:8000'; // 실제 주소로 바꿔주세요

export default function () {
  group("✅ 정상적인 클러스터 요청", () => {
    const validClusters = JSON.stringify({ clusters: [0, 1, 2, 3] });

    const res = http.post(`${BASE_URL}/search/ticker?query=AAPL`, validClusters, {
      headers: { 'Content-Type': 'application/json' },
    });

    check(res, {
      'Status is 200': (r) => r.status === 200,
      'results 배열이 존재하고 0개 이상': (r) => {
        try {
          const body = JSON.parse(r.body);
          return Array.isArray(body.results) && body.results.length >= 0;
        } catch (e) {
          return false;
        }
      },
    });
  });

  group("⚠️ 클러스터 필터 없음 (전체 검색)", () => {
    const res = http.post(`${BASE_URL}/search/ticker?query=GOOG`, null, {
      headers: { 'Content-Type': 'application/json' },
    });

    check(res, {
      'Status is 200': (r) => r.status === 200,
    });
  });

  group("🚫 존재하지 않는 클러스터 (예: [5, 6])", () => {
    const invalidClusters = JSON.stringify([5, 6]);

    const res = http.post(`${BASE_URL}/search/ticker?query=MSFT`, invalidClusters, {
      headers: { 'Content-Type': 'application/json' },
    });

    check(res, {
      'Status is 200 (응답은 OK)': (r) => r.status === 200,
      '결과 없음 또는 empty': (r) => {
        try {
          const parsed = JSON.parse(r.body);
          return Array.isArray(parsed.results) && parsed.results.length === 0;
        } catch (e) {
          return false;
        }
      },
    });
  });


  group("❌ query 생략 (필수 파라미터 누락)", () => {
    const res = http.post(`${BASE_URL}/search/ticker`, JSON.stringify([0, 1]), {
      headers: { 'Content-Type': 'application/json' },
    });

    check(res, {
      'Status is 422 (Unprocessable Entity)': (r) => r.status === 422,
    });
  });
}
