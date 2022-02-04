from os import walk, remove
from tkinter import Tk

def clean(file: int, self: Tk) -> None:
    """Clean up json file"""
    linebreak = False
    with open("temp.json", "w") as tmp:
        with open(self.path + self.choice.get() + "/" + file) as fs:
            for line in fs:
                arr = line.split(":")
                if len(arr) > 1:
                    #Check if There is "" and if not, then add it
                    if arr[1].count("\"") == 2:
                        tmp.write(line)
                    elif any(x in arr[1] for x in "\{\}\[\]"):
                        tmp.write(line)
                    elif arr[1].count("\"") == 1: #linebreaks that have to be dealt with
                        linebreak = True
                        tmp.write(line[:-1]) # Because we know that the first line is always ok, now check for concurrent lines and stop after "\"" is detected
                    elif linebreak:
                        #Deal with it here
                        if "\",\n" in line: #Check this, because this should be a definite newline
                            linebreak = False
                            tmp.write(line + "\n")
                        else:
                            tmp.write(line[:-1]) #The \n has to be ommitted here
                    else:
                        #Add ""
                        end = ""
                        if arr[1][-2] == ",": end = ","
                        tmp.write(arr[0] + ": \"" + arr[1][1:-2] + "\"" + end + "\n")
                else:
                    if linebreak:
                        #Deal with it here
                        if "\",\n" in line: #Check this, because this should be a definite newline
                            linebreak = False
                            tmp.write(line + "\n")
                        else:
                            tmp.write(line[:-1]) #The \n has to be ommitted here
                    else:
                        tmp.write(line)



