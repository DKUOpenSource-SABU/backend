import http from 'k6/http';
import { check, group } from 'k6';

export const options = {
  vus: 5,
  duration: '10s',
};

const BASE_URL = 'http://localhost:8000'; // 실제 서버 주소로 교체

export default function () {
  group("✅ 섹터 분석 - 정상 응답 확인", () => {
    const res = http.get(`${BASE_URL}/cluster/sectors`);

    check(res, {
      'Status is 200': (r) => r.status === 200,
      'sectors 필드가 존재': (r) => {
        try {
          const data = JSON.parse(r.body);
          return Array.isArray(data.sectors);
        } catch {
          return false;
        }
      },
      'sectors 리스트가 0개 이상': (r) => {
        const data = JSON.parse(r.body);
        return data.sectors.length >= 0;
      },
    });
  });
}
