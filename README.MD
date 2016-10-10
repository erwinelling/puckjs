# Puck.js Lid Volume button

* install bluez?
* git clone git://github.com/erwinelling/puckjs.git
* pip install bluepy (https://github.com/IanHarvey/bluepy)



## Remarks

* Some BLE devices allow for subscribing to notifications, could not get that to work, so just reading the right characteristic often.
* Sometimes the Puck.js seems unreadable (also on nRF UART app), removing battery and reinstalling it, fixes this. Annoying :/
* Also tried Adafruit_BluefruitLE library, but it seems impossible to connect with a random address (instead of public), which does seem necessary on Puck.js
* Only one application can connect to Puck.js at a time.

## Notitions
Follow these steps. Maybe not everything necessary for RPI3?
https://learn.adafruit.com/bluefruit-le-python-library/installation#library-installation
https://learn.adafruit.com/install-bluez-on-the-raspberry-pi/installation

http://www.elinux.org/RPi_Bluetooth_LE

hciconfig and gatttool to test

https://stackoverflow.com/questions/22062037/hcitool-lescan-shows-i-o-error

https://eclipse.github.io/kura/doc/bluetooth-le-example.html

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

http://www.jaredwolff.com/blog/get-started-with-bluetooth-low-energy/

gatttool -b C3:25:1D:C7:EF:BD -t random --char-write-req -a "0x000e" -n 0100 --listen

sudo gatttool -b C3:25:1D:C7:EF:BD -t random -I
[C3:25:1D:C7:EF:BD][LE]> connect
Attempting to connect to C3:25:1D:C7:EF:BD
Connection successful
[C3:25:1D:C7:EF:BD][LE]> char-read-hnd 0x000b
Characteristic value/descriptor: 1a
[C3:25:1D:C7:EF:BD][LE]> char-read-hnd 0x000e
Characteristic value/descriptor: 58
[C3:25:1D:C7:EF:BD][LE]> char-read-hnd 0x000b
Characteristic value/descriptor: 1a
[C3:25:1D:C7:EF:BD][LE]> char-desc
handle: 0x0001, uuid: 00002800-0000-1000-8000-00805f9b34fb
handle: 0x0002, uuid: 00002803-0000-1000-8000-00805f9b34fb
handle: 0x0003, uuid: 00002a00-0000-1000-8000-00805f9b34fb
handle: 0x0004, uuid: 00002803-0000-1000-8000-00805f9b34fb
handle: 0x0005, uuid: 00002a01-0000-1000-8000-00805f9b34fb
handle: 0x0006, uuid: 00002803-0000-1000-8000-00805f9b34fb
handle: 0x0007, uuid: 00002a04-0000-1000-8000-00805f9b34fb
handle: 0x0008, uuid: 00002800-0000-1000-8000-00805f9b34fb
handle: 0x0009, uuid: 00002800-0000-1000-8000-00805f9b34fb
handle: 0x000a, uuid: 00002803-0000-1000-8000-00805f9b34fb
handle: 0x000b, uuid: 6e400003-b5a3-f393-e0a9-e50e24dcca9e
handle: 0x000c, uuid: 00002902-0000-1000-8000-00805f9b34fb
handle: 0x000d, uuid: 00002803-0000-1000-8000-00805f9b34fb
handle: 0x000e, uuid: 6e400002-b5a3-f393-e0a9-e50e24dcca9e
[C3:25:1D:C7:EF:BD][LE]> char-read-hnd 0x0001
Characteristic value/descriptor: 00 18
[C3:25:1D:C7:EF:BD][LE]> char-read-hnd 0x0002
Characteristic value/descriptor: 02 03 00 00 2a
[C3:25:1D:C7:EF:BD][LE]> char-read-hnd 0x0003
Characteristic value/descriptor: 50 75 63 6b 2e 6a 73 20 65 66 62 64
[C3:25:1D:C7:EF:BD][LE]> char-read-hnd 0x0004
Characteristic value/descriptor: 02 05 00 01 2a
[C3:25:1D:C7:EF:BD][LE]> char-read-hnd 0x0005
Characteristic value/descriptor: 00 00
[C3:25:1D:C7:EF:BD][LE]> char-read-hnd 0x0006
Characteristic value/descriptor: 02 07 00 04 2a
[C3:25:1D:C7:EF:BD][LE]> char-read-hnd 0x0007
Characteristic value/descriptor: 06 00 10 00 00 00 90 01
[C3:25:1D:C7:EF:BD][LE]> char-read-hnd 0x000
Error: Characteristic value/descriptor read failed: Invalid handle
[C3:25:1D:C7:EF:BD][LE]> char-read-hnd 0x0008
Characteristic value/descriptor: 01 18
[C3:25:1D:C7:EF:BD][LE]> char-read-hnd 0x0009
Characteristic value/descriptor: 9e ca dc 24 0e e5 a9 e0 93 f3 a3 b5 01 00 40 6e
[C3:25:1D:C7:EF:BD][LE]> char-read-hnd 0x000a
Characteristic value/descriptor: 10 0b 00 9e ca dc 24 0e e5 a9 e0 93 f3 a3 b5 03 00 40 6e
[C3:25:1D:C7:EF:BD][LE]> char-read-hnd 0x000b
Characteristic value/descriptor: 1a
[C3:25:1D:C7:EF:BD][LE]> char-read-hnd 0x000c
Characteristic value/descriptor: 00 00
[C3:25:1D:C7:EF:BD][LE]> char-read-hnd 0x000d
Characteristic value/descriptor: 0c 0e 00 9e ca dc 24 0e e5 a9 e0 93 f3 a3 b5 02 00 40 6e
[C3:25:1D:C7:EF:BD][LE]> char-read-hnd 0x000e
Characteristic value/descriptor: 58

THIS WORKS!
pi@raspberrypi:~ $ gatttool -b C3:25:1D:C7:EF:BD -t random --char-write-req -a "0x000c" -n 0100
Characteristic value was written successfully
pi@raspberrypi:~ $ gatttool -b C3:25:1D:C7:EF:BD -t random --char-read -a "0x000b"
Characteristic value/descriptor: 33 33 39 0d 0a


from bluepy import btle
p = btle.Peripheral("C3:25:1D:C7:EF:BD", btle.ADDR_TYPE_RANDOM)
for c in p.getCharacteristics(): print c.uuid, c.getHandle(), c.propertiesToString(), c.read()
p.writeCharacteristic(12, "\x01\x00", False)
p.readCharacteristic(11)
p.readCharacteristic(12)
