from PIL import Image
import os.path
import sys
from statistics import mode
import numpy as np

def get_outline_color(image):
    bgc = get_background_color(image)
    colors = list()
    for j in range(image.height):
        for i in range(image.width):
            col = image.getpixel((i,j))
            if(col)!=bgc:
                colors.append(col)
                break
    print(colors)
    return mode(colors)

def get_background_color(image):
    return mode((image.getpixel((0,0)),image.getpixel((-1,0)),image.getpixel((0,-1)),image.getpixel((-1,-1))))

def reorder_background(image):
    image=image.copy()
    palettedata = image.getpalette()
    background_id = get_background_color(image) #must be a palette ID
    
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
    
def set_rgb_background(image, color=(255, 255, 255), alpha = 255):
    #Image must be RGB at least
    #From stackoverflow
    image=image.convert("RGBA")
    image.palette = None
    data=np.array(image)
    r,g,b,a = data.T
    tr,tg,tb,ta = get_background_color(image)
    background_area = (r==tr) & (b==tb) & (g==tg) 
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
    """
    palettedata = bytearray(image.palette.tobytes())
    background_color = get_background_color(image) #must be a palette ID
    palettedata[background_color*3:background_color*3+3] = color
    image.putpalette(palettedata)"""
    return image
    
def set_background(image,color=(255,255,255), set_transparent = False):
    print("Mode:",image.mode)
    if(image.mode=="P"):
        return set_paletted_background(image,color,set_transparent)
    else:
        return set_rgb_background(image,color,(not set_transparent)*255)
    
def color_background(filename, background_color):
    im = Image.open(filename)
    output = list()
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
            #out.show()
            im.seek(im.tell()+1)
            duration = im.info['duration']
    except EOFError:
        pass # end of sequence
    
    outname = generate_outname(filename,background_color)
    if(len(output)>1):
        output[0].save(outname, save_all=True,append_images=output[1:], optimize=False, disposal=2, duration=duration, loop=0)
    else:
        output[0].save(outname)


def generate_outname(filename,color=None):
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
        parts[-2] = parts[-2][:beginnum]+colorcode+parts[-2][beginnum+7:]
    except Exception as E:
        parts[-2]+=colorcode
    return ".".join(parts)

def remove_background(filename):
    im = Image.open(filename)
    imrgb=im.copy().convert("RGB")
    background_color = get_background_color(imrgb) #to not have palette ID, but an RGB value
    #transparency = get_background_color(im) #get the palette ID if necessary
    #NO MORE USEFUL: will be reordered frame-by-frame
    output = list()
    try:
        while 1:
            if(im.mode=="P"):
                out=reorder_background(im)
                #im.copy() #[TODO]: put the "background" color at the same index for all frames
                #out = set_background(im,background_color,set_transparent=True) #This would be useless as only the index is taken in account when saving
                #Re-indexing the colors with "quantize" will lose the small color difference areas
            else:
                out = set_background(im,background_color,set_transparent=True) #If several frames have different backgrounds
            #out.show()
            output.append(out)
            """if(im0.mode=="P"):
                out=out.quantize(colors=256, method=2)
            output.append(set_background(im,background_color).convert("P"))
            """
            im.seek(im.tell()+1)
            duration = im.info['duration']
    except EOFError:
        pass # end of sequence
        
    outname = generate_outname(filename,None)
    
    if(len(output)>1):
        output[0].save(outname, save_all=True,append_images=output[1:], optimize=False, disposal=2, duration=duration, loop=0, transparency=0)
    else:
        if(output[0].mode=="P"):
            print("Output as",outname,"transparency=",0)
            output[0].save(outname,transparency=0)
        else:
            output[0].save(outname)
        
try:
    if __name__ == "__main__":
        remove = True
        background_color = tuple()
        print(sys.argv[1:])
        if "--remove" in sys.argv:
            remove = True
        if "--color" in sys.argv:
            remove = False
        if "--outline" in sys.argv:
            remove = False
            background_color = "outline"
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
                else:
                    if(remove):
                        remove_background(arg)
                    else:
                        color_background(arg,background_color)
        else:
            input("Error. Pass an image")
        #input("Done")
except Exception as E:
    print(E)
    import traceback
    traceback.print_exc()
    input("Failure")