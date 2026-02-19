from pydantic import BaseModel
import json
import re


class LogAnalysisOutput(BaseModel):
    summary: str
    root_cause: str
    impact: str
    confidence: str


def extract_json(text):
    """
    Extract JSON block from LLM output.
    Handles extra text before/after JSON.
    """
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        return match.group(0)
    return None


def validate_output(llm_output: str):
    if not llm_output:
        return {
            "summary": "No output",
            "root_cause": "LLM returned empty response",
            "impact": "Unknown",
            "confidence": "LOW",
        }

    json_block = extract_json(llm_output)

    if not json_block:
        return {
            "summary": "Output format error",
            "root_cause": "No JSON detected",
            "impact": "Unknown",
            "confidence": "LOW",
            "raw_output": llm_output,
        }

    try:
        parsed = json.loads(json_block)
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
