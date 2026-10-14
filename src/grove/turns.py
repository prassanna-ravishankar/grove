"""Inbound orchestrator turns from a copy of the Repowire journal (state.db).

Each delivered message to an orchestrator peer is logged as a user chat_turn
whose text is the client's wrapper around the daemon's delivered text, which
starts with the recorded [repowire recall] block.
"""

import html
import re
import sqlite3
from dataclasses import dataclass
from pathlib import Path

TURNS_SQL = """
select event_id, timestamp, session_id, peer_name, peer_id, json_extract(payload_json, '$.text')
from events
where type = 'chat_turn' and timestamp >= ? and peer_name like 'orchestrator%'
  and json_extract(payload_json, '$.role') = 'user'
  and payload_json like '%[repowire recall]%'
order by timestamp
"""
PEER_MESSAGE_RE = re.compile(r'<peer-message from="@([^"]+)" to="@([^"]+)" type="([^"]+)"')
TELEGRAM_RE = re.compile(r"sent a message: @(\S+) → @(\S+): ")
LABEL_RE = re.compile(r"(?:^|\s)- (comms\.md|projects\.md|memory/[^\s:]+\.md): ")
BODY_END_RE = re.compile(r"\s*(?:↳ ack\(|</peer-message>)")


@dataclass
class Turn:
    id: str
    ts: str
    session: str
    target: str
    target_id: str
    sender: str
    sender_id: str
    kind: str
    body: str
    recorded: list[str]  # labels in the recorded recall block, in order


def open_readonly(path: Path) -> sqlite3.Connection:
    return sqlite3.connect(f"file:{path}?immutable=1", uri=True)


def load_turns(db: Path, since: str) -> list[Turn]:
    conn = open_readonly(db)
    ids = dict(conn.execute("select peer_name, peer_id from events where peer_name is not null and peer_id is not null group by peer_name"))
    turns = []
    for event_id, ts, session, target, target_id, text in conn.execute(TURNS_SQL, (since,)):
        text = html.unescape(text)
        if m := PEER_MESSAGE_RE.search(text):
            sender, kind = m.group(1), m.group(3)
        elif m := TELEGRAM_RE.search(text):
            sender, kind = m.group(1), "notify"
        else:
            raise ValueError(f"unrecognised wrapper in {event_id}")
        start, end = text.index("[repowire recall]"), text.index("[/repowire recall]")
        block = text[start:end]
        rest = text[end + len("[/repowire recall]") :]
        body = rest[: m2.start()] if (m2 := BODY_END_RE.search(rest)) else rest
        turns.append(Turn(event_id, ts, session or "", target, target_id, sender, ids.get(sender, ""), kind, body.strip(), LABEL_RE.findall(block)))
    return turns
