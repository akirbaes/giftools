import os.path
import os
try:
    if __name__ == "__main__":
        import sys
        if(len(sys.argv)>1):
            for arg in sys.argv[1:]:
                name,extension = os.path.splitext(arg)
                file = open(name+"_palette.sh","w")
                file.write('cd "${0%\\\\*}"' +"""
(
python \""""+os.getcwd()+os.sep+"""transfer_palette.py" "%s" "$1" ;
) || read  -n 1 -p "Failed. Press enter." mainmenuinput ;"""%arg)
        file.close()
except Exception as e:
    input("Failure\n"+str(e))
    raise(e)