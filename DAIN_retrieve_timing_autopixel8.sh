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
    #EXTENSION="${FULLNAME##*.}"
    PARENTFOLDER=$(dirname -- "$FILE")
    echo Transferring pallet and duration approximations
    python "$PYSCRIPTPATH"transfer_palette_and_time.py "$FILE" "$PARENTFOLDER""/""$NAME""/interpolated_frames"
    mv "$NAME"_EXT_interpolated_frames.gif    "$NAME"_interp.gif
    echo Pixelating result...
    bash "$PYSCRIPTPATH""redux nearest 8.sh"  "$NAME"_interp.gif
    bash "$PYSCRIPTPATH""resample X4.sh"      "$NAME"_interp_N8.gif
    (
    mkdir output_N8
    )
    mv                                        "$NAME"_interp.gif        output_N8/"$NAME""(interp).gif"
    mv                                        "$NAME"_interp_N8.gif     output_N8/"$NAME""_interp(small).gif"
    mv                                        "$NAME"_interp_N8_X4.gif  output_N8/"$NAME""_interp(x4).gif"
    
done
)
exec $SHELL