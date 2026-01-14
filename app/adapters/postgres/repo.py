from datetime import date

from sqlalchemy import select

from app.adapters.postgres.models import AtlasLinkModel, AtlasNodeModel, AuditLogModel
from app.core.domain import AtlasLink, AtlasNode
from app.db.session import SessionLocal


def _to_domain(node: AtlasNodeModel) -> AtlasNode:
    return AtlasNode(
        id=node.id,
        title=node.title,
        principle=node.principle,
        evidence=node.evidence,
        confidence=node.confidence,
        last_verified=node.last_verified,
        status=node.status,
        idempotency_key=node.idempotency_key,
        created_at=node.created_at,
        updated_at=node.updated_at,
    )


class PostgresAtlasRepository:
    def get_by_idempotency_key(self, idempotency_key: str) -> AtlasNode | None:
        with SessionLocal() as session:
            stmt = select(AtlasNodeModel).where(AtlasNodeModel.idempotency_key == idempotency_key)
            node = session.execute(stmt).scalar_one_or_none()
            return _to_domain(node) if node else None

    def create_staged_node(
        self,
        idempotency_key: str,
        title: str,
        principle: str,
        evidence: str | None,
        confidence: int,
        last_verified: date,
        links: list[AtlasLink],
    ) -> AtlasNode:
        with SessionLocal() as session:
            node = AtlasNodeModel(
                title=title,
                principle=principle,
                evidence=evidence,
                confidence=confidence,
                last_verified=last_verified,
                status="staged",
                idempotency_key=idempotency_key,
            )
            session.add(node)
            session.flush()
            for link in links:
                session.add(
                    AtlasLinkModel(
                        atlas_node_id=node.id,
                        link_type=link.link_type,
                        link_value=link.link_value,
                    )
                )
            session.commit()
            session.refresh(node)
            return _to_domain(node)

    def mark_committed(self, node_id: str) -> AtlasNode:
        with SessionLocal() as session:
            node = session.get(AtlasNodeModel, node_id)
            node.status = "committed"
            session.add(node)
            session.commit()
            session.refresh(node)
            return _to_domain(node)

    def get_by_id(self, node_id: str) -> AtlasNode | None:
        with SessionLocal() as session:
            node = session.get(AtlasNodeModel, node_id)
            return _to_domain(node) if node else None

    def get_links(self, node_id: str) -> list[AtlasLink]:
        with SessionLocal() as session:
            stmt = select(AtlasLinkModel).where(AtlasLinkModel.atlas_node_id == node_id)
            rows = session.execute(stmt).scalars().all()
            return [AtlasLink(link_type=r.link_type, link_value=r.link_value) for r in rows]


class PostgresAuditRepository:
    def log(
        self,
        action: str,
        entity_type: str,
        entity_id: str | None,
        idempotency_key: str,
        status: str,
        message: str | None = None,
    ) -> None:
        with SessionLocal() as session:
            entry = AuditLogModel(
                action=action,
                entity_type=entity_type,
                entity_id=entity_id,
                idempotency_key=idempotency_key,
                status=status,
                message=message,
            )
            session.add(entry)
            session.commit()
