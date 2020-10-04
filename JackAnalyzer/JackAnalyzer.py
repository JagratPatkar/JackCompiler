import glob
import sys


keywords = ["class","constructor","function","method","field","static",
            "var","int","char","boolean","void","true","false","null"
            ,"this","let","do","if","else","while","return"]
symbols = ["{","}","(",")","[","]",".",",",";","+","-","*","/","&","|","<",">","=","~"]
alphabets = ["a","b","c","d","e","f","g","h","i","j","k","l","m","n","o","p","q","r","s","t","u","v","w","x","y","z","A","B","C","D","F","G","H","I","J","K","L","M","N","O","P","Q","R","S","T","U","V","W","X","Y","Z"]
keywordConstants = ["true","false","null","this"]
op = ["+","-","*","/","&amp;","|","&lt;","&gt;","="]
unaryOp = ["~","-"]


class Tokenizer():

    def __init__(self,file):
        newFileName = file.split("/").pop().split(".")[0] + "T.xml"
        outputFilePath = file.replace(file.split("/").pop(),newFileName)
        self.input = open(file,"r")
        self.output = open(outputFilePath,"w")
        self.tokens = []
        self.currentToken = -1
        
    def tokenize(self):
        el = self.input.readline()
        while el != '':
            if not el.startswith("//") and not el.startswith("/**") and not el.startswith(" *"):
                el = self.serialize(el)
                i = 0
                while i < len(el):
                    if el[i] == '"':
                        token = el[i]
                        i = i + 1
                        if i < len(el):
                                while el[i] != '"': 
                                    token = token + el[i]
                                    i = i + 1
                                else:token = token + el[i]
                        self.tokens.append(token)
                    else:
                        if el[i] != " " and el[i] != "\n" and el[i] != "\r" and el[i] != "\t":
                            token = el[i]
                            i = i + 1
                            if i < len(el):
                               
                                while el[i] != " " and el[i] != "\n" and el[i] != "\r" and el[i] != "\t": 
                                    token = token + el[i]
                                    i = i + 1
                            self.tokens.append(token)
                    if i < len(el): i = i + 1
            el = self.input.readline()

    def serialize(self,line):
        line = line.split("//")
        line = line[0]
        line = line.split("/**")
        line = line[0]
        for i in symbols:
            if i in line:line = line.replace(i," " + i + " ")
        
        return line

    def printTokens(self):
        self.output.write("<tokens> ")
        self.output.write("\n")
        while self.hasMoreTokens():
            self.advance()
            self.printTokenStart()
            self.printTokenVal()
            self.printTokenEnd()  
            self.output.write("\n")
        self.output.write("</tokens>")


    def printTokenStart(self):
        self.output.write("<")
        self.output.write(self.tokenType())
        self.output.write("> ")

    def printTokenEnd(self):
        self.output.write(" </")
        self.output.write(self.tokenType())
        self.output.write(">")


    def printTokenVal(self):
        if self.tokenType() == "keyword": self.output.write(self.keyWord())
        elif self.tokenType() == "symbol": self.output.write(self.symbol())
        elif self.tokenType() == "identifier": self.output.write(self.identifier())
        elif self.tokenType() == "stringConstant": self.output.write(self.stringVal())
        elif self.tokenType() == "integerConstant": self.output.write(self.intVal())

    def hasMoreTokens(self): return self.currentToken < len(self.tokens)-1

    def advance(self): self.currentToken = self.currentToken + 1
    
    def reset(self): self.currentToken = -1

    def tokenType(self):
        if self.tokens[self.currentToken] in keywords:return "keyword"
        elif self.tokens[self.currentToken] in symbols:return "symbol"
        elif self.tokens[self.currentToken].startswith('"'):return "stringConstant"
        elif self.tokens[self.currentToken][0] in alphabets or self.tokens[self.currentToken].startswith("_"):return "identifier"
        else: return "integerConstant" 

    def keyWord(self): return self.tokens[self.currentToken]

    def symbol(self):
        if self.tokens[self.currentToken] == "<": return "&lt;"
        elif self.tokens[self.currentToken] == ">": return "&gt;"
        elif self.tokens[self.currentToken] == "&": return "&amp;"
        elif self.tokens[self.currentToken] == '"': return "&quot"
        else: return self.tokens[self.currentToken] 

    def identifier(self): return self.tokens[self.currentToken] 

    def intVal(self): return self.tokens[self.currentToken] 

    def stringVal(self): return self.tokens[self.currentToken].replace('"',"")
    

class Compiler():

    def __init__(self,file,tokenizer):
        newFileName = file.split("/").pop().split(".")[0] + ".xml"
        outputFilePath = file.replace(file.split("/").pop(),newFileName)
        self.output = open(outputFilePath,"w")
        self.tokenizer = tokenizer
        self.compileClass()

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

        while self.tokenizer.symbol() != ";":
            self.printCurrentToken()
            self.tokenizer.advance()

        self.printCurrentToken()
        self.printEndTag("classVarDec")
        self.output.write("\n")

    
    def compileClassSubroutineDec(self):
        self.printStrartTag("subroutineDec")
        self.output.write("\n")

        for i in range(4):
            self.printCurrentToken()
            self.tokenizer.advance()

        self.compileParameterList()
        self.printCurrentToken()
        self.tokenizer.advance()
        self.compileSubroutineBody()
        self.printEndTag("subroutineDec")
        self.output.write("\n")

    def compileParameterList(self):
        self.printStrartTag("parameterList")
        self.output.write("\n")
        
        while self.tokenizer.symbol() != ")":
            self.printCurrentToken()
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

        while self.tokenizer.symbol() != ";":
            self.printCurrentToken()
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

        while self.tokenizer.symbol() != ";" and self.tokenizer.symbol() != "]" and self.tokenizer.symbol() != ")" and self.tokenizer.symbol() != ",":
            if self.tokenizer.symbol() in op: 
                self.printCurrentToken()
                self.tokenizer.advance()
            else:
                self.compileTerm()
                if self.tokenizer.symbol() != ";" and self.tokenizer.symbol() != "]" and self.tokenizer.symbol() != ")" and self.tokenizer.symbol() not in op  and self.tokenizer.symbol() != ",": self.tokenizer.advance()


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
            tokenizer.printTokens()
            tokenizer.reset()
            Compiler(fp,tokenizer)
    

def main():
    path = sys.argv[1]
    analyzer = Analyzer(path)
    analyzer.analyze()  

if __name__ == "__main__":
    main()