from PIL import Image
import sys
import re
import os
from fractions import Fraction
import numpy as np
import statistics
from gif_manips import get_background_color, unused_color, swap_palette_colors

def reorder_background(image, background=None):
    #Puts the background color at index 0
    image=image.copy()
    if(background==None):
        background_id = get_background_color(image) #must be a palette ID
    else:
        background_id = background
    return swap_palette_colors(image,0,background_id)
    return result

def generate_outname(filename,timing,mode):
    name,ext = os.path.splitext(filename)
    
    
    if(mode=="set"):
        #Set to value, previous value irrelevant
        insert = "T"+str(timing[0])
        matchany = re.search("Tx?[0-9]+d?[0-9]*",name)
        if(matchany):
            name=name[:matchany.start()]+insert+name[matchany.end():]
        else:
            name+=insert
    elif(mode=="multiply"):
        matchmul = re.search("Tx[0-9]+d[0-9]+",name)
        matchnum = re.search("T[0-9]+",name)
        if(matchmul):
            print("#Multiply the multiplicator")
            num = [int(x) for x in name[matchmul.start()+1:matchmul.end()].split(d)]
            f = Fraction(*num)*Fraction(*timing)
            insert = "Tx"+str(f.numerator)+"d"+str(f.denominator)
            name=name[:matchmul.start()]+insert+name[matchmul.end():]
        elif(matchnum):
            print("#Multiply the constant")
            num = int(name[matchnum.start()+1:matchnum.end()])
            dur = max(20,int(num*timing[0]/timing[1]))
            insert = "T"+str(dur)
            name=name[:matchnum.start()]+insert+name[matchnum.end():]
        else:
            print("#Write the multiplicator")
            f = Fraction(*timing)
            insert = "Tx"+str(f.numerator)+"d"+str(f.denominator)
            name+=insert
            
    #print("Name:",name)
    return name+ext
    
def retime_gif(filename,timing,mode="set"):
    im = Image.open(filename)
    output = list()
    transparencies=list()
    durations = list()
    try:
        while 1:
            #output.append(reorder_background(im,im.info.get("transparency",None)))
            output.append(im.copy())
            if(mode=="set"):
                durations.append(timing[0])
            if(mode=="multiply"):
                try:
                    d=int(im.info['duration']*timing[0]/timing[1])
                    if(d<20):
                        print("Warning: timing",len(durations),"=",d,"<20")
                    durations.append(max(20,d))
                except IndexError:
                    durations.append(int(im.info['duration']*timing[0]))
                
            transparency=im.info.get("transparency",None)
            if(transparency is not None):
                transparencies.append(transparency)
            im.seek(im.tell()+1)
            
    except EOFError:
        pass # end of sequence
    if(len(set(durations))==1):
        outname = generate_outname(filename,[durations[0]],"set")
    else:
        outname = generate_outname(filename,timing,mode)
        
    if(transparencies):
        #There exist at least one transparency
        for i in range(len(output)):
            out=output[i]
            tr = out.info.get("transparency",None)
            if(tr!=None):
                output[i]=swap_palette_colors(out,tr,0)
            else:
                output[i]=swap_palette_colors(out,unused_color(out),0)
                #[TODO] test mixed transpareny/no transpareny
    print(output)
    print(outname)
        
    if(len(output)>1):
        if(transparencies):
            #print(transparencies)
            output[0].save(outname, save_all=True,append_images=output[1:], optimize=False, disposal=2, duration=durations, loop=0, transparency=0)
        else:
            output[0].save(outname, save_all=True,append_images=output[1:], optimize=False, disposal=2, duration=durations, loop=0)
        

if __name__ == "__main__":
    timing=None
    mode = "set"
    files=list()
    for arg in sys.argv[1:]:
        if(re.match("[0-9]+d[0-9]+",arg)):
            timing=[int(x) for x in arg.split("d")]
            mode="multiply"
        elif(arg.isnumeric()):
            timing=[int(arg)]
        else:
            files.append(arg)
    if(timing!=None and len(files)):
        for f in files:
            retime_gif(f,timing,mode)
    else:
        input("Error. Pass an image and a timing")
    input("Done")
