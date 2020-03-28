from PIL import Image
import PIL
import os.path
import os
import numpy as np 
alpha_limit = 130
from statistics import mode

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
    if(image.mode!="P"):
        input("Wrong input type")
    image=image.copy()
    tr = image.info.get("transparency",None)
    br = image.info.get("background",None)
    data = np.array(image)
    #print(br,tr,data) #Heavily optimised gifs will have issues
    #mask = np.where(data==tr,0,1)
    if(tr==0):
        data[data!=tr]=1
    else:
        data[data!=tr]=0
        data[data==tr]=2
        data[data==0]=1
        data[data==2]=0
    print("Transparency mask:",data)
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


def index_rgb_and_alpha(im,palette=None,transparency=0):       
    if(im.mode=="RGB" or im.mode=="RGBA"):
        im2, mask = reduce_and_get_rgba_transparency_area(im)
        im2=im.convert("RGB")
    elif(im.mode=="P"):
        mask = get_palette_transparency_area(im)
        im2=im.convert("RGB")
        #im2=im
    else:
        print("Unhandled image mode:",im.mode)
    
    im2 = index_image(im2,palette)
    im2.info["transparency"]=None
    #im2.show()
    if not(mask is None):
        tr=255
        tr=unused_color(palette)
        im2=reset_transparency(im2,mask,tr)
        im2=swap_palette_colors(im2,tr,transparency) 
        # im2.show()
        ##This created a bug where an existing color would become the "background" transparency color
    return im2
    
    
    

#once = 0

def swap_palette_colors(image, source_id=None, target_id = 255):
    #global once
    #Puts the source_id color at index target_id
    image=image.copy()
    # if(once==0):
    #image.show()
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
    """
    intermediate=unused_color(image)
    print(area_source[area_source!=source_id])
    area_source[area_source!=source_id]=intermediate
    area_source[area_source==source_id]=target_id
    area_source[area_source==intermediate]=0
        
    area_target[area_target!=target_id]=intermediate
    area_target[area_target==target_id]=source_id
    area_target[area_target==intermediate]=0
    
    data[data==source_id]=0
    data[data==target_id]=0
    data+=area_source+area_target
    """
    #anti_source_mask = np.where(data==source_id,0,1)
    #anti_target_mask = np.where(data==target_id,0,1)
    source_mask = np.where(data==source_id,1,0)
    target_mask = np.where(data==target_id,1,0)
    #data*=anti_source_mask
    #data*=anti_target_mask
    data = np.where(source_mask==1,target_id,data)
    data = np.where(target_mask==1,source_id,data)
    # data[source_mask]=target_id
    # data[target_mask]=source_id
    
    #Unsafe?: doesn't work
    
    result = Image.fromarray(data)
    result.putpalette(palettedata)
    # if(once==0):
    #result.show()
    # once+=1
    return result
    