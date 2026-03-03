from __future__ import annotations

import os
import time
from dataclasses import dataclass
from typing import Optional

import httpx
from openai import OpenAI

from .types import LLMResult, LLMUsage


@dataclass
class OpenAIProviderConfig:
    model: str
    api_key: Optional[str] = None
    timeout_s: float = 30.0
    max_retries: int = 3


class OpenAIProvider:
    def __init__(self, cfg: OpenAIProviderConfig) -> None:
        self.cfg = cfg
        self.client = OpenAI(
            api_key=cfg.api_key or os.environ.get("OPENAI_API_KEY"),
            timeout=httpx.Timeout(cfg.timeout_s),
            max_retries=cfg.max_retries,
        )

    def generate(
        self,
        prompt: str,
        system: str,
        temperature: float = 0.2,
        max_tokens: int = 512,
    ) -> LLMResult:
        t0 = time.perf_counter()

        resp = self.client.responses.create(
            model=self.cfg.model,
            instructions=system,
            input=prompt,
            temperature=temperature,
            max_output_tokens=max_tokens,
        )

        latency_ms = int((time.perf_counter() - t0) * 1000)

        text = (resp.output_text or "").strip()

        input_tokens = 0
        output_tokens = 0
        if getattr(resp, "usage", None):
            input_tokens = int(getattr(resp.usage, "input_tokens", 0) or 0)
            output_tokens = int(getattr(resp.usage, "output_tokens", 0) or 0)

        return LLMResult(
            text=text,
            usage=LLMUsage(input_tokens=input_tokens, output_tokens=output_tokens),
            latency_ms=latency_ms,
            cost_usd=None,
        )