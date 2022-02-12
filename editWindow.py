from tkinter import Label, Toplevel

class EditWindow(Toplevel):
    def __init__(self, parent, config, data, filename):
        Toplevel.__init__(self, parent)
        self.configLabel = Label(self, text=config)
        self.configLabel.grid(column=0, row=0)
        self.dataLabel = Label(self, text=data)
        self.dataLabel.grid(column=0, row=1)
        self.filenameLabel = Label(self, text=filename)
        self.filenameLabel.grid(column=0, row=1)
    