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
        rm /usr/bin/gbirthday
    fi
if [ -s /usr/local/gbirthday ]
    then
        rm -rf /usr/local/gbirthday
    fi
if [ -s /usr/share/gbirthday ]
    then
        rm -rf /usr/share/gbirthday
    fi
if [ -s /usr/share/applications/gbirthday.desktop ]
    then
        rm -rf /usr/share/applications/gbirthday.desktop
    fi

# Install new version
echo Creating gbirthday folder
mkdir /usr/share/gbirthday
chmod 775 /usr/share/gbirthday
echo Creting pics folder
mkdir /usr/share/gbirthday/pics
chmod 775 /usr/share/gbirthday/pics
echo Moving pics to pics folder
cp -v pics/*.png /usr/share/gbirthday/pics
chmod 664 /usr/share/gbirthday/*.png
echo moving python file to gbirthday folder
cp -v gbirthday.py /usr/share/gbirthday/
chmod 775 /usr/share/gbirthday/gbirthday.py
echo Creating languages folder
mkdir /usr/share/gbirthday/languages
chmod 775 /usr/share/gbirthday/languages/
echo Moving languages to languages floder
cp -v languages/*.lang /usr/share/gbirthday/languages/
echo Creating menu item
cp -v gbirthday.desktop /usr/share/applications/ 
echo Linking python file in bin folder
ln -s /usr/share/gbirthday/gbirthday.py /usr/bin/gbirthday
chmod 775 /usr/bin/gbirthday
