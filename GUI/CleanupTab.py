from Tkinter import *
import tkMessageBox as Box

from MyTab import MyTab
from Splash import Splash
import Cleanup
import MyTrack


class CleanupTab(MyTab):

    def __init__(self, *args, **kwargs):
        MyTab.__init__(self, *args, **kwargs)

        self.classes = {1: "CE500",
                        2: "AMB_IP"}

        self.selected_class = IntVar()
        self.instructor_environment = None
        self.cleanup_listboxes = dict()
        self.cleanup_environments = None

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

        # Listbox Frame
        cleanup_listboxes_frame = Frame(self)
        cleanup_listboxes_frame.pack(**self.frame_pack_options)

        # # Listboxes
        for lbl in ['interconnects', 'caches']:
            self.create_listbox(cleanup_listboxes_frame,
                                lbl)

        self.fill_listboxes()

        cleanup_scr = Scrollbar(cleanup_listboxes_frame,
                                command=self.on_scroll)
        cleanup_scr.pack(side=LEFT,
                         fill=Y,
                         expand=False)

        for lbl in self.cleanup_listboxes.keys():
            self.cleanup_listboxes[lbl]['yscrollcommand'] = cleanup_scr.set

        # End Listboxes Frame

        # Clean-up Button Frame
        cleanup_button_frame = Frame(self)
        cleanup_button_frame.pack(**self.frame_pack_options)

        cleanup_button = Button(cleanup_button_frame,
                                text="Clean-up",
                                command=self.on_cleanup)
        cleanup_button.pack(side=RIGHT)

        # End Clean-up Button Frame

    def create_listbox(self, parent, title):
        listbox_label_frame = Frame(parent)
        listbox_label_frame.pack(side=LEFT)

        label = Label(listbox_label_frame,
                      text=title)
        label.pack(**self.label_pack_options)

        self.cleanup_listboxes[title] = Listbox(listbox_label_frame,
                                                height=25,
                                                selectmode=MULTIPLE,
                                                exportselection=False)
        self.cleanup_listboxes[title].bind("<<ListboxSelect>>",
                                           self.on_select)
        self.cleanup_listboxes[title].bind("<MouseWheel>",
                                           self.on_mousewheel)
        self.cleanup_listboxes[title].pack(side=TOP)

    def fill_listboxes(self):
        _class = self.classes[self.selected_class.get()]

        assigned = MyTrack.get("assigned",
                               _class)
        for a in assigned:
            self.cleanup_listboxes['interconnects'].insert(END,
                                                           a[0])
            self.cleanup_listboxes['caches'].insert(END,
                                                    a[1])

    def refresh(self):
        for lbl in self.cleanup_listboxes.keys():
            self.cleanup_listboxes[lbl].delete(0,
                                               END)
        self.fill_listboxes()

        # Also update the Instructor environment
        self.instructor_environment.delete(0,
                                           END)
        self.instructor_environment.config(state='disabled')
        _class = self.classes[self.selected_class.get()]
        if "CE500" in _class:
            self.instructor_environment.config(state='normal')
            self.instructor_environment.insert(0,
                                               MyTrack.get_instructor("CE500"))

    def on_cleanup(self):
        title = "Clean-up"
        result = None

        _class = self.classes[self.selected_class.get()]
        instructor = "".join([s for s in self.instructor_environment.get() if s.isdigit()])

        interconnects_lb = self.cleanup_listboxes['interconnects']
        cache_lb = self.cleanup_listboxes['caches']
        trainees = []
        for selection in interconnects_lb.curselection():
            trainees.append((interconnects_lb.get(selection),
                             cache_lb.get(selection)))
        if not trainees:  # if no Interconnects are selected, grab all of them to clean up
            for i in range(interconnects_lb.size()):
                trainees.append((interconnects_lb.get(i),
                                 cache_lb.get(i)))

        if not _class:
            Box.showerror(title,
                          "No class selected")
            return

        # with Splash(self, "setup.gif", 5.0):
        if "CE500" in _class:
            result = Cleanup.ce500(instructor, trainees)
        elif "AMB_IP" in _class:
            result = Cleanup.funds(trainees)

        if not result:
            Box.showerror(title,
                          "Error occurred during clean-up for %s\nSee cleanup.err for more details" % _class)

        self.refresh()

    def on_select(self, event):
        widget = event.widget
        selection = widget.curselection()

        for lbl in self.cleanup_listboxes.keys():
            if not (widget is self.cleanup_listboxes[lbl]):
                self.cleanup_listboxes[lbl].selection_clear(0,
                                                            END)
                for s in selection:
                    self.cleanup_listboxes[lbl].selection_set(s)

    def on_scroll(self, *args):
        for lbl in self.cleanup_listboxes.keys():
            self.cleanup_listboxes[lbl].yview(*args)

    def on_mousewheel(self, event):
        for lbl in self.cleanup_listboxes.keys():
            self.cleanup_listboxes[lbl].yview_scroll(-event.delta / 100,
                                                     "units")
        # this prevents default bindings from firing, which
        # would end up scrolling the widget twice
        return "break"

# # # #


def main():
    root = Tk()
    gui = CleanupTab(root)
    root.mainloop()

if __name__ == '__main__':
    main()
