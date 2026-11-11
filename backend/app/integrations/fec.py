"""OpenFEC adapter (https://api.open.fec.gov/developers/). Requires an api.data.gov key."""
from app.integrations.base import AdapterError, BaseAdapter


class FECAdapter(BaseAdapter):
    name = "OpenFEC"
    base_url = "https://api.open.fec.gov/v1"
    docs_url = "https://api.open.fec.gov/developers/"

    def search_candidates(self, query: str, page: int = 1, per_page: int = 10) -> dict:
        data = self.get_json("/candidates/search/", {"q": query, "page": page, "per_page": min(per_page, 50)})
        results = data.get("results")
        if not isinstance(results, list):
            raise AdapterError("invalid_response", "OpenFEC response did not include results.")
        items = []
        for r in results:
            cid = r.get("candidate_id")
            if not cid:
                continue
            items.append({
                "candidate_id": cid,
                "name": r.get("name"),
                "party": r.get("party_full"),
                "office": r.get("office_full"),
                "state": r.get("state"),
                "district": r.get("district"),
                "election_years": r.get("election_years") or [],
                "source_url": f"https://www.fec.gov/data/candidate/{cid}/",
            })
        pag = data.get("pagination") or {}
        return {"items": items, "page": pag.get("page", page), "pages": pag.get("pages", 1),
                "count": pag.get("count", len(items)),
                "provenance": self.provenance(f"{self.base_url}/candidates/search/")}
