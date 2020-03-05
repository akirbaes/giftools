from PIL import Image
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
    return image.quantize(colors=256, method=2, kmeans=0, palette=palette, dither=0)

def remove_unused_color_from_palette(image):
    #Will also mess up the image, but no care for it for now
    #Gif:do it for every frame and group all the colors in one image
    palettedata = image.getpalette()
    data = np.array(image)
    
    # print(image.getpalette())
    # print(len(image.getpalette()))
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
        newpalette.extend(uniquergb[0])
    
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
    
def deal_transparency(image):
    if(image.mode=="RGB"):
        image=image.convert("RGBA")
        #return image, None
    image=image.copy()
    data = np.array(image)
    # print(data)
    print(image.mode)
    print(data[0][0])
    alpha = data[:,:,3:]
    #print(np.unique(alpha))
    alpha[alpha<=alpha_limit]=0
    alpha[alpha>alpha_limit]=255
    alphaonly = data[:,:,3].copy()//255
    result = Image.fromarray(data)
    #print(np.unique(alphaonly))
    #mask = None#Image.fromarray(alphaonly)
    return result, alphaonly

def unused_color(image):
    data = np.array(image)
    uniquecolors = set(np.unique(data))
    print(uniquecolors)
    for i in range(256):
        if(i not in uniquecolors):
            # print("Unused color:",i)
            # input()
            return i
    return None

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
    # print(data[0,0])
    # print(mask[0,0])
    # print("Data:",data)
    # print("Mask:",mask)
    data = data*mask
    mask = -(mask-1)*transparency
    data = data+mask
    result = Image.fromarray(data,"P")
    # print("Result mode",result.mode)
    result.putpalette(paletteimage.getpalette())
    result.info["transparency"]=transparency
    return result
    

def swap_palette_colors(image, source_id=None, target_id = 0):
    #Puts the source_id color at index target_id
    image=image.copy()
    palettedata = image.getpalette()
    if(source_id==None):
        source_id = get_background_color(image) #must be a palette ID
    else:
        source_id = source_id
    
    source_index = source_id*3
    target_index = target_id*3
    
    target_color = palettedata[target_index:target_index+3]
    source_color = palettedata[source_index:source_index+3]
    
    palettedata[target_index:target_index+3] = source_color
    palettedata[source_index:source_index+3] = target_color
    
    if(source_id==target_id):
        return image
    data = np.array(image)
    area_source = data.copy()
    area_target = data.copy()
    
    intermediate = (source_id+1+(target_id==source_id+1))%256
    
    #if(source_id!=0):
    area_source[area_source!=source_id]=intermediate
    area_source[area_source==source_id]=target_id
    area_source[area_source==intermediate]=0
        
    area_target[area_target!=target_id]=intermediate
    area_target[area_target==target_id]=source_id
    area_target[area_target==intermediate]=0
    
    
    data[data==source_id]=0
    data[data==target_id]=0
    data+=area_source+area_target
    
    result = Image.fromarray(data)
    result.putpalette(palettedata)
    
    return result
    
def create_gif_from_folder(foldername,outputname=None,palette=None):
    images = list()
    durations = list()
    previous_time = 0
    if(palette!=None):
        palette=remove_unused_color_from_palette(palette) #this actually ends up mangling the colors, so only do it once
    for file in os.listdir(foldername):
        if file.endswith(".png") or file.endswith(".gif"):
            im = Image.open(foldername+os.sep+file)
            
                
            try:
                time = int(foldername.split(".")[-1])
                if(time!=0):
                    durations.append(max(time-previous_time,20))
            except:
                pass
                
            if(im.mode=="RGB" or im.mode=="RGBA"):
                im2, mask=deal_transparency(im)
                im2=im.convert("RGB")
            elif(im.mode=="P"):
                mask = get_palette_transparency_area(im)
                im2=im.convert("RGB")
            else:
                print("Unhandled image mode:",im.mode)
                
            #palette=remove_unused_color_from_palette(palette) #this actually ends up mangling the colors
            im2 = index_image(im2,palette)
            tr=unused_color(im2)
            if not(mask is None):
                im2=reset_transparency(im2,mask,tr)
                im2=swap_palette_colors(im2,tr,0)
            images.append(im2)
    
    durations+=[20]*(len(images)-len(durations))
    for im in images:
        im.info['transparency']=None
        del im.info['transparency']
    print(len(images),len(durations))
    print(durations)
    images[0].save(outputname, "GIF", save_all=True,append_images=images[1:], optimize=False, transparency=0, disposal=2, duration=durations, loop=0) 

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
            if(im.mode=="P"):
                mask = get_palette_transparency_area(im)
            else:
                im, mask = deal_transparency(im)
            # palette=remove_unused_color_from_palette(palette)
            im2=index_image(im.convert("RGB"),palette)
            tr=unused_color(im2)
            # print("Mode:",im.mode)
            # input(str(mask))
            if(mask is not None):
                im2=reset_transparency(im2, mask,tr)
                im2=swap_palette_colors(im2,tr,0)
            images.append(im2)
            
            try:
                #transparency.append(im.info.get('transparency',transparency))
                #print("tp",transparency)
                durations.append(im.info["duration"])
                disposals.append(im.disposal_method)
                # del im.info["transparency"]
            except Exception as e:
                # print("Exception",e)
                durations=None
                disposals=None
                
            im.seek(im.tell()+1)
    except EOFError:
        pass # end of sequence
    
    if(len(images)>1):
        print(transparency)
        #if(len(transparency)!=0):
        #    transparency=get_background_color(images[0]) #or rather, use the mask created earlier
        images[0].save(outputname, "GIF", save_all=True,append_images=images[1:], optimize=False, duration=durations, transparency=0, loop=0)
    else:
        #if(len(transparency)!=0 and transparency[0]!=None):
        images[0].save(outputname, "GIF", optimize=False, transparency=0)
        # else:
            # images[0].save(outputname, "GIF", optimize=False)
        
try:
    if __name__ == "__main__":
        import sys
        if(len(sys.argv)>1):
            source=sys.argv[1]
            target=sys.argv[2]
                
            #pal = load_palette(source)
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
    
"""def load_palette(filename):
    im = Image.open(filename)
    pal = im.getpalette()
    print(pal)
    return pal
    #This doesn't work because getpalette doesn't return an useable palette data for quantize..."""