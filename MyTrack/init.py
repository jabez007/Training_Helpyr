import json
from AutoVivification import AutoVivification


class MyTrack(AutoVivification):

    def __init__(self, database_file='Interconnects.json'):
        AutoVivification.__init__(self, iterable_file=database_file)
        self.database_file = database_file

    def __del__(self):
        self.save(self.database_file)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.save(self.database_file)

    def get_class(self, ce_or_funds):
        ce_or_funds = ce_or_funds.upper()
        if 'CE500' in ce_or_funds:
            return self.get_ce()
        elif 'AMB_IP' in ce_or_funds:
            return self.get_funds()

    def get_ce(self):
        return [(i, self.get_item("CE500", i)) for i in self["CE500"] if i is not None]

    def get_funds(self):
        return self.get_item("AMB_IP")

# # # #


if __name__ == "__main__":
    track = MyTrack()
    print track.get_ce()
