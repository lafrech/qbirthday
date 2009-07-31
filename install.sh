#! /bin/bash

# Check if root
if [ "$(id -u)" != "0" ]; then
   echo "You will need root privileges to install gbirthday"
   echo "Try again with sudo: \"sudo ./install.sh\""
   exit 1
fi

# Delete previus version
if [ -s /usr/local/bin/gbirthday ]
    then
        rm /usr/local/bin/gbirthday
    fi
if [ -s /usr/local/gbirthday ]
    then
        rm -rf /usr/local/gbirthday
    fi

# Install new version
mkdir /usr/local/gbirthday
chmod 775 /usr/local/gbirthday
cp *.png /usr/local/gbirthday/
chmod 664 /usr/local/gbirthday/*.png
cp gbirthday.py /usr/local/gbirthday/
chmod 775 /usr/local/gbirthday/gbirthday.py
ln -s /usr/local/gbirthday/gbirthday.py /usr/local/bin/gbirthday
chmod 775 /usr/local/bin/gbirthday
