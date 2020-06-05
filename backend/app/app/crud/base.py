from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel

# from sqlalchemy.orm import Session

from app.db.base_class import Base
from app.db import database

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        """
        CRUD object with default methods to Create, Read, Update, Delete (CRUD).

        **Parameters**

        * `model`: A SQLAlchemy model class
        * `schema`: A Pydantic model (schema) class
        """
        self.model = model
        self.table = model.__table__

    async def get(self, id: Any) -> Optional[ModelType]:
        query = self.table.select().where(self.model.id == id)
        data = await database.fetch_one(query=query)
        if not data:
            return None
        return self.model(**data)

    async def get_all(self, *, skip: int = 0, limit: int = 100) -> List[ModelType]:
        query = self.table.select().offset(skip).limit(limit)
        datalist = await database.fetch_all(query=query)
        return [self.model(**data) for data in datalist]

    async def create(self, *, obj_in: Union[CreateSchemaType, Dict[str, Any]]) -> ModelType:
        if isinstance(obj_in, dict):
            obj_in_data = obj_in
        else:
            obj_in_data = obj_in.dict(exclude_unset=True)
        query = self.table.insert().values(**obj_in_data)
        id = await database.execute(query=query)
        return self.model(**{
            "id": id,
            **obj_in_data
        })

    async def update(
        self, *, db_obj: ModelType, obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        update_data = jsonable_encoder(db_obj)
        if isinstance(obj_in, dict):
            update_data.update(obj_in)
        else:
            update_data.update(obj_in.dict(exclude_unset=True))
        query = (
            self.table
            .update()
            .where(db_obj.id == self.table.c.id)
            .values(**update_data)
            .returning(self.table.c.id)
        )
        id = await database.execute(query=query)
        return self.model(**{
            "id": id,
            **update_data
        })

    async def delete(self, *, id: int) -> Any:
        query = self.table.delete().where(id == self.table.c.id)
        return await database.execute(query=query)
