"""LLM provider abstraction with automatic failover."""

import json
import logging
from typing import Any

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

class LLMError(Exception):
    pass


async def generate_json(prompt: str, schema: dict[str, Any], system_prompt: str = "") -> dict:
    """
    Generate JSON from LLM matching the provided schema.
    Tries Gemini -> Groq -> Ollama.
    """
    errors = []

    # 1. Try Gemini API
    if settings.gemini_api_key:
        try:
            return await _call_gemini(prompt, schema, system_prompt)
        except Exception as e:
            logger.warning(f"Gemini failed: {e}")
            errors.append(f"Gemini: {e}")

    # 2. Try Groq API
    if settings.groq_api_key:
        try:
            return await _call_groq(prompt, schema, system_prompt)
        except Exception as e:
            logger.warning(f"Groq failed: {e}")
            errors.append(f"Groq: {e}")

    # 3. Try local Ollama
    if settings.ollama_base_url:
        try:
            return await _call_ollama(prompt, schema, system_prompt)
        except Exception as e:
            logger.warning(f"Ollama failed: {e}")
            errors.append(f"Ollama: {e}")

    raise LLMError(f"All LLM providers failed: {errors}")


async def _call_gemini(prompt: str, schema: dict, system_prompt: str) -> dict:
    import google.generativeai as genai
    
    genai.configure(api_key=settings.gemini_api_key)
    # Using flash model for speed
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    full_prompt = f"{system_prompt}\n\n{prompt}\n\nRespond ONLY with valid JSON matching this schema:\n{json.dumps(schema)}"
    
    response = await model.generate_content_async(
        full_prompt,
        generation_config=genai.types.GenerationConfig(
            response_mime_type="application/json",
        ),
    )
    
    if not response.text:
        raise LLMError("Empty response from Gemini")
        
    return json.loads(response.text)


async def _call_groq(prompt: str, schema: dict, system_prompt: str) -> dict:
    from groq import AsyncGroq
    client = AsyncGroq(api_key=settings.groq_api_key)
    
    full_prompt = f"{prompt}\n\nRespond ONLY with valid JSON matching this schema:\n{json.dumps(schema)}"
    
    chat_completion = await client.chat.completions.create(
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": full_prompt}
        ],
        model="llama3-8b-8192",
        response_format={"type": "json_object"},
    )
    
    content = chat_completion.choices[0].message.content
    if not content:
        raise LLMError("Empty response from Groq")
        
    return json.loads(content)


async def _call_ollama(prompt: str, schema: dict, system_prompt: str) -> dict:
    full_prompt = f"{prompt}\n\nRespond ONLY with valid JSON matching this schema:\n{json.dumps(schema)}"
    
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{settings.ollama_base_url}/api/chat",
            json={
                "model": "qwen2.5:1.5b", # Fast small model default
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": full_prompt}
                ],
                "format": "json",
                "stream": False,
                "options": {
                    "temperature": 0.2
                }
            },
            timeout=120.0
        )
        resp.raise_for_status()
        data = resp.json()
        content = data.get("message", {}).get("content", "")
        
        if not content:
            raise LLMError("Empty response from Ollama")
            
        return json.loads(content)
