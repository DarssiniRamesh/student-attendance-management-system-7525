"""
Base CRUD repository for SQLAlchemy models.
"""

from sqlalchemy.orm.session import Session

# PUBLIC_INTERFACE
class BaseRepository:
    """A generic base repository for CRUD operations."""
    def __init__(self, model):
        self.model = model

    # PUBLIC_INTERFACE
    def get(self, db: Session, obj_id: int):
        """Get object by primary key."""
        return db.query(self.model).get(obj_id)

    # PUBLIC_INTERFACE
    def get_all(self, db: Session, skip: int = 0, limit: int = 100):
        """Get all objects with optional skip and limit."""
        return db.query(self.model).offset(skip).limit(limit).all()

    # PUBLIC_INTERFACE
    def create(self, db: Session, obj_in: dict):
        """Create and persist a new object from dict."""
        db_obj = self.model(**obj_in)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    # PUBLIC_INTERFACE
    def update(self, db: Session, db_obj, obj_in: dict):
        """Update db_obj with obj_in and persist."""
        for field, value in obj_in.items():
            setattr(db_obj, field, value)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    # PUBLIC_INTERFACE
    def delete(self, db: Session, db_obj):
        """Delete the given db_obj."""
        db.delete(db_obj)
        db.commit()
        return db_obj
