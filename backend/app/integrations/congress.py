"""Congress.gov API adapter (https://api.congress.gov/). Requires an api.data.gov key."""
from app.integrations.base import AdapterError, BaseAdapter


class CongressAdapter(BaseAdapter):
    name = "Congress.gov"
    base_url = "https://api.congress.gov/v3"
    docs_url = "https://api.congress.gov/"

    def recent_bills(self, congress: int | None = None, limit: int = 10, offset: int = 0) -> dict:
        path = f"/bill/{congress}" if congress else "/bill"
        data = self.get_json(path, {"format": "json", "limit": min(limit, 50), "offset": offset})
        bills = data.get("bills")
        if not isinstance(bills, list):
            raise AdapterError("invalid_response", "Congress.gov response did not include bills.")
        items = []
        for b in bills:
            if not b.get("number") or not b.get("type"):
                continue
            items.append({
                "congress": b.get("congress"),
                "bill_type": b.get("type"),
                "number": b.get("number"),
                "title": b.get("title"),
                "latest_action": (b.get("latestAction") or {}).get("text"),
                "latest_action_date": (b.get("latestAction") or {}).get("actionDate"),
                "api_url": b.get("url"),
            })
        return {"items": items, "provenance": self.provenance(f"{self.base_url}{path}")}
