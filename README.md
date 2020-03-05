# GraplerGuide_kodi_addon

Kodi Addon for Grapplers Guide Website by Jason Scully.

Add your username and password in the setting section for the addon.

Basically it mimics the website section menu, and you can drill down from there on what you want to see.
Usefull if you want to practice in front of the TV and you have kodi home theatre installed.

...Still a bit buggy (I have a few errors which don't seem to impact the overall functionality)

Installation (linux style boxes):

-Start terminal program in kodi (can ssh to kodi also)

-Locate addon dir in Kodi, (for ubuntu it's /home/kodi/.kodi/addon/)

-cd to the directory:
    >cd /home/kodi/.kodi/addon

-Create dir named plugin.video.gg
    >mkdir plugin.video.gg

-go into the directory you just made:
    >cd plugin.video.gg

-Download the zip file to the dir:
    >wget https://github.com/anthonyp1234/GraplerGuide_kodi_addon/archive/master.zip

-Unzip the file:
    >unzip GraplerGuide_kodi_addon-master.zip

-Get out of the terminal, and go to the settings-->addon section for kodi. Search for each of the addons and install them:
    -requests
    -beautifulsoup
    -beautifulsoup4

-Go to each addon and configure and make sure they are enabled.

-Restart kodi
-Go to the setting-->addons section look for kodi and enable it.
-Configure the addon to add your username and password. Make sure this is typed in correctly, my code isn't at a stage where it handles all exceptions.

-The addon should now appear and you should be able to run it. If you add it to your favourites, some skins allow you to put favourites to the menu section of kodi, so you can have it on your homescreen when you start up.

....Also if you like fighting, I've done one of these for UFC fight pass as well.



