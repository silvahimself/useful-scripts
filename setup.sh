echo "running setup script..." > setup.log

sudo apt update && sudo apt upgrade -y
echo "Update done." >> setup.log

# apt
sudo apt install git virtualbox virtualbox-guest-additions-iso virtualbox-guest-utils flatpak nodejs neofetch npm nodejs python3 p7zip-full p7zip-rar -y

echo "Done with apt installations." >> setup.log

# Snaps
sudo snap install rider --classic
sudo snap install code --classic
sudo snap install htop
sudo snap install brave
echo "Done with snap installations." >> setup.log

echo "Done." >> setup.log

