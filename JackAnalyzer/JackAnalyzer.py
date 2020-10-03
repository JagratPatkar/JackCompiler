import glob
import sys

class Tokenizer():

    def __init__(self,file):
        pass
    
    def tokenize(self):
        pass

class Compiler():
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
            # compiler = Compiler(fn,tokenizer)
        


def main():
    path = sys.argv[1]
    analyzer = Analyzer(path)
    analyzer.analyze()  

if __name__ == "__main__":
    main()