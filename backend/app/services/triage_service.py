import logging
from datetime import datetime, timezone

from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.core.config import settings
from app.integrations.gemini import analyze_ticket
from app.models.ticket import Ticket
from app.models.ticket_triage import TicketTriage


logger = logging.getLogger(__name__)


ALLOWED_CATEGORIES = {
    "hardware",
    "software",
    "network",
    "access",
    "other",
}

ALLOWED_PRIORITIES = {
    "low",
    "medium",
    "high",
    "critical",
}

ALLOWED_REVIEW_STATUSES = {"accepted", "rejected"}


class TriageProviderError(Exception):
    """Erro ao comunicar com o provedor de IA."""


def create_ticket_triage(
    db: Session,
    ticket: Ticket,
) -> TicketTriage:
    """
    Analisa um chamado com IA e armazena a sugestão,
    sem modificar os dados originais do chamado.
    """

    try:
        result = analyze_ticket(
            title=ticket.title,
            description=ticket.description,
        )
    except Exception as exc:
        logger.exception("Falha ao solicitar análise ao Gemini.")
        raise TriageProviderError(
            "O serviço de IA está temporariamente indisponível."
        ) from exc

    if not isinstance(result, dict):
        raise ValueError("A IA retornou uma resposta inválida.")

    category = result.get("category")
    priority = result.get("priority")
    justification = result.get("justification")

    if not isinstance(category, str) or category not in ALLOWED_CATEGORIES:
        raise ValueError("A IA retornou uma categoria inválida.")

    if not isinstance(priority, str) or priority not in ALLOWED_PRIORITIES:
        raise ValueError("A IA retornou uma prioridade inválida.")

    if not isinstance(justification, str) or not justification.strip():
        raise ValueError("A IA retornou uma justificativa inválida.")

    triage = TicketTriage(
        ticket_id=ticket.id,
        organization_id=ticket.organization_id,
        suggested_category=category,
        suggested_priority=priority,
        justification=justification.strip(),
        model=settings.GEMINI_MODEL,
        review_status="pending",
    )

    try:
        db.add(triage)
        db.commit()
        db.refresh(triage)
    except Exception:
        db.rollback()
        raise

    return triage


def list_ticket_triages(
    db: Session,
    ticket_id: int,
    organization_id: int,
) -> list[TicketTriage] | None:

    ticket = (
        db.query(Ticket)
        .filter(
            Ticket.id == ticket_id,
            Ticket.organization_id == organization_id,
        )
        .first()
    )

    if ticket is None:
        return None

    return (
        db.query(TicketTriage)
        .filter(
            TicketTriage.ticket_id == ticket_id,
            TicketTriage.organization_id == organization_id,
        )
        .order_by(desc(TicketTriage.created_at))
        .all()
    )


def review_ticket_triage(
    db: Session,
    ticket_id: int,
    triage_id: int,
    organization_id: int,
    reviewer_id: int,
    review_status: str,
) -> TicketTriage | None:

    if review_status not in ALLOWED_REVIEW_STATUSES:
        raise ValueError("Status de revisão inválido.")

    ticket = (
        db.query(Ticket)
        .filter(
            Ticket.id == ticket_id,
            Ticket.organization_id == organization_id,
        )
        .first()
    )

    if ticket is None:
        return None

    triage = (
        db.query(TicketTriage)
        .filter(
            TicketTriage.id == triage_id,
            TicketTriage.ticket_id == ticket_id,
            TicketTriage.organization_id == organization_id,
        )
        .first()
    )

    if triage is None:
        return None

    if triage.review_status != "pending":
        raise ValueError("Esta análise já foi revisada.")

    if review_status == "accepted":
        ticket.category = triage.suggested_category
        ticket.priority = triage.suggested_priority

    triage.review_status = review_status
    triage.reviewed_by = reviewer_id
    triage.reviewed_at = datetime.now(timezone.utc)

    try:
        db.commit()
        db.refresh(triage)
    except Exception:
        db.rollback()
        raise

    return triage