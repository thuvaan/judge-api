from fastapi import FastAPI
from pydantic import BaseModel
import subprocess
import uuid
import os

app = FastAPI()

class CodeRequest(BaseModel):
	code: str
	input: str = ""
	expected_output: str = ""

@app.post("/run")
def run_code(req: CodeRequest):
	file_id = str(uuid.uuid4())
	filename = f"{file_id}.py"

	try:
		# ghi file code
		with open(filename, "w", encoding="utf-8") as f:
			f.write(req.code)

		# chạy code
		result = subprocess.run(
			["python", filename],
			input=req.input,
			capture_output=True,
			text=True,
			timeout=2
		)

		# ===== LẤY OUTPUT =====
		output = result.stdout.strip()
		expected = req.expected_output.strip()

		# ===== NORMALIZE (không phân biệt hoa thường + bỏ space dư) =====
		def normalize(s):
			return " ".join(s.lower().split())

		# ===== SO SÁNH =====
		if normalize(output) == normalize(expected):
			score = 10
		else:
			score = 0

		return {
			"output": output,
			"score": score,
			"status": "OK"
		}

	except subprocess.TimeoutExpired:
		return {
			"output": "",
			"score": 0,
			"status": "TLE"
		}

	except Exception as e:
		return {
			"output": str(e),
			"score": 0,
			"status": "ERROR"
		}

	finally:
		if os.path.exists(filename):
			os.remove(filename)
