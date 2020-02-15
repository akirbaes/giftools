cd "${0%\\*}"
(
python transfer_palette.py "C:\Users\Akira Baes\Desktop\Old Anims\gloria_fidelis.gif" "$1" ;
) || read  -n 1 -p "Failed. Press enter." mainmenuinput ;