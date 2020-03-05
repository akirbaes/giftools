THISFILE=`basename "$0"`
OUTLINE="${THISFILE//[!0-9]/}" #based on script file name
PYSCRIPTPATH="${0%\\*}\\" #if the .sh script is somewhere else, put the absolute path instead
PARAM_FOLDER=$(dirname -- "$1")
#PARAM_FOLDER="${1%\\*}" #The python script will be local to the image (for creating new ones)
cd "$PARAM_FOLDER"
(
echo python "$PYSCRIPTPATH"crop_image.py "$OUTLINE" "$@"
python "$PYSCRIPTPATH"crop_image.py "$OUTLINE" "$@"
) || exec $SHELL