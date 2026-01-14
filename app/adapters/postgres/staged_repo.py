from datetime import datetime, timedelta

from sqlalchemy import select

from app.adapters.postgres.models import StagedWriteModel
from app.config import settings
from app.db.session import SessionLocal


class StagedWriteRepository:
    def create(
        self,
        payload: dict,
        validation_summary: dict,
        idempotency_key: str,
    ) -> StagedWriteModel:
        expires_at = datetime.utcnow() + timedelta(minutes=settings.staged_write_ttl_minutes)
        with SessionLocal() as session:
            staged = StagedWriteModel(
                payload=payload,
                validation_summary=validation_summary,
                idempotency_key=idempotency_key,
                status="staged",
                expires_at=expires_at,
            )
            session.add(staged)
            session.commit()
            session.refresh(staged)
            return staged

    def get(self, staged_id: str) -> StagedWriteModel | None:
        with SessionLocal() as session:
            return session.get(StagedWriteModel, staged_id)

    def get_by_idempotency_key(self, idempotency_key: str) -> StagedWriteModel | None:
        with SessionLocal() as session:
            stmt = select(StagedWriteModel).where(StagedWriteModel.idempotency_key == idempotency_key)
            return session.execute(stmt).scalar_one_or_none()

    def mark_committed(self, staged_id: str, node_id: str, receipt: dict) -> StagedWriteModel:
        with SessionLocal() as session:
            staged = session.get(StagedWriteModel, staged_id)
            staged.status = "committed"
            staged.committed_node_id = node_id
            staged.committed_at = datetime.utcnow()
            staged.receipt = receipt
            session.add(staged)
            session.commit()
            session.refresh(staged)
            return staged
