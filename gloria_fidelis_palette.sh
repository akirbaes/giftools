cd "${0%\\*}"
(
python "C:\Users\Akira Baes\Desktop\Old Anims\ImageTools\giftools\transfer_palette.py" "C:\Users\Akira Baes\Desktop\Old Anims\ImageTools\giftools\gloria_fidelis.gif" "$1" ;
) || read  -n 1 -p "Failed. Press enter." mainmenuinput ;