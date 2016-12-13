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

    def _get_class_(self, ce_or_funds):
        return [(i, self.get_item(ce_or_funds, i)) for i in self[ce_or_funds]]

    def get_ce(self):
        return self._get_class_("CE500")

    def get_assigned_ce(self):
        return [(i, c) for i, c in self.get_ce() if c != ""]

    def get_next_unassigned_ce(self):
        return [(i, c) for i, c in self.get_ce() if c == ""][0][0]

    def get_instructor_ce(self):
        return [(i, self.get_item("Instructors", "CE500", i)) for i in self["Instructors"]["CE500"]][0]

    def get_funds(self):
        return self._get_class_("AMB_IP")

# # # #


if __name__ == "__main__":
    track = MyTrack()
    print track.get_ce()
    print track.get_assigned_ce()
    print track.get_next_unassigned_ce()
    print track.get_instructor_ce()
    print track.get_funds()
