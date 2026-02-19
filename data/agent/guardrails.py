from pydantic import BaseModel
import json


class LogAnalysisOutput(BaseModel):
    summary: str
    root_cause: str
    impact: str
    confidence: str


def extract_json(text):
    text = text.strip()

    try:
        return json.loads(text)
    except:
        pass

    start = text.find("{")
    end = text.rfind("}")

    if start >= 0 and end >= 0:
        try:
            return json.loads(text[start:end+1])
        except:
            return None

    return None


def validate_output(llm_output: str):
    if not llm_output:
        return {
            "summary": "No output",
            "root_cause": "LLM returned empty response",
            "impact": "Unknown",
            "confidence": "LOW",
        }

    parsed = extract_json(llm_output)

    if not parsed:
        return {
            "summary": "Output format error",
            "root_cause": "No JSON detected",
            "impact": "Unknown",
            "confidence": "LOW",
            "raw_output": llm_output,
        }

    try:
        validated = LogAnalysisOutput(**parsed)
        return validated.dict()
    except Exception as e:
        return {
            "summary": "Validation failed",
            "root_cause": str(e),
            "impact": "Unknown",
            "confidence": "LOW",
            "raw_output": llm_output,
        }
