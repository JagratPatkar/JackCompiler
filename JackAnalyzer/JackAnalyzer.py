import glob
import sys


keywords = ["class","constructor","function","method","field","static",
            "var","int","char","boolean","void","true","flase","null"
            ,"this","let","do","if","else","while","return"]

symbols = ["{","}","(",")","[","]",".",",",";","+","-","*","/","&","|","<",">","=","~"]


    

class Tokenizer():

    def __init__(self,file):
        newFileName = file.split("/").pop().split(".")[0] + "T.xml"
        outputFilePath = file.replace(file.split("/").pop(),newFileName)
        self.input = open(file,"r")
        self.output = open(outputFilePath,"w")
        self.tokens = []
        
    
    def tokenize(self):
        el = self.readline()
        while el != '':
            # for ec in el:
            #     print(ec)
            el = self.readline()
             
    def readline(self):
        el = self.input.readline()
        if el.startswith("//") and el.startswith("/**"):
            el = self.input.readline()
        return el


class Compiler():

    def __init__(self,file,tokenizer):
        newFileName = file.split("/").pop().split(".")[0] + ".xml"
        outputFilePath = file.replace(file.split("/").pop(),newFileName)
        self.output = open(outputFilePath,"w")

    def compile(self):
        pass

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
            compiler = Compiler(fp,tokenizer)
            compiler.compile()
        


def main():
    path = sys.argv[1]
    analyzer = Analyzer(path)
    analyzer.analyze()  

if __name__ == "__main__":
    main()