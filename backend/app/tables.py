from sqlalchemy import Table, Column, Integer, String, MetaData

# ----- SQALchemy Core : Table 스펙 (필요한 칼럼만) -----

metadata = MetaData()
dishes = Table(
    "dishes",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String, nullable=False),
    Column("canonical_dish_key", String, nullable=True),
)
