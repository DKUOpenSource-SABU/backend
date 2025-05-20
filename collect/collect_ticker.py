import subprocess
import os

def download_etf_csv():
    script_path = os.path.abspath("nasdaq-download.js")
    result = subprocess.run(["node", script_path],
                             capture_output=True,
                             text=True)

    print(result.stdout)
    if result.returncode != 0:
        print("❌ 오류 발생:")
        print(result.stderr)
