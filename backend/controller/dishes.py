from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import (
    Table,
    Column,
    Integer,
    String,
    MetaData,
    select,
    insert,
    update,
    delete,
)
from app.deps import get_db
from app.tables import dishes

router = APIRouter(
    prefix="/dishes", tags=["dishes"], responses={404: {"description": "Not found"}}
)


# ----- 요청 스키마 -----
class DishIn(BaseModel):
    name: str
    canonical_dish_key: Optional[str] = None


class DishUpdate(BaseModel):
    name: Optional[str] = None
    canonical_dish_key: Optional[str] = None


# ----- CRUD -----
# 이름 부분 검색
@router.get("", response_model=List[dict])
def search_dishes(q: str = Query(""), limit: int = 50, db: Session = Depends(get_db)):
    stmt = (
        select(dishes.c.id, dishes.c.name, dishes.c.canonical_dish_key)
        .where(dishes.c.name.like(f"%{q}%"))
        .order_by(dishes.c.id.asc())
        .limit(limit)
    )
    rows = db.execute(stmt).mappings().all()
    return [dict(r) for r in rows]


# 단건 조회
@router.get("/{dish_id}", response_model=dict)
def get_dish(dish_id: int, db: Session = Depends(get_db)):
    stmt = select(dishes).where(dishes.c.id == dish_id)
    r = db.execute(stmt).mappings().first()
    if not r:
        raise HTTPException(status_code=404, detail="Not found")
    return dict(r)


# 추가
@router.post("", response_model=dict)
def create_dish(payload: DishIn, db: Session = Depends(get_db)):
    stmt = (
        insert(dishes)
        .values(
            name=payload.name.strip(),
            canonical_dish_key=(
                payload.canonical_dish_key.strip()
                if payload.canonical_dish_key
                else None
            ),
        )
        .returning(dishes.c.id, dishes.c.name, dishes.c.canonical_dish_key)
    )
    r = db.execute(stmt).mappings().first()
    db.commit()
    return dict(r)


# 수정
@router.patch("/{dish_id}", response_model=dict)
def update_dish(dish_id: int, payload: DishUpdate, db: Session = Depends(get_db)):
    vals = {}
    if payload.name is not None:
        vals["name"] = payload.name.strip()
    if payload.canonical_dish_key is not None:
        vals["canonical_dish_key"] = payload.canonical_dish_key
    if not vals:
        raise HTTPException(status_code=400, detail="No fields to update")

    stmt = (
        update(dishes)
        .where(dishes.c.id == dish_id)
        .values(**vals)
        .returning(dishes.c.id, dishes.c.name, dishes.c.canonical_dish_key)
    )

    r = db.execute(stmt).mappings().first()
    if not r:
        raise HTTPException(status_code=404, detail="Not found")
    db.commit()
    return dict(r)


# 삭제
@router.delete("/{dish_id}", response_model=dict)
def delete_dish(dish_id: int, db: Session = Depends(get_db)):
    stmt = delete(dishes).where(dishes.c.id == dish_id).returning(dishes.c.id)
    r = db.execute(stmt).first()
    db.commit()
    if not r:
        raise HTTPException(status_code=404, detail="Not found")
    return {"deleted": dish_id}
