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
if [ -s /usr/bin/gbirthday ]
    then
        rm /usr/local/bin/gbirthday
    fi
if [ -s /usr/local/gbirthday ]
    then
        rm -rf /usr/local/gbirthday
    fi
if [ -s /usr/share/gbirthday ]
    then
        rm -rf /usr/share/gbirthday
    fi

# Install new version
mkdir /usr/share/gbirthday
chmod 775 /usr/share/gbirthday
cp *.png /usr/share/gbirthday/
chmod 664 /usr/share/gbirthday/*.png
cp gbirthday.py /usr/share/gbirthday/
chmod 775 /usr/share/gbirthday/gbirthday.py
ln -s /usr/share/gbirthday/gbirthday.py /usr/bin/gbirthday
chmod 775 /usr/bin/gbirthday
