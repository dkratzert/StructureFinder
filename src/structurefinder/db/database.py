import time
from pathlib import Path
from typing import Optional

from sqlalchemy.orm import sessionmaker
import sqlalchemy as sa

from structurefinder.db.mapping import Structure, Residuals


class DB:
    def __init__(self):
        self.engine = None
        self.Session: Optional[sessionmaker] = None
        self.structure_id: Optional[int] = None
        self.structure: Optional[Structure] = None

    def load_database(self, database_file: Path):
        url_object = sa.URL.create("sqlite", database=str(database_file.resolve()))
        self.engine = sa.create_engine(url_object, echo=True)
        self.Session: sessionmaker = sessionmaker(self.engine)

    def structure_count(self) -> int:
        with self.Session() as session:
            num = session.query(Structure).count()
        return num

    def get_all_structures(self):
        """
        sqlalchemy.engine.Engine SELECT "Structure"."Id", "Structure".dataname, "Structure".filename,
        "Residuals".modification_time, "Structure".path
        FROM "Structure" JOIN "Residuals" ON "Structure"."Id" = "Residuals"."StructureId"
        """
        with self.engine.connect() as conn:
            stmt = (sa.select(Structure.Id, Structure.dataname, Structure.filename,
                              Residuals.modification_time, Structure.path)
                    .join_from(Structure, Residuals)
                    )
            return conn.execute(stmt)

    def get_structure(self, session, structureId: int) -> Structure:
        stmt = sa.select(Structure).filter_by(Id=structureId)
        self.structure = session.scalar(stmt)


if __name__ == '__main__':
    db = DB()
    db.load_database(Path('./test.sqlite'))
    print([x for x in db.get_all_structures()][:3])
