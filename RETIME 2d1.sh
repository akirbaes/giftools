THISFILE=`basename "$0"`
TIMING="${THISFILE//[!0-9d]/}" #based on script file name
PYSCRIPTPATH="${0%\\*}\\retime_gif.py" #if the .sh script is somewhere else, put the absolute path instead
PARAM_FOLDER=$(dirname -- "$1")
#PARAM_FOLDER="${1%\\*}" #The python script will be local to the image (for creating new ones)
cd "$PARAM_FOLDER"
(
echo python "$PYSCRIPTPATH" "$TIMING" "$@"
python "$PYSCRIPTPATH" "$TIMING" "$@"
) || exec $SHELL