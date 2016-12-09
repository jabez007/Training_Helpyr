from Tkinter import *

import TabbedUI
from SetupTab import SetupTab
from CleanupTab import CleanupTab
from UtilitiesTab import UtilitiesTab
from ErrorsTab import ErrorsTab


class Tabbed(Frame):
    def __init__(self, parent):
        Frame.__init__(self,
                       parent)
        self.parent = parent

        self.classes = {1: "CE500",
                        2: "AMB_IP"}

        self.selected_class = None
        self.instructor_cache = None
        self.setup_caches = None
        self.cleanup_listboxes = None
        self.init_ui()

    def init_ui(self):
        self.parent.title("Training Helpyr")
        self.pack(fill=BOTH,
                  expand=True)

        # Container Frame
        container_frame = TabbedUI.TabBar(self,
                                          "Setup")  # default tab

        # # Setup tab
        setup_frame = TabbedUI.Tab(self,
                                   "Setup")
        SetupTab(setup_frame)
        container_frame.add(setup_frame)

        # # Clean-up tab
        cleanup_frame = TabbedUI.Tab(self,
                                     "Clean-up")
        CleanupTab(cleanup_frame)
        container_frame.add(cleanup_frame)

        # # Utilities tab
        utilities_frame = TabbedUI.Tab(self,
                                       "Utilities")
        UtilitiesTab(utilities_frame)
        container_frame.add(utilities_frame)

        # # Errors tab
        errors_frame = TabbedUI.Tab(self,
                                    "Errors")
        ErrorsTab(errors_frame)
        container_frame.add(errors_frame)

        # End Container Frame
        container_frame.config(bd=2,
                               relief=GROOVE)
        container_frame.show()

# # # #


def main():
    root = Tk()
    gui = Tabbed(root)
    root.mainloop()


if __name__ == '__main__':
    main()
