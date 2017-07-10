"""

https://stackoverflow.com/questions/12475850/how-can-an-sql-query-return-data-from-multiple-tables
"""
import pprint
import pg8000

conn = pg8000.connect(user="BrukerPostgreSQL", password="Bruker-PostgreSQL", ssl=False, database="BAXSdb")
cursor = conn.cursor()
cursor.execute("""SELECT 
                        lsq.samples_id,         --0  
                        lsq.a,                  --1
                        lsq.b,                  --2
                        lsq.c,                  --3
                        lsq.alpha, 
                        lsq.beta, 
                        lsq.gamma,
                        col.crystal_colors_id_1,   --7 Farbe 1
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
                        ;
                """)
results = cursor.fetchall()
pprint.pprint(results)



class ApexDB():

    def __init__(self):
        pass

    def open_db(self):
        pass

    def read_data(self):
        pass

    def foo(self):
        pass