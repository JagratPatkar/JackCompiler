import glob
import sys
from Tokenizer import *


class SymbolTable:

    def __init__(self):
        self.table = []
        self.fieldCounter = 0
        self.staticCounter = 0
        self.argumentCounter = 0
        self.localCounter = 0
    
    def addVar(self,name,varType,kind):
        temp = {
            "name":name,
            "type":varType,
            "kind":kind
        }
        if kind == "field":
            temp["#"] = self.fieldCounter
            self.incrementFieldCounter()
        elif kind == "static":
            temp["#"] = self.staticCounter
            self.incrementStaticCounter()
        elif kind == "argument":
            temp["#"] = self.argumentCounter
            self.incrementArgumentCounter()
        elif kind == "local":
            temp["#"] = self.localCounter
            self.incrementLocalCounter()
        self.table.append(temp)


    def resetTable(self):
        self.table = []
        self.staticCounter = 0
        self.argumentCounter = 0

    def kindOf(self,name):
        for i in self.table:
            if name in i.values():return i["kind"]
        if self.parent != None : return self.parent.kindOf(name) 

    def typeOf(self,name):
        for i in self.table:
            if name in i.values():return i["type"]
        if self.parent != None : return self.parent.typeOf(name) 

    def indexOf(self,name):
        for i in self.table: 
            if name in i.values():return i["#"]
        if self.parent != None : return self.parent.typeOf(name) 

    def initThis(self): self.addVar("this",self.parent.name,"argument")
    def setParent(self,parent): self.parent = parent
    def setName(self,name): self.name = name
    def incrementFieldCounter(self): self.fieldCounter = self.fieldCounter + 1
    def incrementArgumentCounter(self): self.argumentCounter = self.argumentCounter + 1
    def incrementStaticCounter(self): self.staticCounter = self.staticCounter + 1
    def incrementLocalCounter(self): self.localCounter = self.localCounter + 1




class Analyzer():
    
    def __init__(self,path):
        self.path = path
        self.files = []
        self.determine()

    def determine(self):
        dest = self.path.split("/").pop()
        if ".jack" in dest : self.files.append(self.path)
        else: [self.files.append(fn) for fn in glob.iglob(self.path+"/*.jack")]
        
    def analyze(self):
        for fp in self.files:
            tokenizer = Tokenizer(fp)
            tokenizer.tokenize()
            
    

def main():
    path = sys.argv[1]
    analyzer = Analyzer(path)
    analyzer.analyze()

if __name__ == "__main__":
    main()