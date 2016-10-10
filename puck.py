from bluepy import btle
import time
import socket
import sys
import os
import logging
import logging.handlers

# Settings
puck_mac = "C3:25:1D:C7:EF:BD" # mac address of BLE device
puck_char = 11 # characteristic of the BLE device to read
min_volume = 0
max_volume = 22
step=360//(max_volume-min_volume) # min degrees per volume change step, i.e.
max_volume_change = 5 # ignore changes above this amount per interval
interval = 0 # in seconds

# Logging
LOG_FILE = os.path.join(sys.path[0], "upload.log")
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
fh = logging.handlers.RotatingFileHandler(
              LOG_FILE, maxBytes=5000000, backupCount=5)
fh.setLevel(logging.DEBUG)
fh.setFormatter(formatter)
logger.addHandler(fh)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(formatter)
logger.addHandler(ch)

def read_datapoint():
    """
    Read the data from the characteristic in Puck.js we need.
    Found out the correct handle for this characteristic through bluepy with:
    # p = btle.Peripheral(puck_mac, btle.ADDR_TYPE_RANDOM)
    # chars = p.getCharacteristics()
    # for c in chars:
    # print c.uuid, c.getHandle(), c.propertiesToString(), c.read()
    """
    # TODO: Debug reading this datapoint without setup of notifications!
    # Need to use UA bla app now?
    datapoint = p.readCharacteristic(puck_char)
    print "Read: %s" % (datapoint)
    try:
        # Read datapoint and cast to int
        datapoint_int = int(datapoint)
        return datapoint_int
    except:
        # Sometimes no integer, but '<- Serial1\r\n>' is read from Puck.js.
        # nRF UART does not display any data at those times.
        # Not great, but removing battery from Puck.js resolves this.
        logger.debug("No valid datapoint value read ('%s'). Try it with nRF UART? Reset battery?" % (datapoint))
        return False

def reset_datapoint(datapoint):
    """
    Use the value of the first datapoint or the value of degrees_zero as absolute 0 point.
    So if no static value is set, make sure to close the lid on startup when calibrating.
    """
    # TODO: het verschil tussen de nieuwe angle en oude omzetten naar een teller die iets van 500 graden is (iets minder dan twee keer de dop draaien zeg maar)
    # TODO: afvangen wanneer hij van 0 naar 359 rolt zodat je geen rare effecten krijgt :]

    if datapoint_of_last_volume_change > 359-step:
        if datapoint < 0+step:
            # Count 360 and up if a roll from 360 to 0 occurred
            datapoint_original = datapoint
            datapoint = datapoint+359
            logger.debug("Going over 360. Last: %s, Current: %s, Reset: %s" % (datapoint_of_last_volume_change, datapoint_original, datapoint))
    if datapoint_of_last_volume_change < 0+step:
        if datapoint > 359-step:
            # Count -1 and down if a roll from 360 to 0 occurred
            datapoint_original = datapoint
            datapoint = -1*(359-datapoint)
            logger.debug("Going under 0. Last: %s, Current: %s, Reset: %s" % (datapoint_of_last_volume_change, datapoint_original, datapoint))

    return datapoint

def send_volume(volume):
    """
    Send volume via UDP.

    #Examples of ASCII Messages to Weigl
    #volume van channel 1 op 0
    #echo '!cmv0:1#' > /dev/udp/169.254.3.101/5555
    #volume van channel 1 op 31
    echo '!cmv31:1#' > /dev/udp/169.254.3.101/5555
    #fade volume naar 31 in 2 seconde
    #echo '!cfm31<2#' > /dev/udp/169.254.3.101/5555
    """
    # TODO: Check if value is valid?
    message = "!cmv%s:1#" % str(volume)
    sock.sendto(message, (UDP_IP, UDP_PORT))
    logger.debug("Sent: %s to %s:%s" % (message, UDP_IP, str(UDP_PORT)))

def transform_data_to_volume(datapoint):
    """
    """
    # Set globals in order to make it possible to globally change them
    global last_datapoint
    global last_volume

    if not datapoint:
        # Set volume to minimum when no datapoint was received.
        volume = min_volume
    elif datapoint == -1:
        # Set volume to maximum when magnet is too far away.
        # Somehow, this never seems to happen :/
        volume = max_volume
    else:
        difference = abs(reset_datapoint(datapoint) - reset_datapoint(datapoint_of_last_volume_change))
        if difference >= step and difference <= step*max_volume_change:
            # As soon as the minimum change is reached, change volume
            # If change is too big, consider it an error and do nothing
            logger.debug("Check if %s-%s=%s is bigger than %s" % (reset_datapoint(datapoint), reset_datapoint(datapoint_of_last_volume_change), difference, step))

            # Calculate volume with floor division and last known value for volume
            volume = last_volume + difference//step
        else:
            volume = last_volume


    if volume != last_volume:
        datapoint_of_last_volume_change = reset_datapoint(new_datapoint)

    last_datapoint = reset_datapoint(new_datapoint)

    logger.debug("Volume: %s" % (volume))
    return volume





# Connect to Puck.js
logger.debug("Connecting...")
p = btle.Peripheral("C3:25:1D:C7:EF:BD", btle.ADDR_TYPE_RANDOM)

# Enable notifications
p.writeCharacteristic(12, "\x01\x00", False)
logger.debug("Connected to: %s" % (p))

# Keep on reading data from Puck.js and send it through UDP
try:
    # Read first data from Puck.js and set some initial values
    first_datapoint = read_datapoint()
    last_datapoint = first_datapoint
    datapoint_of_last_volume_change = first_datapoint
    last_volume = min_volume
    logger.debug("First datapoint: %s" % (first_datapoint))

    # Setup UDP connection
    # As per https://wiki.python.org/moin/UdpCommunication
    UDP_IP = "169.254.3.101"
    UDP_PORT = 5555
    sock = socket.socket(socket.AF_INET, # Internet
                        socket.SOCK_DGRAM) # UDP

    # Check puck.js, transform data to volume, send, repeat
    while True:
        new_datapoint = read_datapoint()

        # Bit ugly with all these nested if's but it works
        if new_datapoint:
            # If new_datapoint was found, calc volume
            # if not, keep on trying
            volume = transform_data_to_volume(new_datapoint)
            if volume != last_volume:
                send_volume(volume)
        time.sleep(interval)

except KeyboardInterrupt:
    logger.debug("Bye")
except Exception:
    raise
finally:
    if p: p.disconnect()
    logger.debug("Disconnected")
