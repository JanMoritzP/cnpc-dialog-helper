from tkinter import Label, Toplevel, StringVar, OptionMenu, Button, Text
from cleanJson import clean
from compoundField import CompoundField
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
            #self.selection = StringVar()
            #self.selectionMenu = OptionMenu(self, self.selection, *data.keys())
            #self.selectionMenu.grid(row=0, column=3)
            #self.addField = Button(master=self, text="Add", command=self.addSelection)
            #self.addField.grid(row=1, column=3)
            self.bind("<Escape>", self.saveQuit)
            #self.textWidth = 40
            #self.textHeight = 2
            self.widgets = {}
            self.widgets["DialogTitle"] = CompoundField(self, "Dialog Title", data["DialogTitle"], "DialogTitle")
            self.widgets["DialogTitle"].grid(column=0, row=0)
            self.widgets["DialogText"] = CompoundField(self, "Dialog Text", data["DialogText"], "DialogText")
            self.widgets["DialogText"].grid(column=0, row=1)
            
            """
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
            self.optionTextFields = [None] * len(data["Options"])
            self.optionLabels = [None] * len(data["Options"])
            self.killButtonList = [None] * len(data["Options"])
            self.removedOptions = []
            """
            self.dialogAmount = len(data["Options"])
            self.currentRow = 2
            self.elements = 0
            
            for option in data["Options"]:
                self.widgets["option" + option["OptionSlot"]] = CompoundField(self, "Option Label for " + option["Option"]["Dialog"], option["Option"]["Title"], "option" + option["OptionSlot"], option["Option"]["Dialog"], self.elements)
                #self.optionLabels[currentElement] = Label(master=self, text="Option Label for " + option["Option"]["Dialog"], name=option["Option"]["Dialog"])
                if option["Option"]["Dialog"] == "-1":
                    self.widgets["option" + option["OptionSlot"]].setLabel("Closing Dialog")
                    self.widgets["option" + option["OptionSlot"]].isClosing = True
                    
                """
                self.optionLabels[currentElement].grid(row=self.currentRow, column=0)
                self.optionTextFields[currentElement] = Text(master=self, height=self.textHeight, width=self.textWidth)
                self.optionTextFields[currentElement].grid(row=self.currentRow, column=1)
                self.optionTextFields[currentElement].insert("end-1c", option["Option"]["Title"])
                self.optionTextFields[currentElement].bind("<Tab>", lambda event:self.shiftFocus(event))
                self.killButtonList[currentElement] = Button(master=self, text="X")
                self.killButtonList[currentElement].configure(command=partial(self.killDialog, self.killButtonList[currentElement], self.optionTextFields[currentElement], self.optionLabels[currentElement]))
                self.killButtonList[currentElement].grid(row=self.currentRow, column=2)
                """
                
                self.widgets["option" + option["OptionSlot"]].grid(row=self.currentRow, column=0)
                self.elements += 1                
                self.currentRow += 1
            self.addClosingDialogButton = Button(master=self, text="Add Closing Dialog", command=self.addClosingDialog)
            self.addClosingDialogButton.grid(row=0, column=1)
            if self.dialogAmount > 5:
                self.addClosingDialogButton.configure(state="disabled")

            self.saveButton = Button(master=self, text="Save", command=self.save)
            self.saveButton.grid(row=0, column=2)
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
            data["DialogTitle"] = self.widgets["DialogTitle"].getText()
            data["DialogText"] = self.widgets["DialogText"].getText()
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
            for widget in self.widgets.values():          
                if widget.slot != None:
                    defaultOption["Option"]["Title"] = widget.getText()
                    defaultOption["Option"]["Title"] = widget.destination
                    defaultOption["OptionSlot"] = widget.slot
                    data["Options"].append(defaultOption)

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
        possibleSlots = [f"{x}" for x in range(6)]
        for widget in self.widgets.values():         
            if widget.slot != None:
                possibleSlots.remove(widget.slot)


        self.widgets["option" + str(self.elements)] = CompoundField(self, "Closing Dialog", "Goodbye", "option" + str(self.elements), "-1", possibleSlots[0])
        self.widgets["option" + str(self.elements)].grid(row=self.currentRow, column=0)
        
        self.currentRow += 1
        self.dialogAmount += 1
        self.elements += 1
        if self.dialogAmount == 6: self.addClosingDialogButton.configure(state="disabled")

    def killDialog(self, killButton, textBox, label):
        self.optionTextFields.remove(textBox)
        self.optionLabels.remove(label)
        killButton.destroy()
        textBox.destroy()
        label.destroy()

    def killWidget(self, widget):
        self.currentRow -= 1
        if widget.slot != None:
            self.dialogAmount -= 1
        if self.dialogAmount < 6: self.addClosingDialogButton.configure(state="active")
        self.widgets.pop(widget.key)
