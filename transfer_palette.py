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
    
from gif_manips import remove_unused_color_from_palette, index_rgb_and_alpha

def create_gif_from_folder(foldername,outputname=None,palette=None,allow_dropped_frames=True):
    images = list()
    durations = list()
    previous_time = 0
    if(palette!=None):
        palette=remove_unused_color_from_palette(palette) #this actually ends up mangling the colors, so only do it once
        #[TODO] Look at the colors of all the frames and not only frame 1
    borrowed_time = 0
    for file in os.listdir(foldername):
        if file.endswith(".png") or file.endswith(".gif"):
            im = Image.open(foldername+os.sep+file)
            
            try:
            
                time = int(file.split(".")[-2])
                if(time!=0):
                    
                    duration = time-previous_time
                    if(allow_dropped_frames):
                        duration-=borrowed_time
                        if(duration==0):
                            borrowed_time=0
                            continue
                        elif(duration==10):
                            borrowed_time = 20-duration
                    else:
                        if(duration==10):
                            duration=20
                    durations.append(duration)
                    previous_time = time
            except Exception as e:
                print(e)
            images.append(index_rgb_and_alpha(im,palette,0))
            #Puts the transparent color at index 255 so that I can simply pass 255 as transparency
            #It seems PIL reserves 255 for transparency anyway
            #Edit: but then optimize=True will make it so that there are less than 128 colors sometimes... so 0 is a safer bet
    
    durations+=[20]*(len(images)-len(durations))
    #durations[-1]=1600
    for im in images:
        try:
            del im.info['transparency']
        except: pass
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
        images[0].save(outputname, "GIF", save_all=True,append_images=images[1:], disposal=2, optimize=False, duration=durations, transparency=0, loop=0)
    else:
        images[0].save(outputname, "GIF", optimize=False, transparency=0)
        
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
    