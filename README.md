# pydPiper3
pydPiper adapted for use with Python3

Improving the version of dhrone/pydPiper for Raspberry Zero webradioproject with DAC, Volumio and 16x2LCD

# NL
Een verbeterde versie van dhrone/pydPiper en synoniem/pydPiper met de verbeteringen zoals ik die gebruik bij mijn webradioproject (https://synoniem.tweakblogs.net/blog/18684/pi-zero-radio). Zoals een nieuwe pydpiper.service bestand en een nieuw pydPiper.cfg bestand. Ondersteuning voor 24 uurs versie klok op het 16x2LCD display (pages_lcd_16x2.py). Toegevoegd ondersteuning van de weersverwachting van het KNMI in plaats van  Wunderground of Accuweather.

Deze versie maakt gebruik van Python3 docker container synoniem/pydpiper3:latest die ik op hub.docker.com heb gezet. Omdat de Pi Zero geen snelheidsmonster is kun je beter eerst een pull doen van synoniem/pydpiper3:latest voordat je de pydpiper.service start.
<pre>
sudo docker pull synoniem/pydpiper3:latest
</pre>

Je kan daarna volstaan met het clonen van deze repo in de map /home/volumio, aanpassen van pydPiper.cfg en het kopieeren van het pydpiper.service bestand:

<pre> 
sudo cp pydpiper.service /etc/systemd/system/pydpiper.service
sudo systemctl daemon-reload
sudo service pydpiper start
</pre>
Het opstarten van pydpiper op een Pi Zero duurt ongeveer een minuut.


