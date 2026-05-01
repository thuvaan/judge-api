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
		with open(filename, "w", encoding="utf-8") as f:
			f.write(req.code)

		result = subprocess.run(
			["python", filename],
			input=req.input,
			capture_output=True,
			text=True,
			timeout=2
		)

		output = result.stdout.strip()
		score = 10 if output == req.expected_output.strip() else 0

		return {
			"output": output,
			"score": score,
			"status": "OK"
		}

	except subprocess.TimeoutExpired:
		return {"status": "TLE", "score": 0}

	finally:
		if os.path.exists(filename):
			os.remove(filename)