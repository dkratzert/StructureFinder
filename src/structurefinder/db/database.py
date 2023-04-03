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
        # t1 = time.perf_counter()
        connection = self.engine.connect()
        req = '''SELECT str.Id, str.dataname, str.filename, res.modification_time, str.path
                        FROM Structure AS str
                        INNER JOIN Residuals AS res ON res.StructureId == str.Id '''
        data = connection.execute(sa.text(req)).fetchall()
        return data
        # print(f'##1 {t1-time.perf_counter():.3}s')
        """t2 = time.perf_counter()
        with self.Session() as session:
            stmt = (sa.select(Structure, Residuals)
                    .join(Residuals, Structure.Id==Residuals.StructureId)
                    )
            data = session.scalars(stmt).all()
            return data
        print(f'##2 {time.perf_counter()-t2:.3}s')"""

    def get_structure(self, session, structureId: int) -> Structure:
        stmt = sa.select(Structure).filter_by(Id=structureId)
        self.structure = session.scalar(stmt)

