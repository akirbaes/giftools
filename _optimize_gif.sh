((
for FILE in "$@"
do 
gifsicle -O3 "${FILE}" -o "${FILE}"
done
) && echo Done.
) || echo Failed! ;
#exec $SHELL