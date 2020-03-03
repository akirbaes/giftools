THISFILE=`basename "$0"`
PYSCRIPTPATH="${0%\\*}\\transfer_palette.py" #if the .sh script is somewhere else, put the absolute path instead
#cd "${0%\\*}"
PARAM_FOLDER="${1%\\*}" #The python script will be local to the image (for creating new ones)
cd "$PARAM_FOLDER"
python -V
(
for FILE in "$@"
do
    FULLNAME=$(basename -- "$FILE")
    NAME="${FULLNAME%.*}"
    EXTENSION="${FULLNAME##*.}"
    PARENTFOLDER=$(dirname -- "$FILE")
    echo python "$PYSCRIPTPATH" "$FILE" "$PARENTFOLDER""/""$NAME""/interpolated_frames"
    python "$PYSCRIPTPATH" "$FILE" "$PARENTFOLDER""/""$NAME""/interpolated_frames"
done
)
exec $SHELL