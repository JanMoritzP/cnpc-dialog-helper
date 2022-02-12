from tkinter import Label, Toplevel, StringVar, OptionMenu, Button, Text
from cleanJson import clean
from os import remove
import json
from functools import partial

class EditWindow(Toplevel):
    def __init__(self, parent, config, data, filename):
        Toplevel.__init__(self, parent)
        self.fields = config
        self.filename = filename
        self.parent = parent
        self.geometry("800x500")
        self.title("Editing " + data["DialogTitle"])
        if config == None:
            self.selection = StringVar()
            self.selectionMenu = OptionMenu(self, self.selection, *data.keys())
            self.selectionMenu.grid(row=0, column=3)
            self.addField = Button(master=self, text="Add", command=self.addSelection)
            self.addField.grid(row=1, column=3)
            self.bind("<Escape>", self.saveQuit)
            self.textWidth = 40
            self.textHeight = 2
            self.labelTitle = Label(master=self, text="Dialog Title")
            self.labelTitle.grid(row=0, column=0)
            self.titleInput = Text(master=self, height=self.textHeight, width=self.textWidth)
            self.titleInput.grid(row=0, column=1)
            self.titleInput.focus()
            self.titleInput.insert("end-1c", data["DialogTitle"])
            self.titleInput.bind("<Tab>", lambda event:self.shiftFocus(event))
            self.titleKill = Button(master=self, text="X")
            self.titleKill.grid(row=0, column=2)
            self.labelText = Label(master=self, text="Dialog Text")
            self.labelText.grid(row=1, column=0)
            self.textInput = Text(master=self, height=self.textHeight, width=self.textWidth)
            self.textInput.grid(row=1, column=1)
            self.textInput.insert("end-1c", data["DialogText"])
            self.textInput.bind("<Tab>", lambda event:self.shiftFocus(event))
            self.textKill = Button(master=self, text="X")
            self.textKill.grid(row=1, column=2)
            self.optionTextFields = []
            self.optionLabels = []
            self.currentRow = 3
            self.dialogAmount = len(data["Options"])
            self.removedOptions = []
            for option in data["Options"]:
                optionLabel = Label(master=self, text="Option Label for " + option["Option"]["Dialog"], name=option["Option"]["Dialog"])
                if option["Option"]["Dialog"] == "-1":
                    optionLabel.configure(text="Closing Dialog")
                optionLabel.grid(row=self.currentRow, column=0)
                self.optionLabels.append(optionLabel)
                optionText = Text(master=self, height=self.textHeight, width=self.textWidth)
                optionText.grid(row=self.currentRow, column=1)
                optionText.insert("end-1c", option["Option"]["Title"])
                optionText.bind("<Tab>", lambda event:self.shiftFocus(event))
                self.optionTextFields.append(optionText)
                killButton = Button(master=self, text="X")
                killButton.configure(command=partial(self.killDialog, killButton, optionText, optionLabel))
                killButton.grid(row=self.currentRow, column=2)
                self.currentRow += 1
            if self.dialogAmount < 6:
                self.addClosingDialogButton = Button(master=self, text="Add Closing Dialog", command=self.addClosingDialog)
                self.addClosingDialogButton.grid(row=0, column=3)

            self.saveButton = Button(master=self, text="Save", command=self.save)
            self.saveButton.grid(row=0, column=4)
            remove("temp.json")

        else:
            print("YOoo, config yeahh")

    def shiftFocus(self, event):
        event.widget.tk_focusNext().focus()
        return("break")


    def saveQuit(self, event=None):
        self.save()
        self.destroy()

    def save(self):
        if self.fields == None:
            clean(self.filename, self.parent)
            tmp = open("temp.json", encoding="utf-8")
            data = json.load(tmp)
            data["DialogTitle"] = self.titleInput.get("1.0", "end").strip()
            data["DialogText"] = self.textInput.get("1.0", "end").strip()
            data["Options"] = []
            currentOption = 0
            defaultOption = {
            "OptionSlot": str(len(data["Options"])),
            "Option": {
                "DialogCommand": "",
                "Dialog": "0",
                "Title": "",
                "DialogColor": "14737632",
                "OptionType": "1"
            }}
            for option in self.optionTextFields:
                defaultOption["Option"]["Title"] = option.get("1.0", "end").strip()
                data["Options"].append(defaultOption)
            for label in self.optionLabels:
                data["Options"][currentOption]["Option"]["Dialog"] = label.winfo_name()
                currentOption += 1
            file = open("dialogs/" + self.parent.choice.get() + "/" + self.filename, "w+", encoding="utf-8")
            json.dump(data, file, indent=4, ensure_ascii=False)
            file.truncate()
            file.close()
            tmp.close()
            remove("temp.json")
            self.parent.refresh()
            self.title("Editing " + data["DialogTitle"])

    def addSelection(self):
        print(self.selection.get())
    
    def addClosingDialog(self):
        optionLabel = Label(master=self, text="Closing Dialog")
        optionLabel.grid(row=self.currentRow, column=0)
        self.optionLabels.append(optionLabel)
        closingDialog = Text(master=self, height=self.textHeight, width=self.textWidth)
        closingDialog.grid(row=self.currentRow, column=1)
        closingDialog.bind("<Tab>", lambda event:self.shiftFocus(event))
        killButton = Button(master=self, text="X")
        killButton.configure(command=partial(self.killDialog, killButton, closingDialog, optionLabel))
        killButton.grid(row=self.currentRow, column=2)
        self.currentRow += 1
        self.optionTextFields.append(closingDialog)
        self.dialogAmount += 1
        if self.dialogAmount == 6: self.addClosingDialogButton.destroy()

    def killDialog(self, killButton, textBox, label):
        self.optionTextFields.remove(textBox)
        self.optionLabels.remove(label)
        killButton.destroy()
        textBox.destroy()
        label.destroy()
