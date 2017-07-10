"""


"""
import pprint

import pg8000

conn = pg8000.connect(user="postgres", password="C.P.Snow")
cursor = conn.cursor()
cursor.execute("SELECT * FROM scd.lsq_refinement")
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