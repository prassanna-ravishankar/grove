"""Claude API access for labels and split proposals, with spend accounting.

The key comes from ~/.repowire/frontier.env and is never printed.
"""

import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import anthropic
from anthropic.types.messages.batch_create_params import Request

from grove.io import append_jsonl

ENV = Path.home() / ".repowire" / "frontier.env"
MODEL = "claude-opus-5-5"
# USD per token: input, output, cache write (5 min), cache read.
PRICE = {"input": 4e-6, "output": 20e-6, "cache_write": 5e-6, "cache_read": 0.2e-6}


def client() -> anthropic.Anthropic:
    env = dict(line.split("=", 1) for line in ENV.read_text().splitlines() if "=" in line and not line.startswith("#"))
    headers = {"anthropic-workspace-id": env["ANTHROPIC_WORKSPACE_ID"].strip()} if env.get("ANTHROPIC_WORKSPACE_ID", "").strip() else {}
    return anthropic.Anthropic(api_key=env["ANTHROPIC_API_KEY"].strip(), default_headers=headers)


def cost(usage) -> float:
    return (
        usage.input_tokens * PRICE["input"]
        + usage.output_tokens * PRICE["output"]
        + (usage.cache_creation_input_tokens or 0) * PRICE["cache_write"]
        + (usage.cache_read_input_tokens or 0) * PRICE["cache_read"]
    )


def json_format(schema: dict) -> dict:
    return {"format": {"type": "json_schema", "schema": schema}}


def parse(message) -> dict | None:
    if message.stop_reason != "end_turn":
        return None
    return json.loads(next(b.text for b in message.content if b.type == "text"))


def run(c: anthropic.Anthropic, requests: list[Request], tag: str, workers: int = 4) -> dict[str, dict | None]:
    """Send {custom_id, params} requests; the first alone so the rest read its cache."""
    out, spend = {}, []

    def one(req: Request) -> None:
        try:
            message = c.messages.create(**req["params"])
        except anthropic.APIStatusError as err:
            print(f"{req['custom_id']}: {err.status_code}")
            out[req["custom_id"]] = None
            return
        spend.append(cost(message.usage))
        out[req["custom_id"]] = parse(message)

    one(requests[0])
    with ThreadPoolExecutor(workers) as pool:
        list(pool.map(one, requests[1:]))
    append_jsonl("frontier_spend.jsonl", {"tag": tag, "requests": len(requests), "usd": round(sum(spend), 4)})
    print(f"{tag}: {len(requests)} requests, ${sum(spend):.3f}, {sum(v is None for v in out.values())} failed")
    return out
