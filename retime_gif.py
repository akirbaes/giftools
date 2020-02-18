from PIL import Image
import sys


def retime_gif(filename,timing):
    im = Image.open(filename)
    output = list()
    transparency=im.info.get("transparency",None)
    try:
        while 1:
            output.append(im.copy())
            
            im.seek(im.tell()+1)
            duration = im.info['duration']
    except EOFError:
        pass # end of sequence
        
    outname = filename
    if(len(output)>1):
        if(transparency!=None):
            output[0].save(outname, save_all=True,append_images=output[1:], optimize=False, disposal=2, duration=timing, loop=0, transparency=transparency)
        else:
            output[0].save(outname, save_all=True,append_images=output[1:], optimize=False, disposal=2, duration=timing, loop=0)
        

if __name__ == "__main__":
    timing=200
    for arg in sys.argv[1:]:
        if(arg.isnumeric()):
            timing = int(arg)
        
    if(len(sys.argv)>1):
        
        for arg in sys.argv[1:]:
            if(arg.isnumeric()):
                timing = int(arg)
            else:
                retime_gif(arg,timing)
    else:
        input("Error. Pass an image and a timing (default fast)")
    #input("Done")
