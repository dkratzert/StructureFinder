"""

https://stackoverflow.com/questions/12475850/how-can-an-sql-query-return-data-from-multiple-tables
"""
import pprint
import pg8000


class ApexDB():
    def __init__(self):
        self.conn = None
        self.cursor = None

    def initialize_db(self):
        """
        Initializes the database connection and cursor.
        """
        try:
            self.conn = pg8000.connect(user="BrukerPostgreSQL", password="Bruker-PostgreSQ",
                                       ssl=False, database="BAXSdb")
        except pg8000.core.ProgrammingError:
            self.conn = None
            return False
        self.cursor = self.conn.cursor()
        return True

    def get_all_data(self):
        """
        Fetches the relevant data from the APEX database.
        Does APEX2 also work?
        """
        self.cursor.execute("""SELECT 
                        lsq.samples_id,         --0  
                        sam.sample_name,           --9
                        sam.last_modified,         --10
                        sam.last_directory,        --11 Not the dir where the files are?
                        indx.first_image           --12 First image of indexing
                        FROM scd.lsq_refinement AS lsq
                          INNER JOIN scd.samples AS sam 
                        ON lsq.samples_id=sam.samples_id
                          INNER JOIN scd.indexing AS indx
                        ON lsq.samples_id=indx.samples_id
                        ;
                """)
        return self.cursor.fetchall()


    def get_residuals(self, Id):
        """
        Only fetch the cell and R-values from DB
        """
        self.cursor.execute("""SELECT 
                        lsq.samples_id,         --0  
                        lsq.a,                  --1
                        lsq.b,                  --2
                        lsq.c,                  --3
                        lsq.alpha, 
                        lsq.beta, 
                        lsq.gamma,
                        col.crystal_colors_id_1,   --7 Farbe 1
                        sam.formula,
                        sam.formula,               --8
                        sam.sample_name,           --9
                        sam.last_modified,         --10
                        sam.last_directory,        --11 Not the dir where the files are?
                        indx.first_image           --12 First image of indexing
                        FROM scd.lsq_refinement AS lsq
                        INNER JOIN scd.sample_color AS col 
                          ON lsq.samples_id=col.samples_id
                        INNER JOIN scd.samples AS sam 
                          ON lsq.samples_id=sam.samples_id
                        INNER JOIN scd.indexing AS indx
                          ON lsq.samples_id=indx.samples_id
                        WHERE lsq.samples_id = {}
                        ;""".format(Id))
        return self.cursor.fetchone()


if __name__ == '__main__':
    apex = ApexDB()
    conn = apex.initialize_db()
    if conn:
        data = apex.get_residuals(2)
        pprint.pprint(data)
        print('###############################')
        data = apex.get_all_data()
        pprint.pprint(data)


