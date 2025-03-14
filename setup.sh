echo "running setup script..." > setup.log

export install_list='git flatpak nodejs neofetch npm nodejs python3 python3-dev python3-pip python3-setuptools p7zip-full p7zip-rar dislocker'

sudo apt update && sudo apt upgrade -y
echo "Update done." >> setup.log

# apt
sudo apt install $install_list -y

# pip
pip3 install thefuck --user

echo 'Done with apt installations.\nInstalled: $install_list' >> setup.log

# Snaps
sudo snap install code --classic
sudo snap install htop
sudo snap install brave

echo "Done with snap installations." >> setup.log

# Install cursor
echo "Installing cursor..." >> setup.log
mkdir /home/david/software/
curl --output /home/david/software/cursor.AppImage "https://downloader.cursor.sh/linux/appImage/x64"
chmod a+x /home/david/software/cursor.AppImage
# register cursor command
sudo ln -s /home/david/software/cursor.AppImage /usr/local/bin/
echo "Done installing cursor." >> setup.log

echo "Setting up aliases..." >> setup.log
echo "\nls=\"ls -haltr\"" >> /home/david/.bashrc
echo "Done setting up aliases." >> setup.log

echo "Done." >> setup.log

