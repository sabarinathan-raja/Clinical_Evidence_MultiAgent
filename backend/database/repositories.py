
from sqlalchemy.orm import Session
from sqlalchemy import select, desc

from backend.database.models import (
    User, ClinicalCase, Document, Evidence,
    WorkflowRun, Review, AuditLog
)


class UserRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(self, **kwargs):
        user = User(**kwargs)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def get_by_id(self, user_id):
        return self.db.get(User, user_id)

    def get_by_email(self, email):
        return self.db.scalar(
            select(User).where(User.email == email)
        )


class CaseRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(self, **kwargs):
        case = ClinicalCase(**kwargs)
        self.db.add(case)
        self.db.commit()
        self.db.refresh(case)
        return case

    def get(self, case_id):
        return self.db.get(ClinicalCase, case_id)

    def list_by_user(self, user_id):
        return list(
            self.db.scalars(
                select(ClinicalCase)
                .where(ClinicalCase.created_by == user_id)
                .order_by(desc(ClinicalCase.created_at))
            ).all()
        )

    def update(self, case_id, **kwargs):
        case = self.get(case_id)

        if case is None:
            return None

        for key, value in kwargs.items():
            if hasattr(case, key) and key not in {"id", "created_by"}:
                setattr(case, key, value)

        self.db.commit()
        self.db.refresh(case)
        return case

    def delete(self, case_id):
        case = self.get(case_id)

        if case is None:
            return False

        self.db.delete(case)
        self.db.commit()
        return True


class DocumentRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(self, **kwargs):
        document = Document(**kwargs)
        self.db.add(document)
        self.db.commit()
        self.db.refresh(document)
        return document

    def get(self, document_id):
        return self.db.get(Document, document_id)

    def list_by_case(self, case_id):
        return list(
            self.db.scalars(
                select(Document)
                .where(Document.case_id == case_id)
            ).all()
        )


class EvidenceRepository:

    def __init__(self, db: Session):
        self.db = db

    def create_many(self, items):
        records = [Evidence(**item) for item in items]
        self.db.add_all(records)
        self.db.commit()
        return records

    def list_by_case(self, case_id):
        return list(
            self.db.scalars(
                select(Evidence)
                .where(Evidence.case_id == case_id)
                .order_by(desc(Evidence.relevance_score))
            ).all()
        )

class WorkflowRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(self, **kwargs):
        workflow = WorkflowRun(**kwargs)
        self.db.add(workflow)
        self.db.commit()
        self.db.refresh(workflow)
        return workflow

    def get(self, workflow_id):
        return self.db.get(WorkflowRun, workflow_id)

    def list_by_user(self, user_id):
        return list(
            self.db.scalars(
                select(WorkflowRun)
                .join(
                    ClinicalCase,
                    WorkflowRun.case_id == ClinicalCase.id
                )
                .where(
                    ClinicalCase.created_by == user_id
                )
                .order_by(desc(WorkflowRun.started_at))
            ).all()
        )

    def list_all(self):
        return list(
            self.db.scalars(
                select(WorkflowRun)
                .order_by(desc(WorkflowRun.started_at))
            ).all()
        )

    def update(self, workflow_id, **kwargs):
        workflow = self.get(workflow_id)

        if workflow is None:
            return None

        for key, value in kwargs.items():
            if hasattr(workflow, key) and key not in {"id", "case_id"}:
                setattr(workflow, key, value)

        self.db.commit()
        self.db.refresh(workflow)
        return workflow

class ReviewRepository:

    def __init__(self, db: Session):
        self.db = db

    def create(self, **kwargs):
        review = Review(**kwargs)
        self.db.add(review)
        self.db.commit()
        self.db.refresh(review)
        return review

    def list_by_case(self, case_id):
        return list(
            self.db.scalars(
                select(Review)
                .where(Review.case_id == case_id)
                .order_by(desc(Review.reviewed_at))
            ).all()
        )


class AuditRepository:

    def __init__(self, db: Session):
        self.db = db

    def log(self, **kwargs):
        record = AuditLog(**kwargs)
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def list_by_case(self, case_id):
        return list(
            self.db.scalars(
                select(AuditLog)
                .where(AuditLog.case_id == case_id)
                .order_by(desc(AuditLog.created_at))
            ).all()
        )
