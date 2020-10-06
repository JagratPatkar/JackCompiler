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
    