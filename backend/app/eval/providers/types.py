from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Protocol


@dataclass(frozen=True)
class LLMUsage:
    input_tokens: int = 0
    output_tokens: int = 0

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens


@dataclass(frozen=True)
class LLMResult:
    text: str
    usage: LLMUsage
    latency_ms: int
    cost_usd: Optional[float] = None


class LLMProvider(Protocol):
    def generate(
        self,
        prompt: str,
        system: str,
        temperature: float = 0.2,
        max_tokens: int = 512,
    ) -> LLMResult: ...