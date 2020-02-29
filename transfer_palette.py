from PIL import Image
import os.path
import os
import numpy as np 

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
    image=image.copy()
    data = np.array(image)
    # print(data)
    alpha = data[:,:,3:]
    #print(np.unique(alpha))
    alpha[alpha<=128]=0
    alpha[alpha>128]=255
    alphaonly = data[:,:,3].copy()//255
    result = Image.fromarray(data)
    #print(np.unique(alphaonly))
    #mask = None#Image.fromarray(alphaonly)
    return result, alphaonly
    
def reset_transparency(paletteimage,mask,transparency=255):
    # print("Paletteimage mode:",paletteimage.mode)
    data = np.array(paletteimage)
    # print(data[0,0])
    # print(mask[0,0])
    data = data*mask
    mask = -(mask-1)*transparency
    data = data+mask
    result = Image.fromarray(data,"P")
    # print("Result mode",result.mode)
    result.putpalette(paletteimage.getpalette())
    result.info["transparency"]=transparency
    return result
    
def create_gif_from_folder(foldername,outputname=None,palette=None):
    images = list()
    for file in os.listdir(foldername):
        if file.endswith(".png"):
            im = Image.open(foldername+os.sep+file)
            
            im2, mask=deal_transparency(im)
            im2=im2.convert("RGB")
            palette=remove_unused_color_from_palette(palette)
            images.append(reset_transparency(index_image(im2,palette),mask))

    for im in images:
        im.info['transparency']=None
        del im.info['transparency']
    images[0].save(outputname, "GIF", save_all=True,append_images=images[1:], optimize=False, transparency=255, disposal=2, duration=30, loop=0) 

def create_gif_from_gif(filename,outputname=None,palette=None):
    images = list()
    im = Image.open(filename)
    duration = 30
    try:
        while 1:
            im2=im.convert("RGB")
            images.append(index_image(im2,palette))
            im.seek(im.tell()+1)
            duration = im.info['duration']
    except EOFError:
        pass # end of sequence
    try:
        images[0].save(outputname, "GIF", save_all=True,append_images=images[1:], optimize=True, disposal=2, duration=duration, loop=0)
    except:
        for im in images:
            im.info['transparency']=None
            del im.info['transparency']
            #Transparency has to be deleted because of a bug in PIL. Restore it with change_background.py
        images[0].save(outputname, "GIF", save_all=True,append_images=images[1:], optimize=True, disposal=2, duration=duration, loop=0)
        
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
                create_gif_from_gif(target,tname+"_COL_"+sname+".gif",palette=pal)
except Exception as E:
    print(E)
    import traceback
    traceback.print_exc()
    input("Failure")
    
#input("wait")
    
"""def load_palette(filename):
    im = Image.open(filename)
    pal = im.getpalette()
    print(pal)
    return pal
    #This doesn't work because getpalette doesn't return an useable palette data for quantize..."""