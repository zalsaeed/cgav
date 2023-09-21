FROM python:3.9

RUN apt-get update -y
RUN apt-get install -y vim curl nodejs npm ripgrep

# a beautiful bash!
COPY resources/.bash_profile /root/.bash_profile
COPY resources/.bashrc /root/.bashrc

# vim configs
COPY resources/.vimrc /root/.vimrc

# plugin manager for vim
RUN curl -fLo ~/.vim/autoload/plug.vim --create-dirs \
    https://raw.githubusercontent.com/junegunn/vim-plug/master/plug.vim

# list of hot key mappings for vim
COPY resources/hotkeys /root/.vim/hotkeys
# RUN chomd 444 ~/.vim/hotkeys  # do we really neeed to?

# install yarn, as needed for some vim plugins
RUN npm install --global yarn

# Install all listed plugins:
# RUN vim -c 'PlugInstall' -c 'qa!' ~/.vimrc
# OR you could use 
RUN vim +PlugInstall +qall

RUN vim +'CocInstall coc-pyright' +qall

COPY requirements.txt requirements.txt

RUN pip3 install --upgrade setuptools
RUN pip3 install -r requirements.txt

COPY src/ /root/src/
WORKDIR /root/src/

