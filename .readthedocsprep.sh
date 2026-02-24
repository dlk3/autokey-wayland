#  ReadTheDocs pre-build steps to load project source
git clone https://github.com/dlk3/autokey-wayland
cd autokey-wayland/autokey-gnome-extension
make
cd ..
pip install .
