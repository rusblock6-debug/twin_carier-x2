from abc import abstractmethod, ABC
from typing import List, TypeVar, Generic, Type

from sqlalchemy import delete
from sqlalchemy.orm import Session, DeclarativeBase

T = TypeVar('T', bound=DeclarativeBase)


class AbstractDAO(ABC, Generic[T]):
    def __init__(self, db_session: Session):
        self._db = db_session

    @property
    @abstractmethod
    def _model(self) -> Type[T]:
        raise NotImplementedError

    def insert(self, records: List[T]) -> List[int]:
        self._db.add_all(records)
        self._db.commit()

        for record in records:
            self._db.refresh(record)

        return [record.id for record in records]

    def delete_where_in(self, ids: List[int]) -> None:
        self._db.execute(
            delete(self._model)
            .where(
                self._model.id.in_(ids)
            )
        )
        self._db.commit()
