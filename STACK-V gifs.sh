THISFILE=`basename "$0"`
PYSCRIPTPATH="${0%\\*}\\STACK_gifs.py" #if the .sh script is somewhere else, put the absolute path instead
PARAM_FOLDER="${1%\\*}" #The python script will be local to the image (for creating new ones)
cd "$PARAM_FOLDER"
(
echo python "$PYSCRIPTPATH" -v "$@"
python "$PYSCRIPTPATH" -v "$@"
) || exec $SHELL