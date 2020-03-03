THISFILE=`basename "$0"`
PYSCRIPTPATH="${0%\\*}\\" #If the .sh script is somewhere else, put the absolute path instead
PARAM_FOLDER="${1%\\*}" #Local to the image (for creating new ones)
cd "$PARAM_FOLDER"
python -V
(
for FILE in "$@"
do
    FULLNAME=$(basename -- "$FILE")
    NAME="${FULLNAME%.*}"
    EXTENSION="${FULLNAME##*.}"
    PARENTFOLDER=$(dirname -- "$FILE")
    echo python "$PYSCRIPTPATH"transfer_palette.py "$FILE" "$PARENTFOLDER""/""$NAME""/interpolated_frames"
    python "$PYSCRIPTPATH"transfer_palette.py "$FILE" "$PARENTFOLDER""/""$NAME""/interpolated_frames"
    mv "$NAME"_EXT_interpolated_frames.gif    "$NAME"_interp.gif
    bash "$PYSCRIPTPATH"_unoptimize_gif.sh    "$NAME"_interp.gif
    bash "$PYSCRIPTPATH""redux nearest 4.sh"  "$NAME"_interp.gif
    bash "$PYSCRIPTPATH""resample X4.sh"      "$NAME"_interp_N4.gif
    bash "$PYSCRIPTPATH"_unoptimize_gif.sh    "$NAME"_interp_N4.gif
    
    mv                                        "$NAME"_interp.gif        "$NAME""(interp).gif"
    mv                                        "$NAME"_interp_N4.gif     "$NAME""_interp(small).gif"
    mv                                        "$NAME"_interp_N4_X4.gif  "$NAME""_interp(big).gif"
    
done
)
exec $SHELL