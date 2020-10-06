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


    def printTable(self):
        print("------------",self.name,"---------------")
        print("------------Table---------------")
        for i in self.table:
            print(i)
        print("--------------------------------")

    def resetTable(self):
        self.table = []
        self.staticCounter = 0
        self.argumentCounter = 0

    def kindOf(self,name):

        for i in self.table:
            if name in self.table.values():
                


    def initThis(self): self.addVar("this",self.parent.name,"argument")
    def setParent(self,parent): self.parent = parent
    def setName(self,name): self.name = name
    def incrementFieldCounter(self): self.fieldCounter = self.fieldCounter + 1
    def incrementArgumentCounter(self): self.argumentCounter = self.argumentCounter + 1
    def incrementStaticCounter(self): self.staticCounter = self.staticCounter + 1
    def incrementLocalCounter(self): self.localCounter = self.localCounter + 1


class Compiler():

    def __init__(self,file,tokenizer):
        newFileName = file.split("/").pop().split(".")[0] + ".vm"
        outputFilePath = file.replace(file.split("/").pop(),newFileName)
        self.output = open(outputFilePath,"w")
        self.tokenizer = tokenizer
        self.classSymbolTable = SymbolTable()
        self.subroutineSymbolTable = SymbolTable()
        self.subroutineSymbolTable.setParent(self.classSymbolTable)
        self.compileClass()
        self.classSymbolTable.printTable()

    def printStrartTag(self,str):
        self.output.write("<")
        self.output.write(str)
        self.output.write("> ")

    def printEndTag(self,str):
        self.output.write(" </")
        self.output.write(str)
        self.output.write(">")

    def printCurrentToken(self):
        self.printStrartTag(self.tokenizer.tokenType())
        if self.tokenizer.tokenType() == "keyword": self.output.write(self.tokenizer.keyWord())
        elif self.tokenizer.tokenType() == "symbol": self.output.write(self.tokenizer.symbol())
        elif self.tokenizer.tokenType() == "identifier": self.output.write(self.tokenizer.identifier())
        elif self.tokenizer.tokenType() == "stringConstant": self.output.write(self.tokenizer.stringVal())
        elif self.tokenizer.tokenType() == "integerConstant": self.output.write(self.tokenizer.intVal())
        self.printEndTag(self.tokenizer.tokenType())
        self.output.write("\n")

    def compileClass(self):

        self.printStrartTag("class")
        self.output.write("\n")

        for i in range(3):
            self.tokenizer.advance()
            if i == 1: self.classSymbolTable.setName(self.tokenizer.identifier())
            self.printCurrentToken()
        
        self.tokenizer.advance()

        while self.tokenizer.keyWord() == "static" or self.tokenizer.keyWord() == "field":
            self.compileClassVarDec()
            self.tokenizer.advance()
        while self.tokenizer.keyWord() == "function" or self.tokenizer.keyWord() == "constructor" or self.tokenizer.keyWord() == "method":
            self.compileClassSubroutineDec()
            self.tokenizer.advance()

        self.printCurrentToken()
        self.printEndTag("class")



    def compileClassVarDec(self):

        self.printStrartTag("classVarDec")
        self.output.write("\n")

        kind = self.tokenizer.keyWord()
        self.tokenizer.advance() 
        if self.tokenizer.tokenType() == "keyword" :
             varType = self.tokenizer.keyWord() 
        elif self.tokenizer.tokenType() == "identifier": 
            varType = self.tokenizer.identifier() 
        self.tokenizer.advance()

        while self.tokenizer.symbol() != ";":
            self.printCurrentToken()
            if self.tokenizer.tokenType() == "identifier" :
                self.classSymbolTable.addVar(self.tokenizer.identifier(),varType,kind) 
            self.tokenizer.advance()

        self.printCurrentToken()
        self.printEndTag("classVarDec")
        self.output.write("\n")

    
    def compileClassSubroutineDec(self):
        self.printStrartTag("subroutineDec")
        self.output.write("\n")
        
        if self.tokenizer.keyWord() == "function" : 
            self.tokenizer.advance()
            self.tokenizer.advance()
            self.subroutineSymbolTable.setName(self.tokenizer.identifier())
        else:
            self.tokenizer.advance()
            self.tokenizer.advance()
            self.subroutineSymbolTable.setName(self.tokenizer.identifier())
            self.subroutineSymbolTable.initThis()


        for i in range(2):
            self.printCurrentToken()
            self.tokenizer.advance()

        self.compileParameterList()
        self.printCurrentToken()
        self.tokenizer.advance()
        self.compileSubroutineBody()
        self.subroutineSymbolTable.printTable()
        self.subroutineSymbolTable.resetTable()
        self.printEndTag("subroutineDec")
        self.output.write("\n")

    def compileParameterList(self):
        self.printStrartTag("parameterList")
        self.output.write("\n")
        varType = None
        while self.tokenizer.symbol() != ")":
           
            if self.tokenizer.symbol() != ",":
                if self.tokenizer.tokenType() == "keyword" : varType = self.tokenizer.keyWord()
                if self.tokenizer.tokenType() == "identifier" : varType = self.tokenizer.identifier()
                self.tokenizer.advance()
                if self.tokenizer.tokenType() == "identifier" :self.subroutineSymbolTable.addVar(self.tokenizer.identifier(),varType,"argument")
                self.tokenizer.advance()
            else:
                self.tokenizer.advance()

        self.printEndTag("parameterList")
        self.output.write("\n")


    def compileSubroutineBody(self):
        self.printStrartTag("subroutineBody")
        self.output.write("\n")
        
        self.printCurrentToken()

        self.tokenizer.advance()
    
        while self.tokenizer.keyWord() == "var":
            self.compileVarDec()
            self.tokenizer.advance()

        self.compileStatements()
        self.printCurrentToken()
        self.printEndTag("subroutineBody")
        self.output.write("\n")

    def compileVarDec(self):
        self.printStrartTag("varDec")
        self.output.write("\n")

        self.tokenizer.advance() 
        if self.tokenizer.tokenType() == "keyword" :
             varType = self.tokenizer.keyWord() 
        elif self.tokenizer.tokenType() == "identifier": 
            varType = self.tokenizer.identifier() 
        self.tokenizer.advance()
        while self.tokenizer.symbol() != ";":
            self.printCurrentToken()
            if self.tokenizer.tokenType() == "identifier" : self.subroutineSymbolTable.addVar(self.tokenizer.identifier(),varType,"local")
            self.tokenizer.advance()    
            

        self.printCurrentToken()
        self.printEndTag("varDec")
        self.output.write("\n")

    def compileStatements(self):
        self.printStrartTag("statements")
        self.output.write("\n")
       
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
        self.printEndTag("statements")
        self.output.write("\n")

    def compileLet(self):
        self.printStrartTag("letStatement")
        self.output.write("\n")

        for i in range(3):
            self.printCurrentToken()
            self.tokenizer.advance()
            if self.tokenizer.symbol() == "[":
                self.printCurrentToken()
                self.tokenizer.advance()
                self.compileExpression()
                self.printCurrentToken()
                self.tokenizer.advance()

        self.compileExpression()
        self.printCurrentToken()#Printing ;
        self.printEndTag("letStatement")
        self.output.write("\n")

    def compileIf(self):
        self.printStrartTag("ifStatement")
        self.output.write("\n")

        for i in range(2):
            self.printCurrentToken()
            self.tokenizer.advance()

        self.compileExpression()

        for i in range(2):
            self.printCurrentToken()
            self.tokenizer.advance()

        self.compileStatements()

        self.printCurrentToken()
        self.tokenizer.advance()

        if self.tokenizer.keyWord() == "else":
            for i in range(2):
                self.printCurrentToken()
                self.tokenizer.advance()
            self.compileStatements()
            self.printCurrentToken()
            self.tokenizer.advance()

        self.printEndTag("ifStatement")
        self.output.write("\n")

    def compileWhile(self):
        self.printStrartTag("whileStatement")
        self.output.write("\n")

        for i in range(2):
            self.printCurrentToken()
            self.tokenizer.advance()

        self.compileExpression()

        for i in range(2):
            self.printCurrentToken()
            self.tokenizer.advance()

        self.compileStatements()

        self.printCurrentToken()

        self.printEndTag("whileStatement")
        self.output.write("\n")

    def compileDo(self):
        self.printStrartTag("doStatement")
        self.output.write("\n")

        for i in range(2):
            self.printCurrentToken()
            self.tokenizer.advance()

        if self.tokenizer.symbol() == ".":
            for i in range(2):
                self.printCurrentToken()
                self.tokenizer.advance()

        self.printCurrentToken()
        self.tokenizer.advance()

        self.compileExpressionList()

        
        self.printCurrentToken()
        self.tokenizer.advance()
        self.printCurrentToken()

        self.printEndTag("doStatement")
        self.output.write("\n")

    def compileReturn(self):
        self.printStrartTag("returnStatement")
        self.output.write("\n")

        self.printCurrentToken()
        self.tokenizer.advance()

        if self.tokenizer.symbol() != ";":
            self.compileExpression()

        
        self.printCurrentToken()

        self.printEndTag("returnStatement")
        self.output.write("\n")

    def compileExpression(self):
        self.printStrartTag("expression")
        self.output.write("\n")

        counter = 0 

        while self.tokenizer.symbol() != ";" and self.tokenizer.symbol() != "]" and self.tokenizer.symbol() != ")" and self.tokenizer.symbol() != ",":
            if self.tokenizer.symbol() in op and not (self.tokenizer.symbol() == "-" and counter == 0):
                self.printCurrentToken()
                self.tokenizer.advance()
            else:
                self.compileTerm()
                if self.tokenizer.symbol() != ";" and self.tokenizer.symbol() != "]" and self.tokenizer.symbol() != ")" and self.tokenizer.symbol() not in op  and self.tokenizer.symbol() != ",": self.tokenizer.advance()
            counter = counter + 1

        self.printEndTag("expression")
        self.output.write("\n")

    def compileTerm(self):

        self.printStrartTag("term")
        self.output.write("\n")

       
        if self.tokenizer.symbol() == "(":  
            self.printCurrentToken()
            self.tokenizer.advance()
            self.compileExpression()
            self.printCurrentToken()
            self.tokenizer.advance()
        else:
            if self.tokenizer.symbol() == "-":
                self.printCurrentToken()
                self.tokenizer.advance()
                self.compileTerm()
            while self.tokenizer.symbol() != ")" and self.tokenizer.symbol() != "]" and self.tokenizer.symbol() != ";" and self.tokenizer.symbol() not in op and self.tokenizer.symbol() != ",":
                if self.tokenizer.tokenType() == "integerConstant" or self.tokenizer.tokenType() == "stringConstant" or self.tokenizer.keyWord() in keywordConstants :
                    self.printCurrentToken()
                    self.tokenizer.advance()
                elif self.tokenizer.symbol() in unaryOp:
                     self.printCurrentToken()
                     self.tokenizer.advance()
                     self.compileTerm()
                elif self.tokenizer.symbol() == "(":
                    self.compileTerm()
                    # self.tokenizer.advance()
                elif self.tokenizer.tokenType() == "identifier":
                    self.printCurrentToken()
                    self.tokenizer.advance()
                    if self.tokenizer.symbol() == "[":
                        self.printCurrentToken()
                        self.tokenizer.advance()
                        self.compileExpression()
                        self.printCurrentToken()
                        self.tokenizer.advance()
                    elif self.tokenizer.symbol() == ".":
                        self.printCurrentToken()
                        self.tokenizer.advance()
                    if self.tokenizer.symbol() == "(":
                        self.printCurrentToken()
                        self.tokenizer.advance()
                        self.compileExpressionList()
                        self.printCurrentToken()
                        self.tokenizer.advance()

       
        self.printEndTag("term")
        self.output.write("\n")

    def compileExpressionList(self):
        self.printStrartTag("expressionList")
        self.output.write("\n")

        while self.tokenizer.symbol() != ")":
            if self.tokenizer.symbol() == "," : 
                self.printCurrentToken()
                self.tokenizer.advance()
            else:
                self.compileExpression()
                if self.tokenizer.symbol() != ")" and self.tokenizer.symbol() != ",": self.tokenizer.advance()

        self.printEndTag("expressionList")
        self.output.write("\n")

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
            Compiler(fp,tokenizer)
    

def main():
    path = sys.argv[1]
    analyzer = Analyzer(path)
    analyzer.analyze()

if __name__ == "__main__":
    main()