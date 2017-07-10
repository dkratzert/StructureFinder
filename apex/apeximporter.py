"""

https://stackoverflow.com/questions/12475850/how-can-an-sql-query-return-data-from-multiple-tables
"""
import pprint
import pg8000

conn = pg8000.connect(user="BrukerPostgreSQL", password="Bruker-PostgreSQL", ssl=False, database="BAXSdb")
cursor = conn.cursor()
cursor.execute("""SELECT lsq_refinement.samples_id, 
                        lsq_refinement.a, 
                        lsq_refinement.b, 
                        lsq_refinement.c, 
                        lsq_refinement.alpha, 
                        lsq_refinement.beta, 
                        lsq_refinement.gamma 
                        FROM scd.lsq_refinement
                JOIN scd.sample_color
                        ON scd.sample_color.samples_id=scd.lsq_refinement.samples_id
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