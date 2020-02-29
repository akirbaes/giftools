THISFILE=`basename "$0"`
COLORS="${THISFILE//[!0-9 ]/}" #based on script file name
PYSCRIPTPATH="${0%\\*}\\change_background.py" #if the .sh script is somewhere else, put the absolute path instead #${0%\\*}\\change_background.py"
#cd "${0%\\*}"
echo COl : $COLORS
echo ALL : $@
PARAM_FOLDER="${1%\\*}" #The python script will be local to the image (for creating new ones)
cd "$PARAM_FOLDER"
(
bash "${0%\\*}\\_unoptimize_gif.sh" "$@"
echo python "$PYSCRIPTPATH" --color $COLORS "$@"
python "$PYSCRIPTPATH" --color $COLORS "$@"
)
|| exec $SHELL