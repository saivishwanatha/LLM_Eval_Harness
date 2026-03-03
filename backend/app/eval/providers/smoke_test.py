from __future__ import annotations

from app.eval.providers.openai_provider import OpenAIProvider, OpenAIProviderConfig
from app.eval.providers.anthropic_provider import AnthropicProvider, AnthropicProviderConfig


def main() -> None:
    system = "Answer in one short sentence."
    prompt = "What is 2 + 2?"

    # OpenAI
    p = OpenAIProvider(OpenAIProviderConfig(model="gpt-4.1-mini"))
    r = p.generate(prompt=prompt, system=system)
    print("openai:", r.text, r.usage, r.latency_ms)

    # Anthropic
    # p = AnthropicProvider(AnthropicProviderConfig(model="claude-3-5-sonnet-latest"))
    # r = p.generate(prompt=prompt, system=system)
    # print("anthropic:", r.text, r.usage, r.latency_ms)


if __name__ == "__main__":
    main()