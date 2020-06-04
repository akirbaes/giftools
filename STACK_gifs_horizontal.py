from PIL import Image
import os.path
import os
import traceback
from gif_manips import index_rgb_and_alpha as index_rgb_alpha
BGCOLOR = (128,128,128,255)
HOR = 0
VER = 1
DEFAULT=HOR

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
   
def read_timings(filename):
    times=[0]
    try:
        im = Image.open(filename)
        # durations=[]
        print(im.n_frames)
        for i in range(im.n_frames):
            d=im.info['duration']
            # durations.append(d)
            times.append(times[-1]+d)
            if(i<im.n_frames-1):
                im.seek(im.tell()+1)
    except:
        traceback.print_exc()
    return times
def get_frame_number(time,times):
    for i in range(len(times)):
        if(times[i]>=time):
            return i-1
    return len(times)-2



def stack_gifs_vh(filenames,direction=HOR,centering="center"):
    print(filenames)
    images = list()
    width = 0
    height = 0
    hor,ver = direction is HOR, direction is VER
    
    if(hor):    xs = list()
    if(ver):    ys = list()
    #For starters, only lengths TOTAL or 1 are accepted
    all_timings = []
    for filename in filenames:
        timings = read_timings(filename)
        all_timings.append(timings)
    
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
    
    print("Image",width,"x",height)
    results = list()
    
    print(all_timings)
    compound_timings = set()
    for timings in all_timings:
        compound_timings.update(timings)
    compound_timings=sorted(compound_timings)
    
    durations = []
    for i in range(len(compound_timings)-1):
        durations.append(compound_timings[i+1]-compound_timings[i])
    compound_timings=compound_timings[1:] #remove timing zero
    print(durations)
    print(compound_timings)
    
    for t in compound_timings:
        target =  Image.new('RGBA', (width, height), BGCOLOR)
        results.append(target)
        
    for i,img in enumerate(images):
        image_index = 0
        timings = all_timings[i]
        
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
        
        for frame_index,time in enumerate(compound_timings):
            print(image_index,"<?",get_frame_number(time,timings))
            if(image_index<get_frame_number(time,timings)):
                img.seek(img.tell()+1)
                image_index+=1
            results[frame_index].paste(img,(x,y))
        
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
    # for result in results:
        # result.save(names+str(index)+".png", transparency=255)
        # index+=1
        
    results[0].save(outputname, "GIF", save_all=True,append_images=results[1:], duration=durations, loop=0)
    #input("Done! Press enter...")
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
    traceback.print_exc()
    input("Failure")

