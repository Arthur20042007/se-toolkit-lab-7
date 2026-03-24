import httpx
from config import config


class BackendClient:
    def __init__(self):
        self.base_url = config.lms_api_base_url
        self.key = config.lms_api_key

    def get_headers(self):
        return {"Authorization": f"Bearer {self.key}"}

    async def _get(self, endpoint: str, params: dict = None):
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}{endpoint}",
                    headers=self.get_headers(),
                    params=params,
                )
                response.raise_for_status()
                return response.json()
            except httpx.ConnectError:
                raise Exception(
                    f"Backend error: connection refused ({self.base_url}). Check that the services are running."
                )
            except httpx.HTTPStatusError as e:
                raise Exception(
                    f"Backend error: HTTP {e.response.status_code} {e.response.reason_phrase}. The backend service may be down."
                )
            except Exception as e:
                raise Exception(f"Backend error: {str(e)}")

    async def _post(self, endpoint: str, json: dict = None):
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}{endpoint}", headers=self.get_headers(), json=json
                )
                response.raise_for_status()
                return response.json()
            except httpx.ConnectError:
                raise Exception(
                    f"Backend error: connection refused ({self.base_url}). Check that the services are running."
                )
            except httpx.HTTPStatusError as e:
                raise Exception(
                    f"Backend error: HTTP {e.response.status_code} {e.response.reason_phrase}. The backend service may be down."
                )
            except Exception as e:
                raise Exception(f"Backend error: {str(e)}")

    async def get_items(self):
        return await self._get("/items/")

    async def get_learners(self):
        return await self._get("/learners/")

    def _normalize_lab(self, lab: str) -> str:
        if not lab:
            return lab
        import re

        # If it's already 'lab-XX' just return it
        if re.match(r"^lab-\d{2}$", lab):
            return lab
        # Try to find a number and format it
        m = re.search(r"\d+", lab)
        if m:
            num = int(m.group())
            return f"lab-{num:02d}"
        return lab

    async def get_scores_distribution(self, lab: str):
        return await self._get(
            "/analytics/scores", params={"lab": self._normalize_lab(lab)}
        )

    async def get_scores(self, lab: str):
        return await self._get(
            "/analytics/pass-rates", params={"lab": self._normalize_lab(lab)}
        )

    async def get_pass_rates(self, lab: str):
        return await self._get(
            "/analytics/pass-rates", params={"lab": self._normalize_lab(lab)}
        )

    async def get_timeline(self, lab: str):
        return await self._get(
            "/analytics/timeline", params={"lab": self._normalize_lab(lab)}
        )

    async def get_groups(self, lab: str):
        return await self._get(
            "/analytics/groups", params={"lab": self._normalize_lab(lab)}
        )

    async def get_top_learners(self, lab: str, limit: int = 5):
        return await self._get(
            "/analytics/top-learners",
            params={"lab": self._normalize_lab(lab), "limit": limit},
        )

    async def get_completion_rate(self, lab: str):
        return await self._get(
            "/analytics/completion-rate", params={"lab": self._normalize_lab(lab)}
        )

    async def trigger_sync(self):
        return await self._post("/pipeline/sync", json={})


backend_client = BackendClient()
