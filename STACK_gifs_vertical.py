from PIL import Image
import os.path
import os
from gif_manips import index_rgb_and_alpha as index_rgb_alpha
BGCOLOR = (50,50,50,0)
HOR = 0
VER = 1
DEFAULT=VER

def compute_lcm(x, y):
   # choose the greater number
   if x > y:
       greater = x
   else:
       greater = y
   while(True):
       if((greater % x == 0) and (greater % y == 0)):
           lcm = greater
           break
       greater += 1
   return lcm

def stack_gifs_vh(filenames,direction=HOR,centering="center"):
    print(filenames)
    images = list()
    width = 0
    height = 0
    lengths = list()
    total_length = 1
    total_duration = 0
    hor,ver = direction is HOR, direction is VER
    
    if(hor):    xs = list()
    if(ver):    ys = list()
    #For starters, only lengths TOTAL or 1 are accepted
    for filename in filenames:
        im = Image.open(filename)
        images.append(im)
        if(hor):
            xs.append(width)
            width+=im.width
            height=max(height,im.height)
        if(ver):
            ys.append(height)
            height+=im.height
            width=max(width,im.width)
        try:
            lengths.append(im.n_frames)
            total_length=max(total_length,im.n_frames)
            total_duration = max(im.n_frames*im.info['duration'],total_duration)
        except:
            lengths.append(1)
    
    print("Image",width,"x",height)
    results = list()
    print(lengths)
    
    for t in range(total_length):
        target =  Image.new('RGBA', (width, height), BGCOLOR)
        results.append(target)
        
    for i,img in enumerate(images):
        length = lengths[i]
        if(hor):
            x=xs[i]
            if(centering=="top"):       y=0
            elif(centering=="bottom"):  y=height-img.height
            else:                       y=int((height-img.height)/2)
        if(ver):
            y=ys[i]
            if(centering=="top"):       x=0
            elif(centering=="bottom"):  x=width-img.width
            else:                       x=int((width-img.width)/2)
        
        if(length==1):
            for target in results:
                target.paste(img,(x,y))
        else:
            ratio = int(total_length/length)
            print("Anim of length",length,"of ratio",ratio)
            for j in range(length):
                for k in range(ratio):
                    print("Image",i,"frame",j,"ratio",k)
                    results[j*ratio+k].paste(img,(x,y))
                try:
                    img.seek(img.tell()+1)
                except:
                    pass
    
    for t in range(len(results)):
        results[t]=index_rgb_alpha(results[t],transparency=255)

        
    #results[0].convert("P").show()
    folder = os.path.dirname(filenames[0]).strip()
    names = "".join([os.path.splitext(os.path.basename(f))[0] for f in filenames])
    if(folder):
        outputname = os.sep.join((folder,names+".gif"))
    else:
        outputname = names+".gif"
    print("Exporting",outputname)
    index = 0
    for result in results:
        result.save(names+str(index)+".png", transparency=255)
        index+=1
        
    results[0].save(outputname, "GIF", save_all=True,append_images=results[1:], optimize=False, disposal=2, duration=total_duration/total_length, loop=0, transparency=255)
    input("Done! Press enter...")
try:
    if __name__ == "__main__":
        import sys
        
        direction = DEFAULT
        centering = "center"
        
        if(len(sys.argv)>1):
            if("-h" in sys.argv):
                direction = HOR
                sys.argv.remove("-h")
            if("-v" in sys.argv):
                direction = VER
                sys.argv.remove("-v")
            if("--center" in sys.argv):
                centering = "center"
                sys.argv.remove("--center")
            if("--bottom" in sys.argv):
                centering = "bottom"
                sys.argv.remove("--bottom")
            if("--top" in sys.argv):
                centering = "top"
                sys.argv.remove("--top")
            
            
            file_list = list()
            for arg in sys.argv[1:]:
                file_list.append(arg)
            
            
            stack_gifs_vh(file_list,direction,centering)
except Exception as E:
    print(E)
    import traceback
    traceback.print_exc()
    input("Failure")

