((
for FILE in "$@"
do 
gifsicle --colors=255 "${FILE}" -o "${FILE}" 
gifsicle -U "${FILE}" -o "${FILE}"
done
) && echo Done.
) || echo Failed! ;
#exec $SHELL