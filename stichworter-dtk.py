import numpy as np
import pandas as pd
import re
from tempfile import mkstemp
from shutil import move
from os import remove, close

class Stichworter():
    
    def __init__(self):
        print('"Stichworter" by Uwe Ziegenhagen, ziegenhagen@gmail.com\n\n')

    def regReplace(self,file_path, pattern, subst):
        """
        Based on http://stackoverflow.com/questions/39086/search-and-replace-a-line-in-a-file-in-python 
        this method uses regular expressions for the matching.
        """
        #Create temporary file
        fh, abs_path = mkstemp()
        with open(abs_path,'w') as new_file:
            with open(file_path) as old_file:
                for line in old_file:
                    #print('>',line)
                    new_file.write(re.sub(pattern,subst,line))
        close(fh)
        #Remove original file
        remove(file_path)
        #Move new file
        move(abs_path, file_path)
    
    def regexpTester(self):
        suchmuster = re.compile('(\\\\\\\\ausgabe{hallo}{)(.*)([}])')
        testString = '\\\\ausgabe{hallo}{1}'
        print(testString,':',re.sub(suchmuster,'\g<2>',testString))

    def regexpTester3(self):
        s = "1,2,3"
        p = re.compile(r"(?P<one>\d),(?P<two>\d),(?P<three>\d)")
        m = re.match(p, s) 
        for k, v in m.groupdict().items():
            print(k,':',v)

    def regexpTester4(self):
        s = '\\\\ausgabe{hallo}{1}}}}}'
        p = re.compile(r"(?P<Befehl>\\\\ausgabe{hallo}{)(?P<Keyword>[0-9,]*)(?P<Klammern>}{1})(?P<Rest>.*)")
        m = re.match(p, s) 
        for k, v in m.groupdict().items():
            print(k,':',v)

    def regexpTester2(self):
        suchmuster = re.compile('(.*)(}{1})(.*)')
        testString = 'abcd}efgh'
        print(re.sub(suchmuster,'\g<1>\g<3>',testString))


    def process(self,jobname):
        # read file with Keyword:Page format
        df = pd.read_csv(jobname+'.sti',sep=':',names=['Stichwort','Seite'])
        # Create unique set of pages for the Keywords
        # http://stackoverflow.com/questions/35964689/creating-a-sorted-list-of-unique-numbers-from-a-dataframe/35964970#35964970
        result = df.groupby(['Stichwort'], as_index=False)['Seite'].agg(lambda x: ', '.join(np.unique(x).astype(str)))
        result = pd.DataFrame(result) # create dataframe from the resulting series
        result = result.set_index('Stichwort') # Set the index to the Stichwort column, since we are to use this as key
        print(result)

        # export list of all keywords to LaTeX file
        # TODO: write table myself, allow finer control of typesetting
        result.to_latex(jobname+'.tab',index=True)
        
        # Go through the list of Keyword/Pages Tupels
        # and search for each Keyword. Replace the content of the pages {<content>}
        # with the joint list of pages
        # Remark: \ausgabe{<keyword>} needs empty {} after it ==> \ausgabe{<keyword>}{}
        for index, row in result.iterrows():
            suchmuster = re.compile('(\\\\ausgabe{'+ index + '}{)(.*)(})')  
            self.regReplace(jobname+'.tex',suchmuster,'\\\\ausgabe{'+ index +'}{' + row[0] + '}')
            print(index,':',row[0])
            
# put here the name of the TeX-file
# more than one TeX file is currently not supported or at least not tested
y = Stichworter().regexpTester4()
#x = Stichworter().process('dtk-catalogentry')