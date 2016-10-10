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
step=500//(max_volume-min_volume) # min degrees per volume change step, i.e.
max_volume_change = 5 # ignore changes above this amount per interval
interval = 0.5 # in seconds

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

    Returns integer or False
    """
    # TODO: Debug reading this datapoint without setup of notifications!
    # Need to use UA bla app now?
    datapoint = p.readCharacteristic(puck_char)
    logger.debug("Read datapoint: %s" % (datapoint))
    try:
        # TODO: According to specs, "-1" should be read, when magnet is too far away. This never happend, so not implementd.

        # Read datapoint and cast to int
        datapoint_int = int(datapoint)
        reset_datapoint_int = reset_datapoint(datapoint_int)
        logger.debug("Reset datapoint: %s" % (datapoint))
        return reset_datapoint_int
    except:
        # Sometimes no integer, but '<- Serial1\r\n>' is read from Puck.js.
        # nRF UART does not display any data at those times.
        # Not great, but removing battery from Puck.js resolves this.
        logger.debug("No valid datapoint value read ('%s'). Try it with nRF UART? Reset battery?" % (datapoint))
        return False

def reset_datapoint(datapoint):
    """
    """
    # TODO: het verschil tussen de nieuwe angle en oude omzetten naar een teller die iets van 500 graden is (iets minder dan twee keer de dop draaien zeg maar)
    # TODO: afvangen wanneer hij van 0 naar 359 rolt zodat je geen rare effecten krijgt :]
    if datapoint_of_last_volume_change:
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
    # TODO: Move resetting of datapoints

    # Set globals in order to make it possible to globally change them
    global last_datapoint
    global last_volume
    global datapoint_of_last_volume_change

    if not datapoint:
        # Set volume to minimum when no datapoint was received.
        volume = min_volume
    else:
        difference = abs(datapoint - datapoint_of_last_volume_change)
        logger.debug("Difference: %s" % (difference))

        # As soon as the minimum change is reached, change volume
        # If change is too big, consider it an error and do nothing
        if difference >= step and difference <= step*max_volume_change:
            logger.debug("|%s-%s|=%s, bigger than step %s" % (datapoint, datapoint_of_last_volume_change, difference, step))

            # Calculate new volume with floor division of steps and last known value for volume
            if datapoint_of_last_volume_change < datapoint:
                # Turn it up
                volume = last_volume + difference//step
            if datapoint_of_last_volume_change > datapoint:
                # Turn it down
                volume = last_volume + difference//step
            logger.debug("Volume: %s, Last volume: %s, Change: %s" % (volume, last_volume, difference))

            # Respect min and max volume
            if volume > max_volume:
                volume = max_volume
                logger.debug("Reset to max volume (%s)" % (max_volume))
            if volume < min_volume:
                volume = min_volume
                logger.debug("Reset to min volume (%s)" % (min_volume))

        else:
            volume = last_volume

    #Update globals
    if volume != last_volume:
        # Volume was changed!
        datapoint_of_last_volume_change = datapoint
    last_datapoint = new_datapoint
    return volume


# Connect to Puck.js
logger.debug("Connecting...")
p = btle.Peripheral("C3:25:1D:C7:EF:BD", btle.ADDR_TYPE_RANDOM)
logger.debug("Connected to: %s" % (p))

#TODO: Maybe disconnect and connect here, to restore f'ed up connections. These seem to result in weird data.

# Enable notifications
time.sleep(1)
p.writeCharacteristic(12, "\x01\x00", False)
time.sleep(1)

try:
    # set some initial values for global vars
    last_volume = min_volume
    datapoint_of_last_volume_change = False
    first_datapoint = False

    # Setup UDP connection
    # As per https://wiki.python.org/moin/UdpCommunication
    UDP_IP = "169.254.3.101"
    UDP_PORT = 5555
    sock = socket.socket(socket.AF_INET, # Internet
                        socket.SOCK_DGRAM) # UDP

    # Check puck.js, transform data to volume, send, repeat
    while True:
        # Read datapoint form Puck.js
        new_datapoint = read_datapoint()

        # When valid datapoint is found (and not False)
        if new_datapoint:
            # If this is first occurence of a valid datapoint set some global vars
            if first_datapoint == False:
                first_datapoint = new_datapoint
                last_datapoint = first_datapoint
                datapoint_of_last_volume_change = first_datapoint

                logger.debug("First datapoint: %s" % (first_datapoint))
                logger.debug("Last volume: %s" % (last_volume))
                logger.debug("Datapoint of last volume change: %s" % (datapoint_of_last_volume_change))

            # Calc volume
            volume = transform_data_to_volume(new_datapoint)

            # Send volume only on change of volume
            if volume != last_volume:
                send_volume(volume)
                last_volume = volume
        time.sleep(interval)

except KeyboardInterrupt:
    p.disconnect()
    logger.debug("Bye")
except Exception:
    raise
finally:
    if p: p.disconnect()
    logger.debug("Disconnected")
