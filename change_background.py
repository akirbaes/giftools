from PIL import Image
import os.path
import sys
from statistics import mode
import numpy as np
from gif_manips import get_outline_color, get_background_color, swap_palette_colors


def reorder_background(image, background=None):
    #Puts the background color at index 0
    image=image.copy()
    if(background==None):
        background_id = get_background_color(image) #must be a palette ID
    else:
        background_id = background
    return swap_palette_colors(image,0,background_id)
    return result
    
def set_rgb_background(image, color=(255, 255, 255), alpha = 255):
    #Image must be RGB at least
    #From stackoverflow
    image=image.convert("RGBA")
    image.palette = None
    data=np.array(image)
    r,g,b,a = data.T
    tr,tg,tb,ta = get_background_color(image)
    background_area = (r==tr) & (b==tb) & (g==tg) 
    print(color,(alpha,))
    data[..., :][background_area.T] = color+(alpha,)
    
    background = Image.fromarray(data)
    return background
    
def set_paletted_background(image,color=(255,255,255), transparent = False):
    #For paletted images to not collapse similar colors
    print(color)
    image=image.copy() #For some strange reason it reverted to original palette without this
    palettedata = image.getpalette()
    background_color = get_background_color(image) #must be a palette ID
    if(transparent):
        image.info["transparency"]=background_color
    else:
        image.info["transparency"]=background_color
        del image.info["transparency"]
    index = background_color*3
    palettedata[index:index+3] = list(color)
    #print(len(palettedata)/3)
    #palettedata = [255,0,0]*256
    #image.show()
    image.putpalette(palettedata)
    return image
    
def set_background(image,color=(255,255,255), set_transparent = False):
    print("Mode:",image.mode)
    if(image.mode=="P"):
        return set_paletted_background(image,color,set_transparent)
    else:
        return set_rgb_background(image,color,(not set_transparent)*255)
    
def generate_outname(filename,color=None, fill=False):
    parts=filename.split(".")
    nameend = parts[-2] #-1 should be the extension
    if(color==None):
        colorcode = "#_empty"
    else:
        colorcode = '#%02x%02x%02x' % color
        
    try:
        beginnum = nameend.index("#")
        if(nameend[beginnum:beginnum+7]=="#_empty"):
            pass
        else:
            old_hexa = int(nameend[beginnum+1:beginnum+6],16)
        if(fill and nameend[beginnum-2:beginnum]!="_f"):
            colorcode="_f"+colorcode
        parts[-2] = parts[-2][:beginnum]+colorcode+parts[-2][beginnum+7:]
    except Exception as E:
        parts[-2]+=fill*"_f"+colorcode
    return ".".join(parts)

def remove_all_background(filename):
    im = Image.open(filename)
    output = list()
    durations = list()
    disposals = list()
    try:
        while 1:
            if(im.mode=="P"):
                out=reorder_background(im) #Put the background color at index 0
            else:
                #RGB mode (i presume)
                background_color = get_background_color(im.convert("RGB")) #not a palette ID, but an RGB value
                out = set_background(im,background_color,set_transparent=True) #If several frames have different backgrounds?
            output.append(out)
            
            try:
                durations.append(im.info["duration"])
                disposals.append(im.disposal_method)
            except:
                pass
            im.seek(im.tell()+1)
    except EOFError:
        pass # end of sequence
        
    outname = generate_outname(filename,None)
    
    if(len(output)>1):
        output[0].save(outname, save_all=True,append_images=output[1:], optimize=False, disposal=2, duration=durations, loop=0, transparency=0)
    else:
        if(output[0].mode=="P"):
            print("Output as",outname,"transparency=",0)
            output[0].save(outname,transparency=0)
        else:
            output[0].save(outname)

def color_all_background(filename, background_color):
    im = Image.open(filename)
    output = list()
    durations = list()
    disposals = list()
    try:
        while 1:
            #im.show()
            if(background_color=="outline"):
                color = get_outline_color(im.copy().convert("RGB"))
                r,b,g= color
                color = r-(r==255)+(r<255),g,b
                out=set_background(im,color)
            else:
                out=set_background(im,background_color)
            output.append(out)
            
            try:
                durations.append(im.info["duration"])
                disposals.append(im.disposal_method)
            except:
                pass
            im.seek(im.tell()+1)
    except EOFError:
        pass # end of sequence
    
    outname = generate_outname(filename,background_color)
    if(len(output)>1):
        output[0].save(outname, save_all=True,append_images=output[1:], optimize=False, disposal=2, duration=durations, loop=0)
    else:
        output[0].save(outname)

def fill_all_background(filename,color=None,transparent=True):
    im = Image.open(filename)
    output = list()
    durations = list()
    disposals = list()
    try:
        while 1:
            if(im.mode=="P"):
                out=fill_paletted_background(im) #Put the background color at index 0
            else:
                out=fill_rgb_background(im)
            output.append(out)
            
            try:
                durations.append(im.info["duration"])
                disposals.append(im.disposal_method)
            except:
                pass
            im.seek(im.tell()+1)
    except EOFError:
        pass # end of sequence
        
    outname = generate_outname(filename,None,True)
    
    if(len(output)>1):
        output[0].save(outname, save_all=True,append_images=output[1:], optimize=False, disposal=2, duration=durations, loop=0, transparency=0)
    else:
        if(output[0].mode=="P"):
            print("Output as",outname,"transparency=",0)
            output[0].save(outname,transparency=0)
        else:
            output[0].save(outname)

def fill_paletted_background(image, color=None):
    image=image.copy() #For some strange reason it reverted to original palette without this
    
    #Determine the filling color: unused color
    palettedata = image.getpalette()
    data = np.array(image)
    uniquecolors = np.unique(data)
    for i in range(256):
        if(255-i not in uniquecolors):
            new_bg = 255-i
            break
            #Will be set at 0 later
    
    old_bg = get_background_color(image)
    width,height = image.size
    coords = list()
    
    for j in range(height):
        coords.append((0,j))
        coords.append((width-1,j))
    for i in range(1,width-1,1):
        coords.append((i,0))
        coords.append((i,height-1))
    
    while(coords):
        x,y = coords.pop()
        if(0<=x<width and 0<=y<height):
            #print("Test:",x,y,'<',data.shape) #X and Y are to call in Y,X order
            if(data[y][x]==old_bg):
                data[y][x]=new_bg
                coords.append((x,y-1))
                coords.append((x,y+1))
                coords.append((x-1,y))
                coords.append((x+1,y))
                
    result = Image.fromarray(data)
    result.putpalette(palettedata)
    
    return reorder_background(result) #puts back the background color at index 0
    
def fill_rgb_background(image, color=None):
    image=image.copy().convert("RGBA")
    
    data = np.array(image)
    old_bg = get_background_color(image)
    width,height = image.size
    coords = list()
    
    for j in range(height):
        coords.append((0,j))
        coords.append((width-1,j))
    for i in range(1,width-1,1):
        coords.append((i,0))
        coords.append((i,height-1))
    
    while(coords):
        x,y = coords.pop()
        if(0<=x<width and 0<=y<height):
            #print("Test:",x,y,'<',data.shape) #X and Y are to call in Y,X order
            if(np.array_equal(data[y][x],old_bg) and data[y][x][3]!=0):
                data[y][x][3]=0
                coords.append((x,y-1))
                coords.append((x,y+1))
                coords.append((x-1,y))
                coords.append((x+1,y))
                
    result = Image.fromarray(data)
    
    return result #puts back the background color at index 0
    
try:
    if __name__ == "__main__":
        remove = True
        fill = False
        background_color = tuple()
        print(sys.argv[1:])
        if "--remove" in sys.argv:
            remove = True
        if "--color" in sys.argv:
            remove = False
        if "--outline" in sys.argv:
            remove = False
            background_color = "outline"
        if "--fill" in sys.argv:
            fill = True
            
        if(len(sys.argv)>1):
            
            for arg in sys.argv[1:]:
                if(arg.isnumeric()):
                    background_color+=int(arg),
                elif arg=="--remove":
                    remove = True
                elif arg=="--color":
                    remove=False
                elif arg=="--outline":
                    remove=False
                    background_color = "outline"
                elif arg=="--fill":
                    fill=True
                else:
                    if(fill):
                        fill_all_background(arg)
                    elif(remove):
                        remove_all_background(arg)
                    else:
                        color_all_background(arg,background_color)
        else:
            input("Error. Pass an image")
        #input("Done")
except Exception as E:
    print(E)
    import traceback
    traceback.print_exc()
    input("Failure")