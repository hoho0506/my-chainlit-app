# run.py
import os
import subprocess

port = os.getenv("PORT", "8000")  # Render가 자동 주입함
subprocess.run(["chainlit", "run", "main.py", "-h", "0.0.0.0", "-p", port])