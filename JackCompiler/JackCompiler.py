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
        self.parent = None
    
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
            if name in i.values() : return str(i["#"])
        if self.parent != None : return self.parent.indexOf(name) 

    def initThis(self): self.addVar("this",self.parent.name,"argument")
    def setParent(self,parent): self.parent = parent
    def setName(self,name): self.name = name
    def incrementFieldCounter(self): self.fieldCounter = self.fieldCounter + 1
    def incrementArgumentCounter(self): self.argumentCounter = self.argumentCounter + 1
    def incrementStaticCounter(self): self.staticCounter = self.staticCounter + 1
    def incrementLocalCounter(self): self.localCounter = self.localCounter + 1



class VMWriter():
    
    def __init__(self,file):
        newFileName = file.split("/").pop().split(".")[0] + ".xml"
        outputFilePath = file.replace(file.split("/").pop(),newFileName)
        self.output = open(outputFilePath,"w")

    def writePush(self,segment,index):
        pass

    def writePop(self,segment,index):
        pass

    def writeArithmetic(self,command):
        pass

    def writeLable(self,lable):
        pass

    def writeGoto(self,lable):
        pass

    def writeIf(self,lable):
        pass

    def writeCall(self,name,nArgs):
        pass

    def writeFunction(self,name,nArgs):
        pass

    def writeReturn(self):
        pass

    def close(self):
        pass


class CompilationEngine():

    def __init__(self,file,tokenizer,writer):
        self.tokenizer = tokenizer
        self.writer = writer
        self.classSymbolTable = SymbolTable()
        self.subroutineSymbolTable = SymbolTable()
        self.subroutineSymbolTable.setParent(self.classSymbolTable)
        self.compileClass()

    def compileClass(self):

        for i in range(3):
            self.tokenizer.advance()
            if i == 1: 
                self.classSymbolTable.setName(self.tokenizer.identifier())

        self.tokenizer.advance()

        while self.tokenizer.keyWord() == "static" or self.tokenizer.keyWord() == "field":
            self.compileClassVarDec()
            self.tokenizer.advance()
        while self.tokenizer.keyWord() == "function" or self.tokenizer.keyWord() == "constructor" or self.tokenizer.keyWord() == "method":
            self.compileClassSubroutineDec()
            self.tokenizer.advance()

    def isVar(self,kind,index):
        pass

    def compileClassVarDec(self):

        counter = 0

        if self.tokenizer.keyWord() == "static": 
            kind = "static"
        elif self.tokenizer.keyWord() == "field":
            kind = "field"

        while self.tokenizer.symbol() != ";":
            if counter == 1:
                if self.tokenizer.tokenType() == "identifier" :  varType = self.tokenizer.identifier()
                elif self.tokenizer.tokenType() == "keyword" : varType = self.tokenizer.keyWord()  
            if self.tokenizer.symbol() != "," and counter != 1:
                self.classSymbolTable.addVar(self.tokenizer.identifier(),varType,kind)
                self.isVar(self.classSymbolTable.kindOf(self.tokenizer.identifier()),self.classSymbolTable.indexOf(self.tokenizer.identifier()))
            self.tokenizer.advance()
            counter = counter + 1


    
    def compileClassSubroutineDec(self):

        if self.tokenizer.keyWord() == "method":
            self.subroutineSymbolTable.initThis()

        for i in range(4):
            self.tokenizer.advance()
        
        self.compileParameterList()
        self.tokenizer.advance()
        self.compileSubroutineBody()
        self.subroutineSymbolTable.resetTable()

    def compileParameterList(self):
        
        counter = 1
        while self.tokenizer.symbol() != ")":
            if counter%2 == 1 and self.tokenizer.symbol() != ",":
                if self.tokenizer.tokenType() == "identifier" :  varType = self.tokenizer.identifier()
                elif self.tokenizer.tokenType() == "keyword" : varType = self.tokenizer.keyWord() 
            elif counter%2 == 0 :
                self.subroutineSymbolTable.addVar(self.tokenizer.identifier(),varType,"argument")
                self.isVar(self.subroutineSymbolTable.kindOf(self.tokenizer.identifier()),self.subroutineSymbolTable.indexOf(self.tokenizer.identifier()))
            self.tokenizer.advance()
            counter = counter + 1


    def compileSubroutineBody(self):
        
        self.tokenizer.advance()
    
        while self.tokenizer.keyWord() == "var":
            self.compileVarDec()
            self.tokenizer.advance()
        self.compileStatements()
    
    def compileVarDec(self):
        counter = 0
        varType = None

        while self.tokenizer.symbol() != ";":
            if counter == 1:
                if self.tokenizer.tokenType() == "identifier" :  varType = self.tokenizer.identifier()
                elif self.tokenizer.tokenType() == "keyword" : varType = self.tokenizer.keyWord() 
            elif counter > 1 and self.tokenizer.symbol() != ",":
                self.subroutineSymbolTable.addVar(self.tokenizer.identifier(),varType,"local")
                self.isVar(self.subroutineSymbolTable.kindOf(self.tokenizer.identifier()),self.subroutineSymbolTable.indexOf(self.tokenizer.identifier()))
            self.tokenizer.advance()
            counter = counter + 1
        

    def compileStatements(self):
       
        while self.tokenizer.tokenType() != "symbol":
            toEx = True
            if self.tokenizer.keyWord() == "let": self.compileLet()
            elif self.tokenizer.keyWord() == "if": 
                self.compileIf()
                toEx = False
            elif self.tokenizer.keyWord() == "while": self.compileWhile()
            elif self.tokenizer.keyWord() == "do": self.compileDo()
            elif self.tokenizer.keyWord() == "return": self.compileReturn()
            if toEx : self.tokenizer.advance()

    def compileLet(self):
        
        for i in range(3):
            if i == 1: self.isVar(self.subroutineSymbolTable.kindOf(self.tokenizer.identifier()),self.subroutineSymbolTable.indexOf(self.tokenizer.identifier()))
            self.tokenizer.advance()
            if self.tokenizer.symbol() == "[":
                self.tokenizer.advance()
                self.compileExpression()
                self.tokenizer.advance()

        self.compileExpression()

    def compileIf(self):
        for i in range(2):
            self.tokenizer.advance()

        self.compileExpression()

        for i in range(2):
            self.tokenizer.advance()

        self.compileStatements()

        self.tokenizer.advance()

        if self.tokenizer.keyWord() == "else":
            for i in range(2):
                self.tokenizer.advance()
            self.compileStatements()
            self.tokenizer.advance()


    def compileWhile(self):
        for i in range(2):
            self.tokenizer.advance()

        self.compileExpression()

        for i in range(2):
            self.tokenizer.advance()

        self.compileStatements()


    def compileDo(self):
        for i in range(2):
            self.tokenizer.advance()

        if self.tokenizer.symbol() == ".":
            for i in range(2):
                self.tokenizer.advance()

        self.tokenizer.advance()

        self.compileExpressionList()
       
        self.tokenizer.advance()


    def compileReturn(self):

        self.tokenizer.advance()
        if self.tokenizer.symbol() != ";":
            self.compileExpression()


    def compileExpression(self):
        counter = 0 

        while self.tokenizer.symbol() != ";" and self.tokenizer.symbol() != "]" and self.tokenizer.symbol() != ")" and self.tokenizer.symbol() != ",":
            if self.tokenizer.symbol() in op and not (self.tokenizer.symbol() == "-" and counter == 0):
                
                self.tokenizer.advance()
            else:
                self.compileTerm()
                if self.tokenizer.symbol() != ";" and self.tokenizer.symbol() != "]" and self.tokenizer.symbol() != ")" and self.tokenizer.symbol() not in op  and self.tokenizer.symbol() != ",": self.tokenizer.advance()
            counter = counter + 1


    def compileTerm(self):

       
        if self.tokenizer.symbol() == "(":  
            self.tokenizer.advance()
            self.compileExpression()
            self.tokenizer.advance()
        else:
            if self.tokenizer.symbol() == "-":

                self.tokenizer.advance()
                self.compileTerm()

            while self.tokenizer.symbol() != ")" and self.tokenizer.symbol() != "]" and self.tokenizer.symbol() != ";" and self.tokenizer.symbol() not in op and self.tokenizer.symbol() != ",":
                if self.tokenizer.tokenType() == "integerConstant" or self.tokenizer.tokenType() == "stringConstant" or self.tokenizer.keyWord() in keywordConstants :
                    
                    self.tokenizer.advance()
                elif self.tokenizer.symbol() in unaryOp:
                    
                     self.tokenizer.advance()
                     self.compileTerm()
                elif self.tokenizer.symbol() == "(":
                    self.compileTerm()
                elif self.tokenizer.tokenType() == "identifier":
                    flag = False
                    ko = self.subroutineSymbolTable.kindOf(self.tokenizer.identifier())
                    io = self.subroutineSymbolTable.indexOf(self.tokenizer.identifier())
                    if ko == None:flag = True
                    else: self.isVar(ko,io)
                    self.tokenizer.advance()
                    if self.tokenizer.symbol() == "[":
                        self.tokenizer.advance()
                        self.compileExpression()
                        self.tokenizer.advance()
                    elif self.tokenizer.symbol() == ".":
                        if flag: pass
                        self.tokenizer.advance()
                    if self.tokenizer.symbol() == "(":
                        if flag: pass
                        self.tokenizer.advance()
                        self.compileExpressionList()
                        self.tokenizer.advance()

       
    def compileExpressionList(self):

        while self.tokenizer.symbol() != ")":
            if self.tokenizer.symbol() == "," : 
                self.tokenizer.advance()
            else:
                self.compileExpression()
                if self.tokenizer.symbol() != ")" and self.tokenizer.symbol() != ",": self.tokenizer.advance()


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
            vmWrite = VMWriter(fp)
            CompilationEngine(fp,tokenizer,vmWrite)

    

def main():
    path = sys.argv[1]
    analyzer = Analyzer(path)
    analyzer.analyze()

if __name__ == "__main__":
    main()