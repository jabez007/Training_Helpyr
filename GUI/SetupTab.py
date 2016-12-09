from Tkinter import *
import tkMessageBox as Box

from MyTab import MyTab
from Splash import Splash
import Setup
import MyTrack


class SetupTab(MyTab):

    def __init__(self, *args, **kwargs):
        MyTab.__init__(self, *args, **kwargs)

        self.classes = {1: "CE500",
                        2: "AMB_IP"}

        self.selected_class = IntVar()
        self.instructor_environment = None
        self.setup_environments = None
        self.overlord_code = None

        self.init_ui()

    def init_ui(self):
        # Class Frame
        class_frame = Frame(self)
        class_frame.pack(**self.frame_pack_options)
        self.selected_class.set(1)  # default to CE500
        for _class in self.classes:
            rb = Radiobutton(class_frame,
                             text=self.classes[_class],
                             variable=self.selected_class,
                             value=_class,
                             command=self.refresh)
            rb.pack(side=LEFT)

        # End Class Frame

        # Instructor Frame
        instructor_frame = Frame(self)
        instructor_frame.pack(**self.frame_pack_options)

        instructor_label = Label(instructor_frame,
                                 text="CE500 Instructor Environment")
        instructor_label.pack(side=LEFT,
                              padx=2)

        self.instructor_environment = Entry(instructor_frame)
        self.instructor_environment.pack(side=LEFT)
        self.instructor_environment.insert(0,
                                           MyTrack.get_instructor("CE500"))

        # End Instructor Frame

        # Environments Frame
        environments_frame = Frame(self)
        environments_frame.pack(**self.frame_pack_options)

        # # Environments Label
        environments_label = Label(environments_frame,
                                   text="Training Environments")
        environments_label.pack(**self.label_pack_options)

        # # Environments Text Frame
        environments_text_frame = Frame(environments_frame)
        environments_text_frame.pack(**self.frame_pack_options)

        # # # Environments Text
        self.setup_environments = Text(environments_text_frame,
                                       width=25)
        self.setup_environments.insert(END,
                                       "epic-trn41\ntrn42\n43")
        self.setup_environments.pack(**self.text_pack_options)

        # # # Scrollbar for Environments Text
        setup_scr = Scrollbar(environments_text_frame,
                              command=self.setup_environments.yview)
        setup_scr.pack(**self.scrollbar_pack_options)

        # # # link Scrollbar and Text
        self.setup_environments['yscrollcommand'] = setup_scr.set

        # # End Environments Text Frame

        # End Environments Frame

        # Overlord Frame
        overlord_frame = Frame(self)
        overlord_frame.pack(**self.frame_pack_options)

        overlord_label = Label(overlord_frame,
                               text="Cache setup code")
        overlord_label.pack(side=LEFT,
                            padx=2)

        self.overlord_code = Entry(overlord_frame)
        self.overlord_code.pack(side=LEFT)
        self.overlord_code.insert(0,
                                  "CSCce500setup")
        self.overlord_code.config(state='disabled')

        # End Overlord Frame

        # Setup Button Frame
        setup_button_frame = Frame(self)
        setup_button_frame.pack(**self.frame_pack_options)

        setup_button = Button(setup_button_frame,
                              text="Setup",
                              command=self.on_setup)
        setup_button.pack(**self.button_pack_options)

        # End Setup Button Frame

    def get_setup_environments(self):
        caches_text = self.setup_environments.get(1.0, END).strip()

        caches_split_newline = caches_text.split('\n')
        caches_split_comma = caches_text.split(',')

        if len(caches_split_comma) > len(caches_split_newline):
            caches = caches_split_comma
        else:
            caches = caches_split_newline

        return caches

    def on_setup(self):
        title = "Setup"
        result = None

        _class = self.classes[self.selected_class.get()]
        instructor = "".join([s for s in self.instructor_environment.get() if s.isdigit()])
        caches = self.get_setup_environments()
        overlord = self.overlord_code.get()

        if not _class:
            Box.showerror(title,
                          "No class selected")
            return

        elif "CE500" in _class and not instructor and not MyTrack.get_instructor("CE500"):
            Box.showerror(title,
                          "No Instructor Environment Selected for CE500 Class")
            return

        # with Splash(self, "setup.gif", 5.0):
        if "CE500" in _class:
            result = Setup.ce500(instructor,
                                 caches,
                                 overlord)
        elif "AMB_IP" in _class:
            result = Setup.funds(caches,
                                 overlord)

        if not result:
            MyTrack.init()  # make sure interconnects.db is accurate
            Box.showerror(title,
                          "Error occurred during setup for %s\nSee setup.err for more details" % _class)

    def refresh(self):
        _class = self.classes[self.selected_class.get()]

        self.instructor_environment.delete(0,
                                           END)
        self.instructor_environment.config(state='disabled')

        self.overlord_code.config(state='normal')
        self.overlord_code.delete(0,
                                  END)

        if "CE500" in _class:
            self.instructor_environment.config(state='normal')
            self.instructor_environment.insert(0,
                                               MyTrack.get_instructor("CE500"))
            self.overlord_code.insert(0,
                                      "CSCce500setup")
            self.overlord_code.config(state='disabled')

        else:
            self.overlord_code.insert(0,
                                      "CSCInpFunds")
# # # #


def main():
    root = Tk()
    gui = SetupTab(root)
    root.mainloop()

if __name__ == '__main__':
    main()
