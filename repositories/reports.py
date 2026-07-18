from sqlalchemy.orm import Session

from models.report import Report


def create_report(
    db: Session,
    reporter_id: int,
    lore_id: int,
    reason: str,
    details: str = "",
):
    report = Report(
        reporter_id=reporter_id,
        lore_id=lore_id,
        reason=reason,
        details=details,
    )

    db.add(report)
    db.commit()
    db.refresh(report)

    return report


def get_report_by_id(
    db: Session,
    report_id: int,
):
    return (
        db.query(Report)
        .filter(Report.id == report_id)
        .first()
    )


def list_reports(
    db: Session,
):
    return (
        db.query(Report)
        .order_by(Report.created_at.desc())
        .all()
    )


def get_reports_for_lore(
    db: Session,
    lore_id: int,
):
    return (
        db.query(Report)
        .filter(
            Report.lore_id == lore_id
        )
        .all()
    )


def delete_report(
    db: Session,
    report_id: int,
):
    report = (
        db.query(Report)
        .filter(
            Report.id == report_id
        )
        .first()
    )

    if report:
        db.delete(report)
        db.commit()

    return report