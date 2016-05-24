
class CifFile(object):
    """
    maybe use a signal to read cif file after uploading?
    cif = CifFile('path to file')
    cif.parse()
    cif.theta_min
    cif.formula
    ...
    """

    def __init__(self, file):
        self.file = self.read_cif_file(file)
        pass

    def read_cif_file(self):
        pass

    def parse_cif_file(self):
        for line in self.file:
            pass
        pass