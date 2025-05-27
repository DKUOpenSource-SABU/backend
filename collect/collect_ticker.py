import subprocess
import os

# NASDAQ ETF 데이터를 다운로드하기 위한 Node.js 스크립트를 실행 함수
# 작성자 : 김태형
def download_etf_csv():
    script_path = os.path.abspath("nasdaq-download.js")
    result = subprocess.run(["node", script_path],
                             capture_output=True,
                             text=True)
    print(result.stdout)
    if result.returncode != 0:
        print("❌ 오류 발생:")
        print(result.stderr)
