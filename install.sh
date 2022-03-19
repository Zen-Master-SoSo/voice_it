#!/bin/bash
set -e
if [ ! dpkg -l python3-pyqt5 &> /dev/null ]
then
	sudo apt install -y python3-pyqt5
fi
if [ ! -d /usr/lib/python3.8/site-packages/voice-it/ ]
then
	sudo mkdir -p /usr/lib/python3.8/site-packages/voice-it/
fi
sudo cp voice-it.py voice-it.png voice-it.svg interface.py interface.html favicon.ico /usr/lib/python3.8/site-packages/voice-it/
sudo chmod 0755 /usr/lib/python3.8/site-packages/voice-it/voice-it.py
sudo chmod 0644 /usr/lib/python3.8/site-packages/voice-it/voice-it.png
sudo chmod 0644 /usr/lib/python3.8/site-packages/voice-it/voice-it.svg
sudo chmod 0644 /usr/lib/python3.8/site-packages/voice-it/interface.py
sudo chmod 0644 /usr/lib/python3.8/site-packages/voice-it/interface.html
sudo chmod 0644 /usr/lib/python3.8/site-packages/voice-it/favicon.ico
sudo cp voice-it.desktop /usr/share/applications/voice-it.desktop
sudo chmod 0644 /usr/share/applications/voice-it.desktop
sudo /usr/sbin/ufw delete allow in to any port 8585
sudo /usr/sbin/ufw allow in to any port 8585 comment 'Voice-it' &> /dev/null
echo "Complete!"
