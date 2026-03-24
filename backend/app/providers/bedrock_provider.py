"""AWS Bedrock provider — Claude, Llama, Titan via AWS Bedrock Runtime."""

from __future__ import annotations

import json
import time
from typing import AsyncIterator

import boto3

from app.providers.base import LLMMessage, LLMProvider, LLMResponse


class BedrockProvider(LLMProvider):
    provider_name = "bedrock"

    def __init__(
        self,
        model_id: str,
        region: str = "us-east-1",
        access_key: str | None = None,
        secret_key: str | None = None,
        profile: str | None = None,
    ) -> None:
        self.model_id = model_id
        session_kwargs: dict = {"region_name": region}
        if access_key and secret_key:
            session_kwargs["aws_access_key_id"] = access_key
            session_kwargs["aws_secret_access_key"] = secret_key
        elif profile:
            session_kwargs["profile_name"] = profile
        session = boto3.Session(**session_kwargs)
        self._client = session.client("bedrock-runtime")

    async def generate(
        self,
        messages: list[LLMMessage],
        *,
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> LLMResponse:
        system_prompt, chat_messages = self._split_messages(messages)
        body = self._build_body(system_prompt, chat_messages, temperature, max_tokens)

        import asyncio
        resp = await asyncio.to_thread(
            self._client.invoke_model,
            modelId=self.model_id,
            contentType="application/json",
            accept="application/json",
            body=json.dumps(body),
        )
        result = json.loads(resp["body"].read())
        return self._parse_response(result)

    async def stream(
        self,
        messages: list[LLMMessage],
        *,
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> AsyncIterator[str]:
        system_prompt, chat_messages = self._split_messages(messages)
        body = self._build_body(system_prompt, chat_messages, temperature, max_tokens)

        import asyncio
        resp = await asyncio.to_thread(
            self._client.invoke_model_with_response_stream,
            modelId=self.model_id,
            contentType="application/json",
            accept="application/json",
            body=json.dumps(body),
        )
        stream = resp.get("body")
        if stream:
            for event in stream:
                chunk = json.loads(event["chunk"]["bytes"])
                text = self._extract_stream_text(chunk)
                if text:
                    yield text

    async def health_check(self) -> tuple[bool, float]:
        start = time.perf_counter()
        try:
            import asyncio
            body = self._build_body("", [{"role": "user", "content": "ping"}], 0.1, 5)
            await asyncio.to_thread(
                self._client.invoke_model,
                modelId=self.model_id,
                contentType="application/json",
                accept="application/json",
                body=json.dumps(body),
            )
            elapsed = (time.perf_counter() - start) * 1000
            return True, elapsed
        except Exception:
            elapsed = (time.perf_counter() - start) * 1000
            return False, elapsed

    # ── Internal helpers ──

    @staticmethod
    def _split_messages(messages: list[LLMMessage]) -> tuple[str, list[dict]]:
        system_parts: list[str] = []
        chat: list[dict] = []
        for m in messages:
            if m.role == "system":
                system_parts.append(m.content)
            else:
                chat.append({"role": m.role, "content": m.content})
        return "\n".join(system_parts), chat

    def _build_body(
        self,
        system: str,
        messages: list[dict],
        temperature: float,
        max_tokens: int,
    ) -> dict:
        """Build the Converse-style request body for Bedrock models."""
        # Anthropic Claude on Bedrock uses the Messages API format
        if "anthropic" in self.model_id or "claude" in self.model_id:
            body: dict = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": max_tokens,
                "temperature": temperature,
                "messages": messages,
            }
            if system:
                body["system"] = system
            return body

        # Amazon Titan / Meta Llama — use generic prompt format
        prompt = ""
        if system:
            prompt += f"System: {system}\n\n"
        for m in messages:
            role_label = "Human" if m["role"] == "user" else "Assistant"
            prompt += f"{role_label}: {m['content']}\n"
        prompt += "Assistant:"

        if "titan" in self.model_id.lower():
            return {
                "inputText": prompt,
                "textGenerationConfig": {
                    "maxTokenCount": max_tokens,
                    "temperature": temperature,
                },
            }
        # Meta Llama models on Bedrock
        return {
            "prompt": prompt,
            "max_gen_len": max_tokens,
            "temperature": temperature,
        }

    def _parse_response(self, result: dict) -> LLMResponse:
        """Parse response from different model families."""
        if "content" in result:
            # Anthropic Claude format
            text = result["content"][0]["text"] if result["content"] else ""
            usage = result.get("usage", {})
            return LLMResponse(
                content=text,
                model=self.model_id,
                provider=self.provider_name,
                prompt_tokens=usage.get("input_tokens", 0),
                completion_tokens=usage.get("output_tokens", 0),
            )
        if "results" in result:
            # Amazon Titan format
            text = result["results"][0].get("outputText", "")
        elif "generation" in result:
            # Meta Llama format
            text = result["generation"]
        else:
            text = str(result)
        return LLMResponse(
            content=text,
            model=self.model_id,
            provider=self.provider_name,
        )

    def _extract_stream_text(self, chunk: dict) -> str:
        """Extract text from a streaming chunk across model families."""
        if "delta" in chunk:
            return chunk["delta"].get("text", "")
        if "outputText" in chunk:
            return chunk["outputText"]
        if "generation" in chunk:
            return chunk["generation"]
        return ""
