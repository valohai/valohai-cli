import hashlib
from typing import Optional, Set

from valohai_cli.api import request
from valohai_cli.utils import force_bytes


class LogManager:
    def __init__(self, execution: dict) -> None:
        self.execution: dict = execution
        self.execution_url: str = execution["url"]
        self.events_url: str = f"{self.execution_url}events/"
        self.seen_events: Set[str] = set()

    def update_execution(self) -> dict:
        self.execution = request("get", self.execution_url).json()
        return self.execution

    def fetch_events(self, limit: Optional[int] = None) -> dict:
        params = {}
        if limit is not None:
            params["limit"] = limit
        events_response = request("get", self.events_url, params=params).json()
        filtered_events = []
        for event in events_response.get("events", ()):
            event_id = hashlib.md5(
                force_bytes("+".join((event["stream"], event["time"], event["message"]))),
            ).hexdigest()
            if event_id in self.seen_events:
                continue
            self.seen_events.add(event_id)
            filtered_events.append(event)
        return {
            "truncated": events_response.get("truncated", False),
            "total": events_response.get("total"),
            "events": filtered_events,
        }
