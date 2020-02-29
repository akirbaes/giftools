from PIL import Image
import os.path
import sys
from statistics import mode
def put_background(image, color=(255, 255, 255)):
    background = Image.new('RGB', image.size, color)
    background.paste(image)
    return background
    
def set_transparent(image):
    transparency = mode((image.getpixel((0,0)),image.getpixel((-1,0)),image.getpixel((0,-1)),image.getpixel((-1,-1))))
    image.info["transparency"]=transparency
    
    
    
def generate_gif_from_sheet(inputfile,take_all = 0):
    
    im = Image.open(inputfile).convert("RGB")
    #transparency = im.info['transparency']
    im=im.quantize(colors=256, method=None, palette=None, kmeans=0, dither=0)
    #print(im.palette.getcolor(transparency))
    print(im.mode) #"P"
    print(im.info)
    #del im.info['transparency']
    #print(im.palette.colors) #Empty dictionary
    #trans = im.palette.getcolor(transparency)
    #print("Quantized transparency",im.info['transparency'])
    #print(im.palette.getcolor(transparency))
    #print(im.palette.getdata())
    #print("Trans:",trans)
    W = im.width
    H = im.height
    w = W//3
    h = H//4
    
    frames = list()
    for i in range(3):
        #print((i*w,0,w,(3+take_all)*h))
        fr = im.crop((i*w,0,i*w+w,(3+take_all)*h))
        #fr = fr
        #del fr.info['transparency']
        frames.append(fr)
    
    first_frame = frames[1].copy()
    name = os.path.splitext(os.path.basename(inputfile))[0]
    outputname = name + "_A.gif"
    print(frames)
    #try:
    #print(first_frame.palette.getcolor(transparency))
    transparency = mode((first_frame.getpixel((0,0)),first_frame.getpixel((-1,0)),first_frame.getpixel((0,-1)),first_frame.getpixel((-1,-1))))
    print((first_frame.getpixel((0,0)),first_frame.getpixel((-1,0)),first_frame.getpixel((0,-1)),first_frame.getpixel((-1,-1))),transparency)
    for frame in frames:
        print(frame.width, frame.height)
    first_frame.save(outputname, format="GIF", save_all=True, append_images=frames, optimize=True, transparency=transparency, disposal=2, duration=200, loop=0)
    """except Exception as e:
        print(e)
        for fr in frames:
            del fr.info['transparency']
        first_frame.save(outputname, format="GIF", save_all=True, append_images=frames, optimize=True, disposal=2, duration=200, loop=0)"""
    
if __name__ == "__main__":
    take_all = 0
    if(len(sys.argv)>1):
        if "--all" in sys.argv[1:]:
            take_all = 1
        for arg in sys.argv[1:]:
            generate_gif_from_sheet(arg,take_all)
    else:
        input("Error. Pass a sprite sheet.")
