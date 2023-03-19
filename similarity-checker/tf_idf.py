import copy
from os import listdir
import string
import math



class similar:
    def __init__(self):
        self.articles = []
        for file in listdir("articles"):
            self.articles.append("articles/" + file)
        self.articles.sort()
        self.corpus_divided = []
        self.frequencies = [{} for i in range(len(self.articles))]
        self.termfrequency = []
        self.freq = {}
        self.idf = {}

    def print(self):
        print(self.corpus_divided)

    def check(self):
        self.seperate_everything()
        self.remove_nesting()
        self.term_frequency()
        self.idf_counter()
        self.tfidf1()


    def seperate_everything(self):
        for article in self.articles:
            self.corpus_divided.append(self.seperate(str(article)))



    def preprocessing(self,article):
        punctuationfree = ""
        for char in str(article):
            if char not in string.punctuation:
                punctuationfree += char.lower()

        tokens = punctuationfree.split()
        return tokens


    def seperate(self, name:str):
        with open(name, "r") as article:
            lines = article.readlines()
        return self.preprocessing(lines)



    def term_frequency(self):
        counter = 0
        for article in self.corpus_divided:
            for item in article:
                if (item in self.frequencies[counter]):
                    self.frequencies[counter][item] += 1
                else:
                    self.frequencies[counter][item] = 1
            counter+=1
        counter=0
        self.termfrequency = copy.deepcopy(self.frequencies)
        for freq in self.frequencies:
            for item in freq:
                self.termfrequency[counter][item] = self.termfrequency[counter][item]/len(self.corpus_divided[counter])
            counter+=1



    def idf_counter(self):
        for freq in self.frequencies:
            for item in freq.keys():
                if item in self.idf:
                    self.idf[item] += 1
                else:
                    self.idf[item] = 1
        for item in self.idf:
            self.idf[item] = math.log(len(self.articles)/self.idf[item],10)

   
    #### {all_words| tfidf1, tfidf2, tfidf}

    def tfidf1(self):
        self.tfidftable = {}
        tfidfvalue = []
        for i in range(len(self.articles)):
            tfidfvalue.append(0.0)
        for word in self.corpus:
            counter = 0
            while counter < len(self.articles):
                for freq in self.termfrequency[counter]:
                    for idfvalue in self.idf.keys():
                        if word == freq:
                            if freq == idfvalue:
                                tfidfvalue[counter] = self.termfrequency[counter][freq] * self.idf[idfvalue]
                counter+=1
            self.tfidftable[word] = tfidfvalue
            tfidfvalue = []
            for i in range(len(self.articles)):
                tfidfvalue.append(0.0)
        

    def remove_nesting(self):
        self.corpus = []
        for article in self.corpus_divided:
            for term in article:
                if term not in self.corpus:
                    self.corpus.append(term)
        return self.corpus
    def compute_cosine_similiraty(self,articleA:int,articleB:int):
        sum = 0
        for term in self.tfidftable:
            sum += (self.tfidftable[term][articleA] * self.tfidftable[term][articleB])
        magnitude_vectorA = 0
        magnitude_vectorB = 0
        for term in self.tfidftable:
            magnitude_vectorA += pow(self.tfidftable[term][articleA],2)
            magnitude_vectorB += pow(self.tfidftable[term][articleB],2)
        print(sum/(math.sqrt(magnitude_vectorA) * math.sqrt(magnitude_vectorB)))
        return sum/(math.sqrt(magnitude_vectorA) * math.sqrt(magnitude_vectorB))

    



if __name__ == '__main__':
    s = similar()
    s.check()
    s.compute_cosine_similiraty(1,2)
