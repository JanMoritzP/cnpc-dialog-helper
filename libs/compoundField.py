from distutils import command
from tkinter import Frame, Label, Text, Button

class CompoundField(Frame):
    def __init__(self, parent, label, textInfo, key, destination=None, slot=None):
        Frame.__init__(self, parent)
        self.key = key
        self.destination = destination
        self.slot = slot
        self.textWidth = 40
        self.textHeight = 2
        self.isClosing = False
        self.parent = parent
        self.label = Label(self, text=label)
        self.label.grid(column=0, row=0)
        self.textBox = Text(self, height=self.textHeight, width=self.textWidth)
        self.textBox.insert("end-1c", textInfo)
        self.textBox.bind("<Tab>", lambda event:self.shiftFocus(event))
        self.textBox.grid(column=1, row=0)
        self.killButton = Button(master=self, text="X", command=self.killWidget)
        self.killButton.grid(column=2, row=0)
    
    def shiftFocus(self, event):
        event.widget.tk_focusNext().focus()
        return("break")

    def killWidget(self):
        self.parent.killWidget(self)
        self.destroy()

    def getText(self):
        return self.textBox.get("1.0", "end").strip()

    def setLabel(self, text):
        self.label.configure(text=text)
        