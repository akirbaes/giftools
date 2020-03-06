from PIL import Image
import sys
import re
import os
from fractions import Fraction
import numpy as np


def reorder_background(image, background=None):
    #Puts the background color at index 0
    image=image.copy()
    palettedata = image.getpalette()
    if(background==None):
        background_id = get_background_color(image) #must be a palette ID
    else:
        background_id = background
    
    bg_index = background_id*3
    zero_index = 0
    
    zero_color = palettedata[zero_index:zero_index+3]
    background_color = palettedata[bg_index:bg_index+3]
    
    palettedata[zero_index:zero_index+3] = background_color
    palettedata[bg_index:bg_index+3] = zero_color
    
    if(background_id==0):
        return image
    #else:
    #print(list(image.getdata()))
    """data = list(image.getdata())
    data = [x if x!=background_color else "a" for x in data]
    data = [x if x!=0 else background_color for x in data]
    data = [x if x!="a" else 0 for x in data]
    result = Image.fromarray(np.array(data))"""
    data = np.array(image)
    #print(data)
    area = data.copy()
    #I could have swapped it easily using 255 as intermediate value, but then I might lose one palette color
    #So I stock the 0 area in a different array
    if(background_id!=1):
        #Valeur intermédiaire ni 0 ni background_id
        #J'aurai pu utiliser max((background_id-1)%255,(background_id+1)%255)
        area[area!=0]=1
        area[area==0]=background_id
        area[area==1]=0
    else:
        area[area!=0]=2
        area[area==0]=background_id
        area[area==2]=0
    data[data==background_id] = 0
    data+=area
    #print("data",data)
    #print("area",area)
    result = Image.fromarray(data)
    result.putpalette(palettedata)
    
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
            output.append(reorder_background(im,im.info.get("transparency",None)))
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
    if(len(output)>1):
        if(transparencies):
            print(transparencies)
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
