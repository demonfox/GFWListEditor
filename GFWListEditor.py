from tkinter import *
import tkinter.messagebox as messagebox

class Application(Frame):
    def __init__(self, master=None):
        self.lastSearchedItem = ''
        self.lastSearchedItemIndex = -1
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

        self.labelText = StringVar()
        self.selectedItemLabel = Label(topFrame, textvariable=self.labelText)
        self.selectedItemLabel.pack(side=LEFT)

        self.deleteButton = Button(topFrame, text='Delete Site', command=self.deleteSite)
        self.deleteButton.pack(side=RIGHT)

        self.addButton = Button(topFrame, text='Add Site', command=self.addSite)
        self.addButton.pack(side=RIGHT)

        bottomFrame = Frame(self)
        bottomFrame.pack(fill=BOTH, expand=True)
        self.scrollBar = Scrollbar(bottomFrame)
        self.scrollBar.pack(side=RIGHT, fill=Y)
        self.listBox = Listbox(bottomFrame, width=100, yscrollcommand = self.scrollBar.set, exportselection=False, selectmode='single')
        self.listBox.bind('<<ListboxSelect>>', self.onGFWListItemSelect)
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

    def onGFWListItemSelect(self, event):
        # messagebox.showinfo('Hi', self.listBox.curselection())
        self.listBox.select_includes(self.listBox.curselection())
        self.labelText.set('Current: %d, %s' % (self.listBox.curselection()[0], self.listBox.get(self.listBox.curselection())))

    def searchGFWList(self):
        itemToSearchFor = self.nameInput.get().strip()
        if itemToSearchFor == '':
            return

        startSearchIndex = 0
        foundItem = False

        #if itemToSearchFor == self.lastSearchedItem:
        #    startSearchIndex = self.lastSearchedItemIndex + 1
        if (self.listBox.curselection()):
            startSearchIndex = self.listBox.curselection()[0] + 1

        foundItem = self.__searchListBox(itemToSearchFor, startSearchIndex, self.listBox.size())

        if not foundItem:
            self.__searchListBox(itemToSearchFor, 0, startSearchIndex-1)

    def addSite(self):
        messagebox.showinfo('Adding a new site', 'Adding ' + self.nameInput.get().strip())
        self.listBox.insert(0, self.nameInput.get().strip())

    def deleteSite(self):
        messagebox.showinfo('Deleting a site', 'Deleting ' + self.listBox.get(self.listBox.curselection()))
        self.listBox.delete(self.listBox.curselection())

    def __searchListBox(self, itemToSearchFor, start, end):
        for index in range(start, end):
            if itemToSearchFor in self.listBox.get(index):
                if (self.listBox.curselection()):
                    self.listBox.select_clear(self.listBox.curselection())
                self.listBox.select_clear(self.lastSearchedItemIndex)
                self.listBox.select_set(index)
                self.listBox.activate(index)
                self.listBox.see(index)
                self.lastSearchedItem = itemToSearchFor
                self.lastSearchedItemIndex = index
                return True
        return False

app = Application()
app.mainloop()
