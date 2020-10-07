import glob
import sys
from Tokenizer import *

class Label():

    def __init__(self):
        self.lableCounter = 0
        self.lable = str(self.lableCounter)

    def getLable(self):  return self.lable

    def updateLable(self): 
        self.lableCounter = self.lableCounter + 1
        self.lable = str(self.lableCounter)



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

    def printTable(self):
        print("---------------------------------------")
        print("           ",self.name,"               ")
        for i in self.table:
            print(i)

    def resetTable(self):
        self.table = []
        self.localCounter = 0
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

    def getFieldCount(self): return str(self.fieldCounter)
    def getArgumentCount(self): return str(self.argumentCounter)
    def getLocalCount(self): return str(self.localCounter)

class VMWriter():
    
    def __init__(self,file):
        newFileName = file.split("/").pop().split(".")[0] + ".vm"
        outputFilePath = file.replace(file.split("/").pop(),newFileName)
        self.output = open(outputFilePath,"w")

    def writePush(self,segment,index): self.output.write("push "+segment+" "+index+"\n")

    def writePop(self,segment,index): self.output.write("pop "+segment+" "+index+"\n")

    def writeArithmetic(self,command):
        if command == "+": self.output.write("add\n")
        elif command == "*": self.writeCall("Math.multiply","2")
        elif command == "-": self.output.write("sub\n")
        elif command == "=": self.output.write("eq\n")
        elif command == ">": self.output.write("gt\n")
        elif command == "<": self.output.write("lt\n")
        elif command == "&": self.output.write("and\n")
        elif command == "|": self.output.write("or\n")
        elif command == "~": self.output.write("not\n")
        elif command == "neg": self.output.write("neg\n")

    def writeLable(self,lable): self.output.write("label "+lable+"\n")

    def writeGoto(self,lable): self.output.write("goto "+lable+"\n")

    def writeIf(self,lable): self.output.write("if-goto "+lable+"\n")

    def writeCall(self,name,nArgs): self.output.write("call "+name+" "+nArgs+"\n")

    def writeFunction(self,name,nArgs): self.output.write("function "+name+" "+nArgs+"\n")

    def writeReturn(self): self.output.write("return\n")

    def close(self): self.output.close()


class CompilationEngine():

    def __init__(self,file,tokenizer,writer,labler):
        self.tokenizer = tokenizer
        self.writer = writer
        self.classSymbolTable = SymbolTable()
        self.subroutineSymbolTable = SymbolTable()
        self.subroutineSymbolTable.setParent(self.classSymbolTable)
        self.lable = labler
        self.methodList = self.tokenizer.getMethods()
        self.tokenizer.reset()
        self.currFuncType = None
        self.compileClass()
        self.classSymbolTable.printTable()

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

    def compileClassVarDec(self):

        counter = 0
        varType = None
        if self.tokenizer.keyWord() == "static": 
            kind = "static"
        elif self.tokenizer.keyWord() == "field":
            kind = "field"

        while self.tokenizer.symbol() != ";":
            if counter == 1:
                if self.tokenizer.tokenType() == "identifier" :  varType = self.tokenizer.identifier()
                elif self.tokenizer.tokenType() == "keyword" : varType = self.tokenizer.keyWord() 
            elif counter > 1 and self.tokenizer.symbol() != ",":
                self.classSymbolTable.addVar(self.tokenizer.identifier(),varType,kind)
            self.tokenizer.advance()
            counter = counter + 1


    
    def compileClassSubroutineDec(self):
        
        if self.tokenizer.keyWord() == "function": self.currFuncType = "function"
        elif self.tokenizer.keyWord() == "constructor": self.currFuncType = "constructor"
        elif self.tokenizer.keyWord() == "method":
            self.currFuncType = "method"
            self.subroutineSymbolTable.initThis()

            
        for i in range(3):
            if i == 2: 
                self.subroutineSymbolTable.setName(self.classSymbolTable.name + "." + self.tokenizer.identifier())
                if self.currFuncType  == "method":
                    self.methodList.append(self.classSymbolTable.name + "." + self.tokenizer.identifier())
            self.tokenizer.advance()

        
        self.compileParameterList()

        self.tokenizer.advance()

        self.compileSubroutineBody()
        self.subroutineSymbolTable.printTable()
        self.subroutineSymbolTable.resetTable()

    def compileParameterList(self):
        self.tokenizer.advance()
        while self.tokenizer.symbol() != ")":
            if self.tokenizer.symbol() != ",":
                if self.tokenizer.tokenType() == "identifier" :  varType = self.tokenizer.identifier()
                elif self.tokenizer.tokenType() == "keyword" : varType = self.tokenizer.keyWord()
                self.tokenizer.advance()
                self.subroutineSymbolTable.addVar(self.tokenizer.identifier(),varType,"argument")
                self.tokenizer.advance()
            else:
                self.tokenizer.advance()


    def compileSubroutineBody(self):
        
        self.tokenizer.advance()
    
        while self.tokenizer.keyWord() == "var":
            self.compileVarDec()
            self.tokenizer.advance()

        self.writer.writeFunction(self.subroutineSymbolTable.name,self.subroutineSymbolTable.getLocalCount())

        if self.currFuncType == "constructor":
            self.writer.writePush("constant",self.classSymbolTable.getFieldCount())
            self.writer.writeCall("Memory.alloc","1")
            self.writer.writePop("pointer","0")
        elif self.currFuncType == "method":
            self.writer.writePush("argument","0")
            self.writer.writePop("pointer","0")

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
        
        self.tokenizer.advance()
        kind = self.subroutineSymbolTable.kindOf(self.tokenizer.identifier())
        index = self.subroutineSymbolTable.indexOf(self.tokenizer.identifier())
        self.tokenizer.advance()

        if self.tokenizer.symbol() == "[":
            # self.tokenizer.advance()
            # self.compileExpression()
            # self.tokenizer.advance()
            pass
        else:
            self.tokenizer.advance()
            self.compileExpression()
            if kind == "field": self.writer.writePop("this",index)
            else: self.writer.writePop(kind,index)


    def compileIf(self):
        for i in range(2):
            self.tokenizer.advance()
        self.compileExpression()
        self.writer.writeArithmetic("~")
        lable1 = "LABEL" + self.lable.getLable()
        self.lable.updateLable() 
        self.writer.writeIf(lable1)
        
        for i in range(2):
            self.tokenizer.advance()

        self.compileStatements()
        
        self.tokenizer.advance()

        if self.tokenizer.keyWord() == "else":
            lable2 = "LABEL"+self.lable.getLable()
            self.lable.updateLable() 
            self.writer.writeGoto(lable2)
            self.writer.writeLable(lable1)
            for i in range(2):
                self.tokenizer.advance()
            self.compileStatements()
            self.tokenizer.advance()
            self.writer.writeLable(lable2)
        else:
            self.writer.writeLable(lable1)

    def compileWhile(self):
        for i in range(2):
            self.tokenizer.advance()

        lable1 = "LABEL" + self.lable.getLable()
        self.lable.updateLable()

        self.writer.writeLable(lable1)

        self.compileExpression()

        self.writer.writeArithmetic("~")
        lable2 = "LABEL" + self.lable.getLable()
        self.lable.updateLable()

        self.writer.writeIf(lable2)

        for i in range(2):
            self.tokenizer.advance()

        self.compileStatements()

        self.writer.writeGoto(lable1)
        self.writer.writeLable(lable2)

    def compileDo(self):
        flag = False
        self.tokenizer.advance()
        name = self.tokenizer.identifier()
        ko = self.subroutineSymbolTable.kindOf(self.tokenizer.identifier())
        if ko == None: flag = True
        self.tokenizer.advance()

        if self.tokenizer.symbol() == "(":

            funcName = self.classSymbolTable.name + "." + name
            self.tokenizer.advance()
            if name in self.methodList: 
                self.writer.writePush("pointer","0")
            nArgs = self.compileExpressionList()
            self.tokenizer.advance()
            if name in self.methodList:  nArgs = str(int(nArgs)+1)
            self.writer.writeCall(funcName,nArgs)

        elif self.tokenizer.symbol() == ".":
            self.tokenizer.advance()
            subName = self.tokenizer.identifier()
            self.tokenizer.advance()
            self.tokenizer.advance()
            if not flag : 
                if ko == "field": self.writer.writePush("this",self.subroutineSymbolTable.indexOf(name))
                else:self.writer.writePush(ko,self.subroutineSymbolTable.indexOf(name))
            nArgs = self.compileExpressionList()
            if not flag : nArgs = str(int(nArgs)+1)
            self.tokenizer.advance()
            if flag: self.writer.writeCall(name + "." + subName,nArgs)
            else:
                clsName = self.subroutineSymbolTable.typeOf(name)
                self.writer.writeCall(clsName + "." + subName,nArgs)

        self.writer.writePop("temp","0")

    def compileReturn(self):

        self.tokenizer.advance()
        if self.tokenizer.symbol() != ";":
            self.compileExpression()
        else:
            self.writer.writePush("constant","0")

        self.writer.writeReturn()

    def compileExpression(self):
        while self.tokenizer.symbol() != ";" and self.tokenizer.symbol() != "]" and self.tokenizer.symbol() != ")" and self.tokenizer.symbol() != ",":
            self.compileTerm()
            if self.tokenizer.symbol() != ";" and self.tokenizer.symbol() != "]" and self.tokenizer.symbol() != ")"  and self.tokenizer.symbol() != "," and self.tokenizer.symbol() not in op: self.tokenizer.advance()


    def compileTerm(self):

       
        if self.tokenizer.symbol() == "-":

            self.tokenizer.advance()
            self.compileExpression() 
            self.writer.writeArithmetic("neg")
            
        while self.tokenizer.symbol() != ")" and self.tokenizer.symbol() != "]" and self.tokenizer.symbol() != ";"  and self.tokenizer.symbol() != ",":
            if self.tokenizer.symbol() in op: 
                sym = self.tokenizer.symbol()                    
                self.tokenizer.advance()
                self.compileTerm() #4
                self.writer.writeArithmetic(sym)
            elif self.tokenizer.tokenType() == "integerConstant": 
                self.writer.writePush("constant",self.tokenizer.intVal())
                self.tokenizer.advance()
            elif self.tokenizer.tokenType() == "stringConstant":
                #TODO ----------------------------------
                self.tokenizer.advance()
            elif self.tokenizer.keyWord() in keywordConstants:
                if self.tokenizer.keyWord() == keywordConstants[3]: self.writer.writePush("pointer","0")
                elif self.tokenizer.keyWord() == keywordConstants[2]: self.writer.writePush("constant","0")
                elif self.tokenizer.keyWord() == keywordConstants[1]: self.writer.writePush("constant","0")
                elif self.tokenizer.keyWord() == keywordConstants[0]: 
                    self.writer.writePush("constant","1")
                    self.writer.writeArithmetic("neg")
                self.tokenizer.advance()
            elif self.tokenizer.symbol() in unaryOp:
                sym = self.tokenizer.symbol()
                self.tokenizer.advance()
                self.compileExpression() 
                self.writer.writeArithmetic(sym)
            elif self.tokenizer.symbol() == "(":
                self.tokenizer.advance()
                self.compileExpression()
                self.tokenizer.advance()
            elif self.tokenizer.tokenType() == "identifier":
                nArgs = "0"
                flag = False
                name = self.tokenizer.identifier()
                ko = self.subroutineSymbolTable.kindOf(self.tokenizer.identifier())
                io = self.subroutineSymbolTable.indexOf(self.tokenizer.identifier())
                if ko == None: flag = True
                else:
                    if ko == "field": self.writer.writePush(keywordConstants[3],io)
                    else: self.writer.writePush(ko,io) 
                self.tokenizer.advance()
                if self.tokenizer.symbol() == "[": #TODO ----------------------------------
                    self.tokenizer.advance()
                    self.compileExpression()
                    self.tokenizer.advance()
                elif self.tokenizer.symbol() == ".":
                    self.tokenizer.advance()
                    subName = self.tokenizer.identifier()
                    self.tokenizer.advance()
                    self.tokenizer.advance()
                    nArgs = self.compileExpressionList()
                    self.tokenizer.advance()
                    if flag: self.writer.writeCall(name + "." + subName,nArgs)
                    else:
                        clsName = self.subroutineSymbolTable.typeOf(name)
                        nArgs = str(int(nArgs) + 1)
                        self.writer.writeCall(clsName + "." + subName,nArgs)

                elif self.tokenizer.symbol() == "(":

                    funcName = self.classSymbolTable.name + "." + name
                    self.tokenizer.advance()
                    if name in self.methodList: self.writer.writePush("pointer","0")
                    nArgs = self.compileExpressionList()
                    self.tokenizer.advance()
                    if name in self.methodList:  nArgs = str(int(nArgs)+1)
                    self.writer.writeCall(funcName,nArgs)


       
    def compileExpressionList(self):
        counter = 0
        while self.tokenizer.symbol() != ")":
            self.compileExpression()
            counter = counter + 1
            if self.tokenizer.symbol() != ")" : self.tokenizer.advance()
        return str(counter)

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
        labler = Label()
        for fp in self.files:
            tokenizer = Tokenizer(fp)
            tokenizer.tokenize()
            vmWrite = VMWriter(fp)
            CompilationEngine(fp,tokenizer,vmWrite,labler)



def main():
    path = sys.argv[1]
    analyzer = Analyzer(path)
    analyzer.analyze()

if __name__ == "__main__":
    main()