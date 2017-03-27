from Tkinter import *
import tkMessageBox as Box

from MyTab import MyTab
import PowerShell
import Overlord


class UtilitiesTab(MyTab):

    def __init__(self, *args, **kwargs):
        MyTab.__init__(self, *args, **kwargs)

        self.overlord_tag = None
        self.overlord_optvars = None
        self.overlord_environments = None

        self.init_ui()

    def init_ui(self):
        """

        :return:
        """
        '''
        PowerShell scripts
        '''
        # PowerShell Frame
        powershell_frame = Frame(self)
        powershell_frame.pack(**self.frame_pack_options)

        powershell_label = Label(powershell_frame,
                                 text="PowerShell scripts to run",
                                 font="Verdana 18 bold")
        powershell_label.pack(**self.label_pack_options)

        # # Interconnect-train* services Frame
        interconnect_services_frame = Frame(powershell_frame)
        interconnect_services_frame.pack(**self.frame_pack_options)
        # # Restart Interconnect-train* services
        restart_button = Button(interconnect_services_frame,
                                text="Restart Interconnect-train*",
                                command=self.on_restart_all)
        restart_button.pack(**self.button_pack_options)
        # # Stop Interconnect-train* services
        stop_button = Button(interconnect_services_frame,
                             text="Stop Interconnect-train*",
                             command=self.on_stop_all)
        stop_button.pack(**self.button_pack_options)
        # # End Interconnect-train* services Frame

        # # Application Pools Frame
        app_pools_frame = Frame(powershell_frame)
        app_pools_frame.pack(**self.frame_pack_options)
        # # Reassign App Pools
        reassign_button = Button(app_pools_frame,
                                 text="Reassign App Pools",
                                 command=self.on_reassign)
        reassign_button.pack(**self.button_pack_options)
        # End PowerShell Frame

        '''
        Overlord command
        '''
        # Overlord Frame
        overlord_frame = Frame(self)
        overlord_frame.pack(**self.frame_pack_options)

        overlord_label = Label(overlord_frame,
                               text="Overlord tags to execute",
                               font="Verdana 18 bold")
        overlord_label.pack(**self.label_pack_options)

        # # Overlord tag to run
        # # Overlord Tag Frame
        overlord_tag_frame = Frame(overlord_frame)
        overlord_tag_frame.pack(**self.frame_pack_options)
        # # Overlord Tag Label
        overlord_tag_label = Label(overlord_tag_frame,
                                   text="Overlord Tag to run")
        overlord_tag_label.pack(side=LEFT,
                                padx=2)
        # # Overlord Tag Entry
        self.overlord_tag = Entry(overlord_tag_frame)
        self.overlord_tag.pack(side=LEFT)
        # # End Overlord Tag Frame

        # # Overlord OptVars Frame
        overlord_optvars_frame = Frame(overlord_frame)
        overlord_optvars_frame.pack(**self.frame_pack_options)

        # # Overlord OptVar Label
        overlord_optvars_label = Label(overlord_optvars_frame,
                                       text="Input variables needed for Tag")
        overlord_optvars_label.pack(side=LEFT,
                                    padx=2)

        # # Overlord OptVars Entry
        self.overlord_optvars = Entry(overlord_optvars_frame)
        self.overlord_optvars.pack(side=LEFT)
        # # End Overlord Optvars Frame

        # # Environment(s) to run tag in
        # # Environments Frame
        environments_frame = Frame(overlord_frame)
        environments_frame.pack(**self.frame_pack_options)

        # # Environments Label
        environments_label = Label(environments_frame,
                                   text="Environments to run Overlord Tag in")
        environments_label.pack(**self.label_pack_options)

        # # # Environments Text Frame
        environments_text_frame = Frame(environments_frame)
        environments_text_frame.pack(**self.frame_pack_options)

        # # # Environments Text
        self.overlord_environments = Text(environments_text_frame,
                                          width=25)
        self.overlord_environments.insert(END,
                                          "epic-trn41\ntrn42\n43")
        self.overlord_environments.pack(**self.text_pack_options)

        # # # Scrollbar for Environments Text
        overlord_scr = Scrollbar(environments_text_frame,
                                 command=self.overlord_environments.yview)
        overlord_scr.pack(**self.scrollbar_pack_options)

        # # # link Scrollbar and Text
        self.overlord_environments['yscrollcommand'] = overlord_scr.set
        # # # End Environments Text Frame
        # # End Environments Frame

        # # Run Overlord
        # # Overlord Button Frame
        overlord_button_frame = Frame(overlord_frame)
        overlord_button_frame.pack(**self.frame_pack_options)

        # # Overlord Button
        overlord_button = Button(overlord_button_frame,
                                 text="Run Overlord",
                                 command=self.on_overlord)
        overlord_button.pack(**self.button_pack_options)
        # # End Overlord Button Frame

        # # Result from Overlord

    def on_restart_all(self):
        if not PowerShell.restart_services():
            Box.showerror("PowerShell",
                          "PowerShell encountered an error\nSee powershell.err for more details")

    def on_stop_all(self):
        if not PowerShell.stop_services():
            Box.showerror("PowerShell",
                          "PowerShell encountered an error\nSee powershell.err for more details")

    def on_reassign(self):
        if not PowerShell.update_app_pools():
            Box.showerror("PowerShell",
                          "PowerShell encountered an error\nSee powershell.err for more details")

    def on_overlord(self):
        environments = self.overlord_environments.get(1.0, END).strip()
        overlord_tag = self.overlord_tag.get().strip()
        overlord_optvars = self.overlord_optvars.get().strip()

        if not Overlord.overlord(environments, overlord_tag, overlord_optvars):
            Box.showerror("Overlord",
                          "Overlord encountered an error\nSee cache.err for more details")

# # # #


def main():
    root = Tk()
    UtilitiesTab(root)
    root.mainloop()

if __name__ == '__main__':
    main()
