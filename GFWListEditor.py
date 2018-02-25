#!/usr/bin/env python3

import configparser
import datetime
import glob, os
import tkinter.messagebox as messagebox
from azure.storage.file import FileService
from io import BytesIO
from io import StringIO
from io import TextIOWrapper
from shutil import copyfile
from tkinter import *

class Application(Frame):
    NOT_INITIALIZED = 0
    AT_START_OF_RULES = 1
    SCANNING_RULES = 2
    SCANNING_SECTION_AFTER_RULES = 3
    DONE_SCANNING = 4

    def __init__(self, master=None):
        self.lastSearchedItem = ''
        self.lastSearchedItemIndex = -1
        self.config = configparser.ConfigParser()
        self.config.read('config.ini')
        self.gfwlistFileDir = self.config['General']['GFWListLocalFileDir']
        self.gfwlistFile = self.config['General']['GFWListLocalFileName']
        self.azureAccountName = self.config['General']['AzureAccountName']
        self.azureAccountKey = self.config['General']['AzureAccountKey']
        self.azureFileServiceDomain = self.config['General']['AzureFileServiceDomain']
        self.azureFileShareName = self.config['General']['AzureFileShareName']
        self.azureFileShareFileDir = self.config['General']['AzureFileShareFileDir']
        self.azureFileShareFileName = self.config['General']['AzureFileShareFileName']
        self.currentState = Application.NOT_INITIALIZED
        self.sectionBeforeRules = StringIO()
        self.sectionAfterRules = StringIO()

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
        topFrame.pack(padx=5, pady=5, fill=X)

        self.nameInput = Entry(topFrame)
        self.nameInput.pack(fill=X, expand=True)

        self.loadButton = Button(topFrame, text='Load', command=self.loadGFWList)
        self.loadButton.pack(side=LEFT)

        self.searchButton = Button(topFrame, text='Search', command=self.searchGFWList)
        self.searchButton.pack(side=LEFT)

        self.selectedItemLabelText = StringVar()
        self.selectedItemLabel = Label(topFrame, textvariable=self.selectedItemLabelText)
        self.selectedItemLabel.pack(side=LEFT)

        self.deleteButton = Button(topFrame, text='Delete Site', command=self.deleteSite)
        self.deleteButton.pack(side=RIGHT)

        self.addButton = Button(topFrame, text='Add Site', command=self.addSite)
        self.addButton.pack(side=RIGHT)

        self.totalItemsLabelText = StringVar()
        self.totalItemsLabel = Label(topFrame, textvariable=self.totalItemsLabelText)
        self.totalItemsLabel.pack(side=RIGHT)


        middleFrame = Frame(self)
        middleFrame.pack(padx=5, pady=5, fill=BOTH, expand=True)
        self.scrollBar = Scrollbar(middleFrame)
        self.scrollBar.pack(side=RIGHT, fill=Y)
        self.listBox = Listbox(middleFrame, width=100, yscrollcommand = self.scrollBar.set, exportselection=False, selectmode='single')
        self.listBox.bind('<<ListboxSelect>>', self.onGFWListItemSelect)
        self.listBox.pack(side=LEFT, fill=BOTH, padx=5, pady=5, expand=True)
        self.scrollBar.config(command = self.listBox.yview)

        bottomFrame = Frame(self)
        bottomFrame.pack(padx=5, pady=3, fill=X)
        self.saveButton = Button(bottomFrame, text='Save Changes', command=self.saveChanges)
        self.saveButton.pack(side=LEFT)
        self.cleanupBackupsButton = Button(bottomFrame, text='Cleanup old backups', command=self.cleanupBackups)
        self.cleanupBackupsButton.pack(side=RIGHT)

    def loadGFWList(self):
#        name = self.nameInput.get() or 'world'
#        messagebox.showinfo('Message', 'Hello, %s' % name)
        # notice: the catch here is if your local file does not match what is on the file share, then
        # the first time you load it, it will not take effect on your local machine until you save it
        # once first.
        self.listBox.delete(0, self.listBox.size())
        self.sectionBeforeRules.close()
        self.sectionAfterRules.close()
        self.sectionBeforeRules = StringIO()
        self.sectionAfterRules = StringIO()
        with self.openGFWListFile() as f:
            startOfRules = self.config['General']['StartOfRules']
            endOfRules = self.config['General']['EndOfRules']
            self.currentState = Application.NOT_INITIALIZED
            for line in f.readlines():
                if line.startswith(startOfRules):
                    self.currentState = Application.AT_START_OF_RULES
                elif line.startswith(endOfRules):
                    self.currentState = Application.SCANNING_SECTION_AFTER_RULES

                if self.currentState == Application.NOT_INITIALIZED:
                    self.sectionBeforeRules.write(line)
                elif self.currentState == Application.AT_START_OF_RULES:
                    self.sectionBeforeRules.write(line)
                    self.currentState = Application.SCANNING_RULES
                elif self.currentState == Application.SCANNING_RULES:
                    self.listBox.insert(END, line.strip().strip('\",'))
                elif self.currentState == Application.SCANNING_SECTION_AFTER_RULES:
                    self.sectionAfterRules.write(line)
            self.currentState = Application.DONE_SCANNING
            self.totalItemsLabelText.set('Total Sites: %d' % self.listBox.size())

    def openGFWListFile(self):
        azureFileService = FileService(account_name=self.azureAccountName, account_key=self.azureAccountKey)
        # the following snippet creates a file share and a directory
        # azureFileService.create_share('myshare')
        # azureFileService.create_directory('myshare', 'GFWListEditor')
        
        # this scans the file share for all directories
        # generator = azureFileService.list_directories_and_files('myshare')
        # for fileOrDir in generator:
        #    print(fileOrDir.name)
        
        # this uploads a file to the target directory
        # azureFileService.create_file_from_path('myshare', 'GFWListEditor', self.gfwlistFile.rsplit('/', 1)[1], self.gfwlistFile) 
        
        # this downloads a file to a stream
        gfwlistFileStream = BytesIO()
        azureFileService.get_file_to_stream(self.azureFileShareName, self.azureFileShareFileDir, self.azureFileShareFileName, gfwlistFileStream)
        gfwlistFileStream.seek(0)
        return TextIOWrapper(gfwlistFileStream)
        # return open(self.gfwlistFile, 'r') 

    def onGFWListItemSelect(self, event):
        # messagebox.showinfo('Hi', self.listBox.curselection())
        if not self.listBox.curselection():
            return
        self.listBox.select_includes(self.listBox.curselection())
        self.selectedItemLabelText.set('Current: %s, %s' % (self.listBox.curselection()[0], self.listBox.get(self.listBox.curselection())))

    def searchGFWList(self):
        itemToSearchFor = self.nameInput.get().strip()
        if itemToSearchFor == '':
            return

        startSearchIndex = 0
        foundItem = False

        #if itemToSearchFor == self.lastSearchedItem:
        #    startSearchIndex = self.lastSearchedItemIndex + 1
        if (self.listBox.curselection()):
            startSearchIndex = int(self.listBox.curselection()[0]) + 1

        foundItem = self.__searchListBox(itemToSearchFor, startSearchIndex, self.listBox.size())

        if not foundItem:
            self.__searchListBox(itemToSearchFor, 0, startSearchIndex-1)

    def addSite(self):
        #messagebox.showinfo('Adding a new site', 'Adding ' + self.nameInput.get().strip())
        self.listBox.insert(0, self.nameInput.get().strip())
        self.totalItemsLabelText.set('Total Sites: %d' % self.listBox.size())

    def deleteSite(self):
        #messagebox.showinfo('Deleting a site', 'Deleting ' + self.listBox.get(self.listBox.curselection()))
        self.listBox.delete(self.listBox.curselection())
        self.totalItemsLabelText.set('Total Sites: %d' % self.listBox.size())

    def saveChanges(self):
        if (self.currentState != Application.DONE_SCANNING):
            return

        gfwlistBackupFile = self.azureFileShareFileName + '.' + datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S" + '.bk')
        # messagebox.showinfo('You are about to save the changes', 'Are you sure?')
        result = messagebox.askquestion('You are about to save the changes', 'Are you sure?', icon='warning')
        if result == 'yes':
            # this is for copying file locally: copyfile(self.gfwlistFile, gfwlistBackupFile)
            azureFileService = FileService(account_name=self.azureAccountName, account_key=self.azureAccountKey)
            sourceUrl = 'https://%s.%s/%s/%s/%s' % (self.azureAccountName, self.azureFileServiceDomain, self.azureFileShareName, self.azureFileShareFileDir, self.azureFileShareFileName)
            azureFileService.copy_file(self.azureFileShareName, self.azureFileShareFileDir, gfwlistBackupFile, sourceUrl)
            # the folliwng is for writing file locally
            with open(self.gfwlistFile, 'w') as f:
                f.write(self.sectionBeforeRules.getvalue())
                f.write(',\n'.join('  "' + str(e) + '"' for e in self.listBox.get(0, END)))
                f.write('\n')
                f.write(self.sectionAfterRules.getvalue())
            
            # then write it to the file share
            azureFileService.create_file_from_path(self.azureFileShareName, self.azureFileShareFileDir, self.azureFileShareFileName, self.gfwlistFile)

    def cleanupBackups(self):
        result = messagebox.askquestion('You are about to save the changes', 'Are you sure?', icon='warning')
        if result == 'yes':
            # files = []
            # for (dirpath, dirname, filenames) in walk(self.gfwlistFileDir):
            #     files.extend(filenames)
            # for f in files:
            #     print (f)
            
            # the following is for cleaning up files locally
            # bkups = glob.glob(os.path.join(self.gfwlistFileDir, '*.bk'))
            # for f in bkups[:len(bkups)-1]:
            #     os.remove(f)
            
            azureFileService = FileService(account_name=self.azureAccountName, account_key=self.azureAccountKey)
            generator = azureFileService.list_directories_and_files(self.azureFileShareName, self.azureFileShareFileDir)
            for fileOrDir in generator:
                if (fileOrDir.name.endswith('.bk')):
                    azureFileService.delete_file(self.azureFileShareName, self.azureFileShareFileDir, fileOrDir.name)

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
                self.selectedItemLabelText.set('Current: %s, %s' % (self.listBox.curselection()[0], self.listBox.get(self.listBox.curselection())))
                return True
        return False

app = Application()
app.mainloop()
