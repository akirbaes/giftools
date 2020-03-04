from PIL import Image
import os.path
import sys
import statistics
import numpy as np
    
def get_background_color(image):
    return statistics.mode((image.getpixel((0,0)),image.getpixel((-1,0)),image.getpixel((0,-1)),image.getpixel((-1,-1))))
    
def rindex(lst, value):
    #https://stackoverflow.com/questions/522372/finding-first-and-last-index-of-some-value-in-a-list-in-python
    for i, v in enumerate(reversed(lst)):
        if v == value:
            return len(lst) - i - 1  # return the index in the original list
    return None    
    
def generate_outname(filename,crop,outlines):
    name,ext = os.path.splitext(filename)
    if("+" in name):
        plus = name.rindex("+")
        c=0
        numbers=0
        if(len(name)>plus):
            c = name[plus+1]=="c"
            
        for x in range(4):
            index = plus+c+x+1
            if(index<len(name) and name[index].isnumeric()):
                numbers+=1
            else:
                break
        if(numbers):
            if(not crop):
                #Add more
                outlines += int(name[plus+c+1:plus+c+numbers+1])
            crop = crop or c
            insertion = "+"+crop*"c"+str(outlines)
            return name[:plus]+insertion+name[plus+c+numbers+1:]+ext
    insertion = "+"+crop*"c"+str(outlines)
    return name+insertion+ext

def crop_image(filename,outlines=0,crop=True):
    im = Image.open(filename)
    width,height=im.size
    if(crop):
        left,top,right,bottom = width,height,0,0
        try:
            while 1:
                bg = get_background_color(im)
                data = np.array(im)
                
                for x in range(width):
                    for y in range(height):
                        if(data[y][x]!=bg):
                            left = min(left,x)
                            right = max(right,x)
                            top = min(top,y)
                            bottom = max(bottom,y)
                im.seek(im.tell()+1)
        except EOFError:
            pass # end of sequence
        im = Image.open(filename)
    else:
        left,top,right,bottom = 0,0,width,height
        
    new_width = right-left+outlines*2
    new_height = bottom-top+outlines*2
    output = list()
    transparency = None
    transparencies = list()
    durations = list()
    disposals = list()
    try:
        while 1:
            bg = get_background_color(im)
            out = im.copy()
            out = out.resize((new_width,new_height),resample=Image.NEAREST)
            out.paste(bg,(0,0,new_width,new_height))
            out.paste(im,(-left+outlines,-top+outlines))
            
            transparency = im.info.get('transparency', transparency)
            transparencies.append(im.info.get('transparency', None))
            duration = im.info.get('duration', None)
            if(duration is not None):
                durations.append(duration)
            disposal = im.disposal_method
            if(disposal is not None):
                disposals.append(disposal)
            output.append(out)
            
            im.seek(im.tell()+1)
    except EOFError:
        pass # end of sequence
    print(transparencies)
    outname = generate_outname(filename,crop,outlines)
    if(len(output)>1):
        if(transparency!=None):
            output[0].save(outname, save_all=True,append_images=output[1:], optimize=False, disposal=disposals, transparency=transparency, duration=durations, loop=0)
        else:
            output[0].save(outname, save_all=True,append_images=output[1:], optimize=False, disposal=disposals, duration=durations, loop=0)
            
    else:
        if(transparency!=None):
            output[0].save(outname, transparency=transparency)
        else:
            output[0].save(outname)
    
if __name__ == "__main__":
    import sys
    if(len(sys.argv)>1):
        file = None
        outline = 1
        crop=False
        
        files = list()
        for arg in sys.argv[1:]:
            if(arg.isnumeric()):
                outline = int(arg)
            elif(arg=="--crop"):
                crop=True
            else:
                files.append(arg)
        for file in files:
            crop_image(file,outline,crop)
        if not files:
            exit("Please provide a file!")
    else:
        input("Usage: python crop_image.py [int:outline] [--crop] files")
        