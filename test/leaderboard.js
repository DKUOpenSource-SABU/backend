import http from 'k6/http';
import { check, group } from 'k6';

export const options = {
  vus: 5,
  duration: '10s',
};

const BASE_URL = 'http://localhost:8000'; // 실제 주소로 수정하세요

export default function () {
  group("✅ 리더보드 조회", () => {
    const res = http.get(`${BASE_URL}/backtest/leaderboard`);

    check(res, {
      'Status is 200': (r) => r.status === 200,
      'leaderboard 필드 존재': (r) => {
        try {
          const data = JSON.parse(r.body);
          return Array.isArray(data.leaderboard);
        } catch {
          return false;
        }
      },
      '항목이 0개 이상': (r) => {
        const data = JSON.parse(r.body);
        return data.leaderboard.length >= 0;
      },
    });
  });
}
