if grep --exclude=to-do_check.sh --exclude-dir=.git -rnw ${GITHUB_WORKSPACE} -i -e "TODO"; then
    printf "\nPlease clean up unfinished \"TODO\" tasks before merging to main.\n"
    exit 1
fi