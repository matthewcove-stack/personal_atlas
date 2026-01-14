from notion_client import Client

from app.config import settings
from app.core.domain import AtlasLink, AtlasNode


class NotionMirrorRepository:
    def __init__(self) -> None:
        self._client = Client(auth=settings.notion_token)
        self._database_id = settings.notion_database_id

    def mirror_node(self, node: AtlasNode, links: list[AtlasLink]) -> None:
        page_id = self._find_existing(node.id)
        properties = {
            "Title": {"title": [{"text": {"content": node.title}}]},
            "Principle": {"rich_text": [{"text": {"content": node.principle}}]},
            "Confidence": {"number": node.confidence},
            "LastVerified": {"date": {"start": str(node.last_verified)}},
            "AtlasId": {"rich_text": [{"text": {"content": node.id}}]},
        }
        if page_id:
            self._client.pages.update(page_id=page_id, properties=properties)
        else:
            self._client.pages.create(
                parent={"database_id": self._database_id},
                properties=properties,
            )

    def _find_existing(self, atlas_id: str) -> str | None:
        response = self._client.databases.query(
            database_id=self._database_id,
            filter={
                "property": "AtlasId",
                "rich_text": {"equals": atlas_id},
            },
        )
        results = response.get("results", [])
        if not results:
            return None
        return results[0]["id"]
