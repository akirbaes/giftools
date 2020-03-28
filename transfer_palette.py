from PIL import Image
import PIL
import os.path
import os
import numpy as np 
alpha_limit = 130
from statistics import mode
#Transfers one image's palette to another.
#Usage: python transfer_palette.py sourceImage targetImage
#target can be a folder full of pngs. It will compile them into a gif.

#You can also use generate_palette.py to create a bash script that makes the argument pass easier with drag-and-drop.
    
def index_image(image,palette=None):
    #print(palette.mode)
    if(palette!=None):
        #255: one less to allow one transparency color
        return image.quantize(colors=255, method=2, kmeans=0, palette=palette, dither=0)
    else:
        return image.quantize(colors=255, method=2, kmeans=0, dither=0)

def remove_unused_color_from_palette(image):
    #Will also mess up the image, but no care for it for now
    #[TODO]Gif:do it for every frame and group all the colors in one image
    palettedata = image.getpalette()
    data = np.array(image)
    
    if(image.info.get("transparency",None) != None):
        #Remove transparency from frame
        tv = image.info.get("transparency")
        # print("Transparent color detected in palette",tv)
        fill = int(tv==0)
        data[data==tv]=fill
        # print("Filled with",fill)
        #trgb = palettedata[tv*3:tv*3+3]
        #palettedata[tv*3:tv*3+3] = (0,0,0)
        
    uniquecolors = np.unique(data)
    uniquergb = [tuple(palettedata[x*3:x*3+3]) for x in uniquecolors]
    palettesize = len(uniquergb)
    newpalette = list()
    for rgb in uniquergb:
        newpalette.extend(rgb)
    while len(newpalette)<3*256:
        newpalette.extend(min(uniquergb))
    
    #newpalette[0:palettesize] are the used colors
    
    # print("Unique colors:",len(uniquecolors))
    # print(uniquecolors)
    image.info["transparency"]=255
    image.putpalette(newpalette)
    # print(image.getpalette())
    # print(len(image.getpalette()))
    #image.show()
    return image
"""
def get_outline_color(image):
    bgc = get_background_color(image)
    colors = list()
    for j in range(image.height):
        for i in range(image.width):
            col = image.getpixel((i,j))
            if(col)!=bgc:
                colors.append(col)
                break
    # print(colors)
    return mode(colors)
    
def get_background_color(image):
    return mode((image.getpixel((0,0)),image.getpixel((-1,0)),image.getpixel((0,-1)),image.getpixel((-1,-1))))
"""
def unused_color(image):
    #Returns unused palette index
    data = np.array(image)
    uniquecolors = set(np.unique(data))
    for i in range(256):
        if(i not in uniquecolors):
            return i
    return None

def reduce_and_get_rgba_transparency_area(image):
    #Remove alpha transparency and makes a binary transparency mask
    if(image.mode=="RGB"):
        image=image.convert("RGBA")
        #return image, None
    image=image.copy()
    data = np.array(image)
    alpha = data[:,:,3:]
    alpha[alpha<=alpha_limit]=0
    #Here: change data's rgb for alpha>alpha_limit
    alpha[alpha>alpha_limit]=255
    alphaonly = data[:,:,3].copy()//255
    result = Image.fromarray(data)
    #print(np.unique(alphaonly))
    return result, alphaonly

def get_palette_transparency_area(image):
    image=image.copy()
    tr = image.info.get("transparency",None)
    
    data = np.array(image)
    if(tr==0):
        data[data!=tr]=1
    else:
        data[data!=tr]=0
        data[data==tr]=2
        data[data==0]=1
        data[data==2]=0
    # print("Transparency mask:",data)
    return data
    
def reset_transparency(paletteimage,mask,transparency=255):
    # print("Paletteimage mode:",paletteimage.mode)
    data = np.array(paletteimage)
    data = data*mask
    mask = -(mask-1)*transparency
    data = data+mask
    result = Image.fromarray(data,"P")
    result.putpalette(paletteimage.getpalette())
    result.info["transparency"]=transparency
    return result
    
#once = 0

def swap_palette_colors(image, source_id=None, target_id = 255):
    #global once
    #Puts the source_id color at index target_id
    image=image.copy()
    # if(once==0):
        # image.show()
    palettedata = image.getpalette()
    if(source_id==None):
        source_id = get_background_color(image) #must be mode P to give an ID
    else:
        source_id = source_id
    if(source_id==target_id):
        return image
        
    source_index = source_id*3
    target_index = target_id*3
    
    target_color = palettedata[target_index:target_index+3]
    source_color = palettedata[source_index:source_index+3]
    palettedata[target_index:target_index+3] = source_color
    palettedata[source_index:source_index+3] = target_color
    
    data = np.array(image)
    area_source = data.copy()
    area_target = data.copy()
    
    # intermediate = (source_id+1+(target_id==source_id+1))%256 #Will ruin the intermediate color
    intermediate=unused_color(image)
    
    area_source[area_source!=source_id]=intermediate
    area_source[area_source==source_id]=target_id
    area_source[area_source==intermediate]=0
        
    area_target[area_target!=target_id]=intermediate
    area_target[area_target==target_id]=source_id
    area_target[area_target==intermediate]=0
    
    data[data==source_id]=0
    data[data==target_id]=0
    data+=area_source+area_target
    
    ##area_target[[area_target==target_id]],area_source[[area_source==source_id]]=source_id,target_id
    #Unsafe: doesn't work
    
    result = Image.fromarray(data)
    result.putpalette(palettedata)
    # if(once==0):
        # result.show()
    # once+=1
    return result
    
def index_rgb_and_alpha(im,palette=None,transparency=0):       
    if(im.mode=="RGB" or im.mode=="RGBA"):
        im2, mask = reduce_and_get_rgba_transparency_area(im)
        im2=im.convert("RGB")
    elif(im.mode=="P"):
        mask = get_palette_transparency_area(im)
        im2=im.convert("RGB")
    else:
        print("Unhandled image mode:",im.mode)
    
    im2 = index_image(im2,palette)
    if not(mask is None):
        #tr=unused_color(im2)
        tr=255
        im2=reset_transparency(im2,mask,tr)
        im2=swap_palette_colors(im2,tr,transparency) 
        ##This created a bug where an existing color would become the "background" transparency color
    return im2

def create_gif_from_folder(foldername,outputname=None,palette=None):
    images = list()
    durations = list()
    previous_time = 0
    if(palette!=None):
        palette=remove_unused_color_from_palette(palette) #this actually ends up mangling the colors, so only do it once
        #[TODO] Look at the colors of all the frames and not only frame 1
    for file in os.listdir(foldername):
        if file.endswith(".png") or file.endswith(".gif"):
            im = Image.open(foldername+os.sep+file)
            
            try:
                time = int(foldername.split(".")[-1])
                if(time!=0):
                    durations.append(max(time-previous_time,20))
            except:
                pass
            images.append(index_rgb_and_alpha(im,palette,0))
            #Puts the transparent color at index 255 so that I can simply pass 255 as transparency
            #It seems PIL reserves 255 for transparency anyway
    
    durations+=[20]*(len(images)-len(durations))
    #durations[-1]=1600
    for im in images:
        del im.info['transparency']
    print(len(images),len(durations))
    print(durations)
    #optimize=True will only try to reduce the size of the palette
    images[0].save(outputname, "GIF", save_all=True,append_images=images[1:], optimize=True, tranparency=0,disposal=2, duration=durations, loop=0) 

def create_gif_from_image(filename,outputname=None,palette=None):
    im = Image.open(filename)
    
    if(palette!=None):
        palette=remove_unused_color_from_palette(palette) #this actually ends up mangling the colors, so only do it once
    images = list()
    durations = list()
    disposals = list()
    transparency = list()
    try:
        while 1:
            images.append(index_rgb_and_alpha(im,palette,0))
            
            try:
                #transparency.append(im.info.get('transparency',255))
                durations.append(im.info["duration"])
                disposals.append(im.disposal_method)
                # del im.info["transparency"]
            except Exception as e:
                durations=None
                disposals=None
                
            im.seek(im.tell()+1)
    except EOFError:
        pass # end of sequence
    
    if(len(images)>1):
        print(transparency)
        images[0].save(outputname, "GIF", save_all=True,append_images=images[1:], disposal=2, optimize=True, duration=durations, transparency=0, loop=0)
    else:
        images[0].save(outputname, "GIF", optimize=False, transparency=255)
        
try:
    if __name__ == "__main__":
        import sys
        if(len(sys.argv)>1):
            source=sys.argv[1]
            target=sys.argv[2]
                
            pal = Image.open(source)
            
            if(pal.mode!="P"):
                print("Source is not palleted image: quantizing")
                pal = pal.quantize(colors=256, method=None, kmeans=0, palette=None, dither=0)
            else:
                pass
                # print("Source image palette:",pal.getpalette())
                # print("Source has transparency:",pal.info.get("transparency",None))
            name,extension = os.path.splitext(source)
            if(os.path.isdir(target)):
                tname = os.path.basename(target)
                create_gif_from_folder(target,name+"_EXT_%s.gif"%tname,palette=pal)
            else:
                tname = os.path.splitext(target)[0]
                sname = os.path.splitext(os.path.basename(source))[0]
                create_gif_from_image(target,tname+"_COL_"+sname+".gif",palette=pal)
except Exception as E:
    print(E)
    import traceback
    traceback.print_exc()
    input("Failure")
    