from PIL import Image
import os.path
import os

"""def load_palette(filename):
    im = Image.open(filename)
    pal = im.getpalette()
    print(pal)
    return pal"""
    
def index_image(image,palette=None):
    return image.quantize(colors=256, method=None, kmeans=0, palette=palette, dither=0)
    
def create_gif_from_folder(foldername,outputname=None,palette=None):
    images = list()
    for file in os.listdir(foldername):
        if file.endswith(".png"):
            im = Image.open(foldername+os.sep+file)
            images.append(index_image(im,palette))

    images[0].save(outputname, "GIF", save_all=True,append_images=images[1:], optimize=True, disposal=2, duration=30, loop=0) #, transparency=0

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
            del im.info['transparency']
        images[0].save(outputname, "GIF", save_all=True,append_images=images[1:], optimize=True, disposal=2, duration=duration, loop=0)
        #images[0].save(outputname, "GIF", save_all=True,append_images=images[1:], optimize=True, disposal=2, duration=duration, loop=0, transparency=0)
        
try:
    if __name__ == "__main__":
        import sys
        if(len(sys.argv)>1):
            source=sys.argv[1]
            target=sys.argv[2]
                
            #pal = load_palette(source)
            pal = Image.open(source)
            
            name,extension = os.path.splitext(source)
            if(os.path.isdir(target)):
                tname = os.path.basename(target)
                create_gif_from_folder(target,name+"_EXT_%s.gif"%tname,palette=pal)
            else:
                tname = os.path.splitext(target)[0]
                sname = os.path.splitext(os.path.basename(source))[0]
                create_gif_from_gif(target,tname+"_COL_"+sname+".gif",palette=pal)
except Exception as E:
    input("Failure")
    raise E