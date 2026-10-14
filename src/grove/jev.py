"""Jev System One client, same request shape as repowire daemon-go/routing/jev.go.

The key and model are read from ~/.repowire/config.yaml with yq and never
printed. Every call is appended to data/jev_calls.jsonl with its usage.
"""

import os
import subprocess
from pathlib import Path

import httpx

from grove.io import append_jsonl

CONFIG = Path.home() / ".repowire" / "config.yaml"
BASE_URL = "https://api.typesafe.ai"
# Router paper appendix: 28.8M input tokens for about $1.21.
USD_PER_INPUT_TOKEN = 1.21 / 28.8e6


def _yq(path: str) -> str:
    return subprocess.run(["yq", path, str(CONFIG)], capture_output=True, text=True, check=True).stdout.strip()


class Jev:
    def __init__(self) -> None:
        self.key = os.environ.get("JEV_API_KEY") or _yq(".routing.jev.api_key")
        self.model = _yq(".routing.jev.model")
        self.http = httpx.Client(timeout=60)
        self.input_tokens = 0

    def ask(self, state: dict, questions: dict[str, dict], tag: str = "") -> dict[str, float]:
        """Send one System One request; return the yes probability per question key."""
        body = {"state": state, "model": self.model, "questions": questions}
        for _ in range(4):
            resp = self.http.post(f"{BASE_URL}/v1/systemone", json=body, headers={"Authorization": f"Bearer {self.key}"})
            if resp.status_code < 500 and resp.status_code != 429:
                break
        resp.raise_for_status()
        data = resp.json()
        tokens = (data.get("usage") or {}).get("input_tokens") or 0
        self.input_tokens += tokens
        answers = {k: data["answers"][k]["noul"] for k in questions}
        append_jsonl("jev_calls.jsonl", {"tag": tag, "model": data.get("model"), "input_tokens": tokens, "questions": len(questions)})
        return answers

    @property
    def usd(self) -> float:
        return self.input_tokens * USD_PER_INPUT_TOKEN


def noul(instructions: str, yes: str, no: str) -> dict:
    return {"type": "noul", "instructions": instructions, "criteria": {"true": yes, "false": no}}
