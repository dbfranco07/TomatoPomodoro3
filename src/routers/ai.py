import anthropic
import openai
from fastapi import APIRouter, HTTPException
from schemas import AIRequest

router = APIRouter(prefix="/ai", tags=["ai"])

SYSTEM_PROMPTS = {
    "summarize": "Summarize the following notes or bullet points concisely. Output only the summary.",
    "cleanup":   "Clean up and rewrite the following text. Fix grammar, improve clarity, preserve meaning. Output only the rewritten text.",
    "expand":    "Expand the following rough idea or bullet points into a more complete, coherent thought. Output only the expanded text.",
}


@router.post("/generate")
def ai_generate(body: AIRequest):
    user_msg = body.content.strip()
    if not user_msg:
        raise HTTPException(status_code=400, detail="Content is empty")

    system = body.custom_prompt.strip() if body.action == "custom" else SYSTEM_PROMPTS.get(body.action, "")
    if not system:
        raise HTTPException(status_code=400, detail=f"Unknown action: {body.action}")

    try:
        if body.provider == "anthropic":
            client = anthropic.Anthropic(api_key=body.api_key)
            msg = client.messages.create(
                model=body.model,
                max_tokens=1024,
                system=system,
                messages=[{"role": "user", "content": user_msg}],
            )
            return {"result": msg.content[0].text}
        else:
            # OpenAI-compatible: OpenAI, Ollama, vLLM, etc.
            kwargs: dict = {"api_key": body.api_key or "ollama"}
            if body.base_url:
                kwargs["base_url"] = body.base_url
            client = openai.OpenAI(**kwargs)
            resp = client.chat.completions.create(
                model=body.model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user_msg},
                ],
                max_tokens=1024,
            )
            return {"result": resp.choices[0].message.content}
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))
