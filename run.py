import os
import subprocess

# Render가 제공하는 PORT 환경변수를 읽음
port = os.environ.get("PORT", "8000")

# Chainlit 실행 (추가 옵션 없이)
subprocess.run(["chainlit", "run", "main.py"], env={**os.environ, "PORT": port})