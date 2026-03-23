import httpx
from config import config

class BackendClient:
    def __init__(self):
        self.base_url = config.lms_api_base_url
        self.key = config.lms_api_key

    def get_headers(self):
        return {"Authorization": f"Bearer {self.key}"}

    async def get_items(self):
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{self.base_url}/items/", headers=self.get_headers())
                response.raise_for_status()
                return response.json()
            except httpx.ConnectError as e:
                raise Exception(f"Backend error: connection refused ({self.base_url}). Check that the services are running.")
            except httpx.HTTPStatusError as e:
                raise Exception(f"Backend error: HTTP {e.response.status_code} {e.response.reason_phrase}. The backend service may be down.")
            except Exception as e:
                raise Exception(f"Backend error: {str(e)}")

    async def get_scores(self, lab: str):
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{self.base_url}/analytics/pass-rates?lab={lab}", headers=self.get_headers())
                response.raise_for_status()
                return response.json()
            except httpx.ConnectError as e:
                raise Exception(f"Backend error: connection refused ({self.base_url}). Check that the services are running.")
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 404:
                    raise Exception(f"Lab {lab} not found.")
                raise Exception(f"Backend error: HTTP {e.response.status_code} {e.response.reason_phrase}. The backend service may be down.")
            except Exception as e:
                raise Exception(f"Backend error: {str(e)}")

backend_client = BackendClient()
