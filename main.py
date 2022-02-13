from os import walk, remove, path, mkdir
from shutil import rmtree
from tkinter import *
import json
import math
from shutil import copyfile
from turtle import width
from cleanJson import clean
from createBubble import getArrow
from editWindow import EditWindow


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
        self.loadedChoice = ""

        self.saveBtn = Button(self, text='Save', command=self.saveConfig)
        self.saveBtn.pack()

        self.moveBtn = Button(self, text="move", command=self.toggleMove, state='disabled')
        self.moveBtn.pack()
        self.editBtn = Button(self, text="edit", command=self.toggleEdit)
        self.editBtn.pack()
        self.createBtn = Button(self, text="create", command=self.toggleCreate)
        self.createBtn.pack()
        self.linkBtn = Button(self, text="link", command=self.toggleLink)
        self.linkBtn.pack()
        self.createNewFolder = Button(self, text="create new folder", command=self.createFolder)
        self.createNewFolder.pack()
        self.createFolderText = Text(self, height=1, width=50)
        self.createFolderText.pack()
        self.removeFolder = Button(self, text="remove folder", command=self.removeFolder)
        self.removeFolder.pack()
        self.exitBtn = Button(self, text="exit", command=self.destroy)
        self.exitBtn.pack()
        
        self.mode = "move"

        self.bind('<Escape>', self.endFullscreen)
        self.bind('<F11>', self.toggleFullscreen)
    
        #self.canvas = Canvas(self, width=1920, height=900)
        self.canvas = Canvas(self, width=10000, height=10000)
        #self.canvas.grid(column=0, row=0, sticky=(W, E, S))
        self.canvas.place(x=0, y=1080-900)
        self.canvas.pack()
        self.canvas.bind("<B1-Motion>", self.moveMouse)
        self.canvas.bind("<ButtonRelease-1>", self.release)
        self.canvas.bind("<Button-1>", self.canvasClicked)

        self.changes = []

        self.amountItems = 0
        self.bboxes = []
        self.clicked = False
        self.clickedRect = []
        self.lines = []
        self.fileIndeces = []
        self.positions = {}
        self.openWindow = {}
        
        self.linking = False
        self.linkSrc = None

    def toggleMove(self, event=None):
        self.mode = "move"
        self.handleButtonStates("move")

    def toggleEdit(self, event=None):
        self.mode = "edit"
        self.handleButtonStates("edit")
        
    def toggleCreate(self, event=None):
        self.mode = "create"
        self.handleButtonStates("create")
        
    def toggleLink(self, event=None):
        self.mode = "link"
        self.handleButtonStates("link")

    def handleButtonStates(self, button):
        self.moveBtn.configure(state='active')
        self.editBtn.configure(state='active')
        self.createBtn.configure(state='active')
        self.linkBtn.configure(state='active')
        if button == "move":
            self.moveBtn.configure(state='disabled')
        elif button == "edit":
            self.editBtn.configure(state='disabled')
        elif button == "create": 
            self.createBtn.configure(state='disabled')
        elif button == "link":
            self.linkBtn.configure(state='disabled')

    def createFolder(self):
        if self.createFolderText.get("1.0", "end").strip() != "":
            mkdir(self.path + self.createFolderText.get("1.0", "end").strip())
            self.createFolderText.delete("1.0", "end")        
            (_, dirnames, _) = walk(self.path).__next__()
            self.choice.set("")
            self.dropdownMenu['menu'].delete(0, "end")
            for dirname in dirnames:
                self.dropdownMenu['menu'].add_command(label=dirname, command=lambda value=dirname:self.choice.set(value))
            
    def removeFolder(self):
        if self.choice.get() != "":
            rmtree(self.path + self.choice.get())    
            self.createFolderText.delete("1.0", "end")        
            (_, dirnames, _) = walk(self.path).__next__()
            self.choice.set("")
            self.dropdownMenu['menu'].delete(0, "end")
            for dirname in dirnames:
                self.dropdownMenu['menu'].add_command(label=dirname, command=lambda value=dirname:self.choice.set(value))
            self.canvas.delete('all')

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
        self.lines = []
        self.amountItems = 0
        self.canvas.delete('all')
        self.loadedChoice = self.choice.get()
        (_, _, filenames) = walk(self.path + self.choice.get()).__next__()
        for file in filenames:
            clean(file, self)
            tmp = open("temp.json", encoding="utf-8") #Make sure the encoding is utf-8 so that special chars can be displayed       
            try:
                data = json.load(tmp)
            except json.JSONDecodeError:
                print("JsonDecodeError with " + file)
                tmp.close()
                remove('temp.json')
                continue
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


    def refresh(self):
        self.load()

    def clickedText(self, event):
        #enumerate over the bboxes and check in whick bbox the click is
        if not self.clicked and self.mode == "move":
            for bbox in self.bboxes:
                x1, y1, x2, y2 = bbox[0]
                if event.x >= x1 and event.x <= x2 and event.y >= y1 and event.y <= y2:
                    self.clicked = True
                    self.clickedRect = [bbox[2], bbox[3], event.x, event.y]
        elif self.clicked and self.mode == "move": 
            self.clicked = False
            self.clickedRect = []
        elif self.mode == "edit":
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
            tmp.close()

            editWindow = EditWindow(self, None, data, tag)
        elif self.mode == "link":
            if self.linking:
                self.linking = False
                source = self.linkSrc
                dst = False
                for bbox in self.bboxes:
                    x1, y1, x2, y2 = bbox[0]
                    if event.x >= x1 and event.x <= x2 and event.y >= y1 and event.y <= y2:
                        dst = [bbox[2], bbox[3], event.x, event.y] #rect, textBox, x, y
                if dst == False:
                    return
                filename = self.canvas.gettags(dst[1])[0] #This gives us filename
                clean(filename, self)
                tmp = open("temp.json", encoding='utf-8')
                #try:
                #except:
                #    return
                data = json.load(tmp)
                tmp.close()
                remove("temp.json")
                if len(data["Options"]) > 6: return
                filename = source
                clean(source, self)
                tmp = open("temp.json", encoding='utf-8')
                sourceData = json.load(tmp)
                tmp.close()
                remove("temp.json")
                if len(data["Options"]) > 0:
                    for option in data["Options"]:
                        if option["Option"]["Dialog"] == source.split("."):
                            return
                defaultOption = {
                "OptionSlot": str(len(data["Options"])),
                "Option": {
                    "DialogCommand": "",
                    "Dialog": sourceData["DialogId"],
                    "Title": sourceData["DialogTitle"],
                    "DialogColor": "14737632",
                    "OptionType": "1"
                }}
                data["Options"].append(defaultOption)
                file = open(self.path + self.choice.get() + "/" + self.canvas.gettags(dst[1])[0], 'w', encoding='utf-8')
                json.dump(data, file, indent=4, ensure_ascii=False)
                file.truncate()
                file.close()
                
                initCoords = self.canvas.coords(self.canvas.find_withtag(source + "rect")[0])
                targetCoords = self.canvas.coords(self.canvas.find_withtag(self.canvas.gettags(dst[1])[0] + "rect")[0])
                startMid, targetMid = getArrow(initCoords, targetCoords)
                line = self.canvas.create_line(startMid[0], startMid[1], targetMid[0], targetMid[1], arrow=LAST, tags=source + "arrow" + self.canvas.gettags(dst[1])[0])
                self.lines.append([self.canvas.find_withtag(source + "rect")[0], self.canvas.find_withtag(self.canvas.gettags(dst[1])[0] + "rect")[0], line])
            else:
                for bbox in self.bboxes:
                    x1, y1, x2, y2 = bbox[0]
                    if event.x >= x1 and event.x <= x2 and event.y >= y1 and event.y <= y2:
                        src = [bbox[2], bbox[3], event.x, event.y] #rect, textBox, x, y
                if src == False:
                    return
                self.linking = True
                self.linkSrc = self.canvas.gettags(src[1])[0]

    def canvasClicked(self, event):
        if self.mode == "create" and self.loadedChoice != "":
            x, y = event.x, event.y
            tag = str(self.currentId) + ".json"
            textBox=self.canvas.create_text(x, y, anchor=W, text="new dialog", tags=tag)
            rect=self.canvas.create_rectangle(self.canvas.bbox(textBox), outline="black", tags=tag + "rect")
            self.canvas.tag_bind(tag, "<ButtonPress-1>", self.clickedText)
            self.amountItems += 1
            self.bboxes.append([self.canvas.coords(rect), tag, rect, textBox])
            
            self.fileIndeces.append(self.currentId)
            self.positions[tag] = self.canvas.coords(textBox)
            filename = self.path + self.choice.get() + "/" + tag
            file = open(filename, 'w+', encoding='utf-8')
            file.close()
            copyfile('reference.json', filename)
            file = open(filename, 'r', encoding='utf-8')

            data = json.load(file)
            data["DialogId"] = self.currentId
            data["DialogTitle"] = "New Dialog"
            data["DialogText"] = "Insert Dialog Text"
            file.close()
            file = open(filename, 'w', encoding='utf-8')
            json.dump(data, file, indent=4, ensure_ascii=False)
            file.truncate()
            file.close()
            self.currentId += 1

def main():
    #path = input("Enter the root path of your dialog directory: ")
    #print(dirnames)
    gui = GUI()
    gui.mainloop()  
    
if __name__ == "__main__":
    main()