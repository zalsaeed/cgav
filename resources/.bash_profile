
# add color to the listed folders 
export CLICOLOR=1
export LSCOLORS=GxFxCxDxBxegedabagaced

# add colors to the current working directory
export TERM="xterm-color" 
export PS1='\[\e[0;33m\]\u\[\e[0m\]@\[\e[0;32m\]\h\[\e[0m\]:\[\e[0;34m\]\w\[\e[0m\]\$ '

eval `ssh-agent -s`