# Puck.js Lid Volume button

* install bluez?
* git clone git://github.com/erwinelling/puckjs.git
* pip install bluepy (https://github.com/IanHarvey/bluepy)



## Remarks

* Some BLE devices allow for subscribing to notifications, could not get that to work, so just reading the right characteristic often.
* Sometimes the Puck.js seems unreadable (also on nRF UART app), removing battery and reinstalling it, fixes this. Annoying :/
* Also tried Adafruit_BluefruitLE library, but it seems impossible to connect with a random address (instead of public), which does seem necessary on Puck.js


## Notitions
Follow these steps. Maybe not everything necessary for RPI3?
https://learn.adafruit.com/bluefruit-le-python-library/installation#library-installation
https://learn.adafruit.com/install-bluez-on-the-raspberry-pi/installation

http://www.elinux.org/RPi_Bluetooth_LE

hciconfig and gatttool to test

https://stackoverflow.com/questions/22062037/hcitool-lescan-shows-i-o-error

sudo nano /lib/systemd/system/bluetooth.service
added --experimental

systemctl status bluetooth

https://www.raspberrypi.org/forums/viewtopic.php?t=133246&p=890410

https://urbanjack.wordpress.com/2014/06/05/how-to-set-bluez-into-ble-or-le-only-mode-ibeacon/

sudo /etc/init.d/dbus restart
pi@raspberrypi:~ $ sudo systemctl restart bluetooth
pi@raspberrypi:~ $ systemctl status bluetooth

gatttool -t random -b C3:25:1D:C7:EF:BD -I
-t random is heel bealngrijk

sudo blescan
Device (new): c3:25:1d:c7:ef:bd (random), -69 dBm
Flags: <05>
Complete 128b Services: <9ecadc240ee5a9e093f3a3b50100406e>
Complete Local Name: 'Puck.js efbd'

val = binascii.b2a_hex(ch.read())
val = binascii.unhexlify(val)
val = struct.unpack('f', val)[0]
print str(val)

gatttool -b C3:25:1D:C7:EF:BD -t random --char-write-req -a 0x000b -n 0100 --listen
sudo gatttool -b C3:25:1D:C7:EF:BD -t random --char-write-req --handle=0x000e --value=0300 --listen


Didn't get it to read notifications :/
https://github.com/IanHarvey/bluepy/issues/124
