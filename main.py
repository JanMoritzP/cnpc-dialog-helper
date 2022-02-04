from os import walk, remove, path
from tkinter import *
import json
import math
from cleanJson import clean
from createBubble import getArrow


class GUI(Tk):
    def __init__(self):
        super().__init__()
        self.attributes('-fullscreen', True)
        self.fullscreen = True
        
        self.title("DialogHelper")
        self.geometry("1920x1080")
        
        self.frame = Frame(self)
        self.frame.pack()

        self.path = "dialogs/"
        (_, dirnames, _) = walk(self.path).__next__()
        self.currentId = 0
        for dir in dirnames:
            (_, _, files) = walk(self.path + dir).__next__()
            for file in files:
                if int(file.split('.')[0]) > self.currentId: self.currentId = int(file.split('.')[0])
        self.currentId += 1 #This is the id for any new dialog
        self.choice = StringVar()
        self.dropdownMenu = OptionMenu(self, self.choice, *dirnames)
        self.dropdownMenu.place(x=20, y=20)
        self.dropdownMenu.pack()
        
        self.loadBtn = Button(self, text='Load', command=self.load)
        self.loadBtn.pack()

        self.loadBtn = Button(self, text='Save', command=self.saveConfig)
        self.loadBtn.pack()

        self.toggleMoveBtn = Button(self, text="move", command=self.toggleMove)
        self.toggleMoveBtn.pack()
        self.move = True
        
        self.bind('<Escape>', self.endFullscreen)
        self.bind('<F11>', self.toggleFullscreen)
    
        #self.canvas = Canvas(self, width=1920, height=900)
        self.canvas = Canvas(self, width=10000, height=10000)
        #self.canvas.grid(column=0, row=0, sticky=(W, E, S))
        self.canvas.place(x=0, y=1080-900)
        self.canvas.pack()
        self.canvas.bind("<B1-Motion>", self.moveMouse)
        self.canvas.bind("<ButtonRelease-1>", self.release)

        self.changes = []

        self.amountItems = 0
        self.bboxes = []
        self.clicked = False
        self.clickedRect = []
        self.lines = []
        self.fileIndeces = []
        self.positions = {}
        self.openWindow = {}

    def toggleMove(self, event=None):
        if self.move: self.toggleMoveBtn.configure(text="edit")
        else: self.toggleMoveBtn.configure(text="move")
        self.move = not self.move

    def saveConfig(self):
        if path.isfile("dialogHelper.config"):
            with open("dialogHelper.config", "r+", encoding="utf-8") as file:
                try:
                    data = json.load(file)
                    data[self.choice.get()] = self.positions
                    file.seek(0)
                    json.dump(data, file, indent=4, ensure_ascii=False)
                    file.truncate()
                except json.JSONDecodeError:
                    file.seek(0)
                    json.dump({self.choice.get(): self.positions}, file, indent=4, ensure_ascii=False)
                    file.truncate()
        else:
            with open("dialogHelper.config", "w", encoding="utf-8") as file:
                data = {self.choice.get(): self.positions}
                json.dump(data, file, indent=4, ensure_ascii=False)
                file.truncate()
    
    def save(self, element):
        clean(element, self)
        tmp = open("temp.json", encoding="utf-8")
        data = json.load(tmp)
        data["DialogTitle"] = self.openWindow["dialogTitle"].get("1.0", "end")
        data["DialogText"] = self.openWindow["dialogText"].get("1.0", "end")
        file = open("dialogs/" + self.choice.get() + "/" + element, "w+", encoding="utf-8")
        json.dump(data, file, indent=4, ensure_ascii=False)
        file.truncate()
        file.close()
        tmp.close()
        remove("temp.json")

    def release(self, event):
        #get the tag from the textBox xxx.json and save that to the positons object
        if self.clickedRect != []:
            self.positions[self.canvas.gettags(self.clickedRect[1])[0]] = self.canvas.coords(self.clickedRect[1])
        self.clicked = False
        self.clickedRect = []

    def moveMouse(self, event):
        if self.clicked and self.clickedRect != 0:
            rect, textBox, initX, initY = self.clickedRect
            x1, y1, _, _ = self.canvas.coords(rect) # Coords of textbox, move according to init mouse, get top left and move relative
            distX, distY = initX - x1, initY - y1
            #Not get the distance of the current mouse from the initial position because you always want the distance to be the same
            offsetX, offsetY = event.x - x1, event.y - y1
            self.canvas.move(rect, offsetX - distX, offsetY - distY)
            self.canvas.move(textBox, offsetX - distX, offsetY - distY)
            self.clickedRect = rect, textBox, event.x, event.y
            #Now update the arrows
            #initCoords = self.canvas.coords(file)
            #targetCoords = self.canvas.coords(option["Option"]["Dialog"] + ".json")
            #self.canvas.create_line(initCoords[0], initCoords[1], targetCoords[0], targetCoords[1], arrow=LAST, tags=file + "arrow" + option["Option"]["Dialog"] + ".json")
            for element in self.lines:
                start, target, line = element
                if start == rect or target == rect:
                    startMid, targetMid = getArrow(self.canvas.coords(start), self.canvas.coords(target))
                    coords = startMid[0], startMid[1], targetMid[0], targetMid[1]
                    self.canvas.coords(line, coords)
                     
            #Update self.bboxes
            for bbox in self.bboxes:
                if bbox[2] == rect and bbox[3] == textBox:
                    bbox[0] = self.canvas.coords(rect)

    def endFullscreen(self, event=None):  #To get out of fullscreen
        self.fullscreen=False,
        self.attributes('-fullscreen', False)
        return "break"
    
    def toggleFullscreen(self, event=None):  #To toggle fullscreen
        self.fullscreen = not self.fullscreen
        self.attributes('-fullscreen', self.fullscreen)

    def load(self):
        self.positions = {}
        self.bboxes = []
        self.amountItems = 0
        self.canvas.delete('all')
        (_, _, filenames) = walk(self.path + self.choice.get()).__next__()
        for file in filenames:
            clean(file, self)
                    
            tmp = open("temp.json", encoding="utf-8") #Make sure the encoding is utf-8 so that special chars can be displayed       
            data = json.load(tmp)
            #coords = (self.amountItems*50, self.amountItems*50 + 50, self.amountItems*40, self.amountItems*40 +30)
            #Insert an artificial linebreak for the text to make it not collide
            #To do that, check the size of the string, and find a whitespace closest to the middle of the string and replace with \n
            shownText = data["DialogTitle"]
            length = len(shownText)
            if length > 30:
                #Modify shownText
                indeces = [i for i, ltr in enumerate(shownText) if ltr == " "]
                #now check for closest to 15
                currentDist = length
                currentIdx = 0
                for i in indeces:
                    if i - length/2 < currentDist:
                        currentDist = abs(i - length/2)
                        currentIdx = i
                shownText = shownText[:currentIdx] + "\n" + shownText[currentIdx + 1:]
            xCoord = self.amountItems%5*200 + 100
            yCoord = math.floor(self.amountItems/5)*30 + 20
            tag = file
            with open("dialogHelper.config", "r", encoding="utf-8") as configFile:
                data = json.load(configFile)
                try:
                    xCoord, yCoord = data[self.choice.get()][tag]
                except:
                    pass
            textBox=self.canvas.create_text(xCoord, yCoord, anchor=W, text=shownText, tags=tag)
            rect=self.canvas.create_rectangle(self.canvas.bbox(textBox), outline="black", tags=tag + "rect")
            # self.canvas.tag_lower(textBox, rect)
            self.canvas.tag_bind(tag, "<ButtonPress-1>", self.clickedText)
            self.amountItems += 1
            self.bboxes.append([self.canvas.coords(rect), tag, rect, textBox])
            
            self.fileIndeces.append(file.split(".")[0])
            self.positions[tag] = self.canvas.coords(textBox)

            tmp.close()
            remove("temp.json")

        #Now create lines, this has to be done in a different loop, because the tags have to be done first
        for file in filenames:
            clean(file, self)
                    
            tmp = open("temp.json", encoding="utf-8") #Make sure the encoding is utf-8 so that special chars can be displayed       
            data = json.load(tmp)
            for option in data["Options"]:
                if option["Option"]["Dialog"] != "-1": #-1 is always the exit dialog
                    #Draw arrow here to "option["Dialog"].json"
                    #Get middle of the target and draw to the target
                    if option["Option"]["Dialog"] in self.fileIndeces:
                        initCoords = self.canvas.coords(self.canvas.find_withtag(file + "rect")[0])
                        targetCoords = self.canvas.coords(self.canvas.find_withtag(option["Option"]["Dialog"] + ".json" + "rect")[0])
                        startMid, targetMid = getArrow(initCoords, targetCoords)
                        line = self.canvas.create_line(startMid[0], startMid[1], targetMid[0], targetMid[1], arrow=LAST, tags=file + "arrow" + option["Option"]["Dialog"] + ".json")
                        self.lines.append([self.canvas.find_withtag(file + "rect")[0], self.canvas.find_withtag(option["Option"]["Dialog"] + ".json" + "rect")[0], line])
                    else:
                        print("look through folders and find dialog")
            
            tmp.close()
            remove("temp.json")


    def printSelection(self):
        print(self.selection.get() + " added")

    def clickedText(self, event):
        #enumerate over the bboxes and check in whick bbox the click is
        if not self.clicked and self.move:
            for bbox in self.bboxes:
                x1, y1, x2, y2 = bbox[0]
                if event.x >= x1 and event.x <= x2 and event.y >= y1 and event.y <= y2:
                    self.clicked = True
                    self.clickedRect = [bbox[2], bbox[3], event.x, event.y]
        elif self.clicked and self.move: 
            self.clicked = False
            self.clickedRect = []
        elif not self.move:
            #Open Popup menu
            self.openWindow = {}
            tag = ""
            for bbox in self.bboxes:
                x1, y1, x2, y2 = bbox[0]
                if event.x >= x1 and event.x <= x2 and event.y >= y1 and event.y <= y2:
                    tag = bbox[1]
            if tag == "": return
            clean(tag, self)

            tmp = open("temp.json", encoding="utf-8")
            data = json.load(tmp)

            self.popup = Toplevel(master=self, name=tag.split('.')[0])
            self.popup.title("Edit")
            self.popup.geometry("1000x400")
            self.openWindow["master"] = self.popup

            self.selection = StringVar()
            selectionMenu = OptionMenu(self.popup, self.selection, *data.keys())
            selectionMenu.grid(row=0, column=3)
            addField = Button(master=self.popup, text="Add", command=self.printSelection)
            addField.grid(row=1, column=3)

            textWidth = 80
            textHeight = 5
            labelTitle = Label(master=self.popup, text="Dialog Title")
            labelTitle.grid(row=0, column=0)
            titleInput = Text(master=self.popup, height=textHeight, width=textWidth)
            titleInput.grid(row=0, column=1)
            titleInput.insert("end-1c", data["DialogTitle"])
            titleKill = Button(master=self.popup, text="X")
            titleKill.grid(row=0, column=2)
            self.openWindow["dialogTitle"] = titleInput
            labelText = Label(master=self.popup, text="Dialog Text")
            labelText.grid(row=1, column=0)
            textInput = Text(master=self.popup, height=textHeight, width=textWidth)
            textInput.grid(row=1, column=1)
            textInput.insert("end-1c", data["DialogText"])
            textKill = Button(master=self.popup, text="X")
            textKill.grid(row=1, column=2)
            self.openWindow["dialogText"] = textInput
            
            exitButton = Button(master=self.popup, text="Save", name="btn;" + tag.split(".")[0], command=lambda m=tag:self.save(m))
            exitButton.grid(row=2, column=0)
            tmp.close()
            remove("temp.json")




def main():
    #path = input("Enter the root path of your dialog directory: ")
    #print(dirnames)
    gui = GUI()
    gui.mainloop()  
    
if __name__ == "__main__":
    main()