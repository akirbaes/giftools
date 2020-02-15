import os.path

try:
    if __name__ == "__main__":
        import sys
        if(len(sys.argv)==2):
            name,extension = os.path.splitext(sys.argv[1])
        file = open(name+"_palette.sh","w")
        file.write('cd "${0%\\\\*}"' +"""
(
python transfer_palette.py "%s" "$1" ;
) || read  -n 1 -p "Failed. Press enter." mainmenuinput ;"""%sys.argv[1])
        file.close()
except Exception as e:
    input("Failure\n"+str(e))
    raise(e)