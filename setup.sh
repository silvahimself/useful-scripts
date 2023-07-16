echo "running setup script..." > setup.log

export install_list='git virtualbox virtualbox-guest-additions-iso virtualbox-guest-utils flatpak nodejs neofetch npm nodejs python3 python3-dev python3-pip python3-setuptools p7zip-full p7zip-rar dislocker'

sudo apt update && sudo apt upgrade -y
echo "Update done." >> setup.log

# apt
sudo apt install $install_list -y

# pip
pip3 install thefuck --user

echo 'Done with apt installations.\nInstalled: $install_list' >> setup.log

# Snaps
sudo snap install rider --classic
sudo snap install code --classic
sudo snap install htop
sudo snap install brave
echo "Done with snap installations." >> setup.log

echo "Done." >> setup.log

