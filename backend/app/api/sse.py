"""Server-Sent Events (SSE) streaming for LangGraph workflow execution."""
import json
from typing import AsyncGenerator
from fastapi.responses import StreamingResponse

async def event_generator() -> AsyncGenerator[str, None]:
    steps = [
        {"node": "parse_document", "status": "completed", "message": "Parsed threat document"},
        {"node": "extract_behaviors", "status": "running", "message": "Extracting adversary actions"},
    ]
    for step in steps:
        yield f"data: {json.dumps(step)}\n\n"

def get_sse_stream():
    return StreamingResponse(event_generator(), media_type="text/event-stream")
