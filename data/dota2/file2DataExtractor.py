import codecs
import re
import json 
import pandas as pd



f = codecs.open('D:\\Work\\Projects\\Extractor\\Dmembers.txt','r','UTF-8')
# data = json.loads(f.read())
# jsonNormal = pd.json_normalize(data)
# print(jsonNormal)
tResult = []
lines = f.readlines()
# print(lines)
for line in lines:
    if re.search('id: ([0-9])\w+',line):
        tResult.append(line)
    # elif re.search('name: ', line):
    #     tResult.append(line.replace('name: ',''))
print(tResult)