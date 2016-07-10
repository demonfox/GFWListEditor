from tkinter import *
import tkinter.messagebox as messagebox

class Application(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.createWidgets()

    def createWidgets(self):
#        self.helloLabel = Label(self, text='Hello world!')
#        self.helloLabel.pack()
#        self.quitButton = Button(self, text='Quit', command=self.quit)
#        self.quitButton.pack()
        self.master.title("GFWList Editor")
        self.pack(fill=BOTH, expand=True)

        topFrame = Frame(self)
        topFrame.pack(fill=X)
        self.nameInput = Entry(topFrame)
        self.nameInput.pack(fill=X, expand=True)
        self.loadButton = Button(topFrame, text='Load', command=self.loadGFWList)
        self.loadButton.pack(side=LEFT)
        self.searchButton = Button(topFrame, text='Search', command=self.searchGFWList)
        self.searchButton.pack(side=LEFT)

        bottomFrame = Frame(self)
        bottomFrame.pack(fill=BOTH, expand=True)
        self.scrollBar = Scrollbar(bottomFrame)
        self.scrollBar.pack(side=RIGHT, fill=Y)
        self.listBox = Listbox(bottomFrame, width=100, yscrollcommand = self.scrollBar.set)
        self.listBox.pack(side=LEFT, fill=BOTH, padx=5, pady=5, expand=True)
        self.scrollBar.config(command = self.listBox.yview)

    def loadGFWList(self):
#        name = self.nameInput.get() or 'world'
#        messagebox.showinfo('Message', 'Hello, %s' % name)
        self.listBox.delete(0, self.listBox.size())
        with open('/Users/demonfox/.ShadowsocksX/test.js', 'r') as f:
            startOfRules = "var rules = ["
            endOfRules = "];"
            isEnumeratingRules = False
            for line in f.readlines():
                if line.startswith(startOfRules):
                    isEnumeratingRules = True
                    continue  #skip this line: "var rules = ["
                elif line.startswith(endOfRules):
                    isEnumeratingRules = False
                if isEnumeratingRules:
                    self.listBox.insert(END, line.strip().strip('\",'))

    def searchGFWList(self):
        itemToSearchFor = self.nameInput.get().strip()
        for index in range(self.listBox.size()):
            if itemToSearchFor == self.listBox.get(index):
                messagebox.showinfo('Message', 'yes')
                self.listBox.selection_set(index)
                self.listBox.see(index)

app = Application()
app.mainloop()
