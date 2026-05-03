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
    language: str = "python"


@app.post("/run")
def run_code(req: CodeRequest):
    file_id = str(uuid.uuid4())

    try:
        lang = req.language.lower()

        # ===== PYTHON =====
        if lang == "python":
            filename = f"{file_id}.py"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(req.code)

            cmd = ["python", filename]

        # ===== C++ =====
        elif lang == "cpp":
            filename = f"{file_id}.cpp"
            exe_file = f"{file_id}.exe"

            with open(filename, "w", encoding="utf-8") as f:
                f.write(req.code)

            compile = subprocess.run(
                ["g++", filename, "-o", exe_file],
                capture_output=True,
                text=True
            )

            if compile.returncode != 0:
                return {
                    "output": compile.stderr,
                    "score": 0,
                    "status": "COMPILE_ERROR"
                }

            cmd = [exe_file]

        # ===== C# =====
        elif lang == "c#":
            filename = f"{file_id}.cs"
            exe_file = f"{file_id}.exe"

            with open(filename, "w", encoding="utf-8") as f:
                f.write(req.code)

            compile = subprocess.run(
                ["mcs", filename],
                capture_output=True,
                text=True
            )

            if compile.returncode != 0:
                return {
                    "output": compile.stderr,
                    "score": 0,
                    "status": "COMPILE_ERROR"
                }

            cmd = ["mono", exe_file]

        else:
            return {
                "output": "",
                "score": 0,
                "status": "UNSUPPORTED_LANGUAGE"
            }

        # ===== RUN =====
        result = subprocess.run(
            cmd,
            input=req.input,
            capture_output=True,
            text=True,
            timeout=3
        )

        output = result.stdout.strip()
        expected = req.expected_output.strip()

        # ===== NORMALIZE =====
        def normalize(s):
            return " ".join(s.lower().split())

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
        # cleanup
        for ext in [".py", ".cpp", ".cs", ".exe"]:
            file = f"{file_id}{ext}"
            if os.path.exists(file):
                os.remove(file)
