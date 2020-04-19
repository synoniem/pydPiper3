# pydPiper
Improving the version of dhrone/pydPiper for Raspberry Zero webradioproject with DAC, Volumio and 16x2LCD

# NL
Een versie van dhrone/pydPiper met wat kleine verbeteringen zoals ik die gebruik bij mijn webradioproject (https://synoniem.tweakblogs.net/blog/18684/pi-zero-radio). Zoals een nieuwe pydpiper.service bestand en een nieuwe pydPiper.cfg bestand. Ondersteuning voor 24 uurs versie klok op het 16x2LCD display (pages_lcd_16x2.py). Nog in de pijplijn zit ondersteuning van de weersverwachting van het KNMI in plaats van de Wunderground of Accuweather.

Deze versie maakt gebruik van de docker container dhrone/pydPiper:latest die dhrone op hub.docker.com heeft staan. In de nabije toekomst hoop ik een eigen container gebaseerd op python3 op de dockerhub te plaatsen. 

Voor nu kun je volstaan met het clonen van deze repo in de map /home/volumio, aanpassen van pydPiper.cfg en het kopieeren van het pydpiper.service bestand: 

sudo cp pydpiper.service /etc/systemd/system/pydpiper.service
sudo systemctl daemon-reload
sudo service pydpiper start

Het opstarten op een Pi Zero duurt ongeveer een minuut.
