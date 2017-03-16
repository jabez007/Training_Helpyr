from Tkinter import *
import os

import TabbedUI
from MyTab import MyTab
import Log


class ErrorsTab(MyTab):

    def __init__(self, *args, **kwargs):
        MyTab.__init__(self, *args, **kwargs)

        self.errors = dict()

        self.init_ui()

    def init_ui(self):
        # Errors Tabs Frame
        errors_tabs_frame = TabbedUI.TabBar(self,
                                            "Setup")

        # # Error Files Frames
        for f in os.listdir(Log.LOG_DIR):
            if os.path.isdir(os.path.join(Log.LOG_DIR, f)):
                self.errors[f] = TabbedUI.Tab(self,
                                              f)
                self.errors[f, "Text"] = Text(self.errors[f])
                self.errors[f, "Text"].pack(**self.text_pack_options)
                errors_tabs_frame.add(self.errors[f])

        self.get_errors()
        # # End Error Files Frames

        # # Refresh Errors Button Frame
        errors_button_frame = Frame(self)
        errors_button_frame.pack(**self.frame_pack_options)

        errors_button = Button(errors_button_frame,
                               text="Refresh All",
                               command=self.on_refresh)
        errors_button.pack(side=RIGHT)
        # # End Refresh Errors Button Frame

        errors_tabs_frame.show()
        # End Errors Tabs Frame

    def get_errors(self):
        for f in self.errors:
            if type(f) is str:
                errors_text = Log.MyReader(name=f).read()
                self.errors[f, "Text"].insert(END,
                                              errors_text)
                if errors_text:
                    width = max([len(s) for s in errors_text.split('\n')]) + 1
                    self.errors[f, "Text"].config(width=width)

    def on_refresh(self):
        for f in self.errors:
            if type(f) is tuple:
                self.errors[f].delete(1.0,
                                      END)

        self.get_errors()


# # # #


def main():
    root = Tk()
    gui = ErrorsTab(root)
    root.mainloop()

if __name__ == '__main__':
    main()
