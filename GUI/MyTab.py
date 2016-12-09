from Tkinter import *


class MyTab(Frame):

    def __init__(self, *args, **kwargs):
        Frame.__init__(self, *args, **kwargs)

        self.pack(fill=BOTH,
                  expand=True)

        # options for Frame.pack
        self.frame_pack_options = options = {}
        options['side'] = TOP
        options['fill'] = BOTH
        options['padx'] = 2
        options['pady'] = 2
        options['expand'] = True

        # options for Label.pack
        self.label_pack_options = options = {}
        options['side'] = TOP
        options['fill'] = X
        options['padx'] = 2
        options['pady'] = 2

        # options for Text.pack
        self.text_pack_options = options = {}
        options['side'] = LEFT
        options['fill'] = BOTH
        options['padx'] = 2
        options['pady'] = 2
        options['expand'] = True

        # options for Scrollbar.pack
        self.scrollbar_pack_options = options = {}
        options['side'] = LEFT
        options['fill'] = Y
        options['expand'] = False

        # options for Button.pack
        self.button_pack_options = options = {}
        options['side'] = RIGHT
        options['fill'] = BOTH
        options['padx'] = 2
        options['pady'] = 2

# # # #
