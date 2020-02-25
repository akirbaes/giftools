from PIL import Image
import os.path
import os
from statistics import mode

def get_background_color(image):
    return mode((image.getpixel((0,0)),image.getpixel((-1,0)),image.getpixel((0,-1)),image.getpixel((-1,-1))))
    
def rearange(filename,w1,h1,w2,h2):
    print(filenames)
    image = Image.open(filename)
    width,height = image.width, image.height
    width2 = int(width/w1*w2)
    height2 = int(height/h1*h2)
    cellwidth = int(width/w1)
    cellheight = int(height/h1)
    duration = image.info['duration']
    transparency = image.info.get('transparency',None)
    
    print("Image",width,"x",height)
    results = list()
    
    try:
        while 1:
            bg = get_background_color(image)
            res = image.copy().resize((width2,height2))
            res.paste(bg,(0,0,width2,height2))
            for i in range(w1):
                for j in range(h1):
                    x,y = i*cellwidth,j*cellheight
                    index = i*h1+j
                    x2,y2 = int(index//h2)*cellwidth, (index%h2)*cellheight
                    res.paste(image.copy().crop((x,y,x+cellwidth,y+cellheight)),(x2,y2))
                    
            results.append(res)
            image.seek(image.tell()+1)
    except EOFError:
        pass # end of sequence
        
    folder = os.path.dirname(filename)
    name = os.path.splitext(os.path.basename(filename))[0]
    outputname = folder+os.sep+name+" "+str(w2)+"x"+str(h2)+".gif"
    outputname = filename+" "+str(w2)+"x"+str(h2)+".gif"
    print(outputname)
    if(transparency!=None):
        results[0].save(outputname, "GIF", save_all=True,append_images=results[1:], optimize=False, disposal=2, duration=duration, transparency=transparency, loop=0)
    else:
        results[0].save(outputname, "GIF", save_all=True,append_images=results[1:], optimize=False, disposal=2, duration=duration, loop=0)
        
try:
    if __name__ == "__main__":
        import sys
        
        
        w1,h1,w2,h2 = (int(x) for x in sys.argv[1:5])
        filenames = sys.argv[5:]
        if(w1*h1>w2*h2):
            print("Sheet parts will be lost")
        # elif(w1*h1<w2*h2):
            # print("Empty areas")
        
        for filename in filenames:
            rearange(filename,w1,h1,w2,h2)
            
except Exception as E:
    print(E)
    import traceback
    traceback.print_exc()
    input("Failure")
#input("End")
