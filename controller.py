from tkinter import Frame, Button

class Controller(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.parent = parent

        self.moveBtn = Button(self, text="move", command=lambda :self.handleButtonStates("move"), state='disabled')
        self.moveBtn.pack()
        self.editBtn = Button(self, text="edit", command=lambda :self.handleButtonStates("edit"))
        self.editBtn.pack()
        self.createBtn = Button(self, text="create", command=lambda :self.handleButtonStates("create"))
        self.createBtn.pack()
        self.deleteBtn = Button(self, text="delete", command=lambda :self.handleButtonStates("delete"))
        self.deleteBtn.pack()
        self.linkBtn = Button(self, text="link", command=lambda :self.handleButtonStates("link"))
        self.linkBtn.pack()
        
        self.mode = "move"

    def handleButtonStates(self, button):
        self.moveBtn.configure(state='active')
        self.editBtn.configure(state='active')
        self.createBtn.configure(state='active')
        self.deleteBtn.configure(state='active')
        self.linkBtn.configure(state='active')
        self.mode = button
        if button == "move":
            self.moveBtn.configure(state='disabled')
        elif button == "edit":
            self.editBtn.configure(state='disabled')
        elif button == "create": 
            self.createBtn.configure(state='disabled')
        elif button == "delete": 
            self.deleteBtn.configure(state='disabled')
        elif button == "link":
            self.linkBtn.configure(state='disabled')

    def getMode(self):
        return self.mode

    