from __future__ import annotations

import os
import time
from dataclasses import dataclass
from typing import Optional

import httpx
from anthropic import Anthropic

from .types import LLMResult, LLMUsage


@dataclass
class AnthropicProviderConfig:
    model: str
    api_key: Optional[str] = None
    timeout_s: float = 30.0
    max_retries: int = 3


class AnthropicProvider:
    def __init__(self, cfg: AnthropicProviderConfig) -> None:
        self.cfg = cfg
        self.client = Anthropic(
            api_key=cfg.api_key or os.environ.get("ANTHROPIC_API_KEY"),
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

        msg = self.client.messages.create(
            model=self.cfg.model,
            system=system,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=max_tokens,
        )

        latency_ms = int((time.perf_counter() - t0) * 1000)

        parts: list[str] = []
        for block in getattr(msg, "content", []) or []:
            if getattr(block, "type", None) == "text":
                parts.append(getattr(block, "text", "") or "")
        text = "".join(parts).strip()

        input_tokens = 0
        output_tokens = 0
        if getattr(msg, "usage", None):
            input_tokens = int(getattr(msg.usage, "input_tokens", 0) or 0)
            output_tokens = int(getattr(msg.usage, "output_tokens", 0) or 0)

        return LLMResult(
            text=text,
            usage=LLMUsage(input_tokens=input_tokens, output_tokens=output_tokens),
            latency_ms=latency_ms,
            cost_usd=None,
        )