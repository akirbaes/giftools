import sys
import os
import re
import STACK_gifs_horizontal
#Receives a folder and stackgifs two-by-two

def sorted_alphanumeric(data):
    #https://stackoverflow.com/a/48030307
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ] 
    return sorted(data, key=alphanum_key)
os.chdir(sys.argv[1])


for index,file in enumerate(sorted_alphanumeric(os.listdir())):
    first=not index%2
    
    if(first):
        files=[file]
    else:
        files.append(file)
        second_file=file
        STACK_gifs_horizontal.stack_gifs_vh(files,STACK_gifs_horizontal.HOR)