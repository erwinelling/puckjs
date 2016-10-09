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

degrees_zero = False # set for static 0 point, i.e. lid = closed & volume = 0; Set to False to use value of first datapoint

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
        logger.debug("No valid datapoint read. Try it with nRF UART?")
        return False

def reset_datapoint(datapoint):
    """
    Use the value of the first datapoint or the value of degrees_zero as absolute 0 point.
    So if no static value is set, make sure to close the lid on startup when calibrating.
    """
    if degrees_zero:
        offset = degrees_zero
    else:
        offset = first_datapoint

    new_value = datapoint - offset
    if new_value < 0:
        new_value = new_value + 360
    return new_value

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
        # TODO: pick max rotation, make it a hard cap
        # TODO: After -1 make sure to reset the heading var to first new heading coming in, without comparing to old heading
        # TODO: het verschil tussen de nieuwe angle en oude omzetten naar een teller die iets van 500 graden is (iets minder dan twee keer de dop draaien zeg maar)
        # TODO: afvangen wanneer hij van 0 naar 359 rolt zodat je geen rare effecten krijgt :]

        previous_datapoint = last_datapoint
        last_datapoint = datapoint

        if abs(reset_datapoint(datapoint) - reset_datapoint(datapoint_of_last_volume_change)) >= step:
            # As soon as the minimum change is reached, change volume
            # Calculate volume with floor division on "resetted" datapoint
            # TODO: don't use datapoint, but use difference and last value for volume
            volume = reset_datapoint(datapoint)//step
            # TODO: Fix volume >360degrees, make it work for 500 degrees?
            if abs(volume - last_volume) > max_volume_change:
                # If change is too big, consider it an error and do nothing
                # TODO: Play with this number
                volume = last_volume


        # difference_with_first = datapoint - first_datapoint
        # difference_with_previous = datapoint - previous_datapoint
        # logger.debug("First datapoint: %s, Previous datapoint: %s, Last datapoint: %s, Difference: %s (and %s with first)" % (first_datapoint, previous_datapoint, datapoint, difference_with_first, difference_with_previous))
        # logger.debug("First_datapoint: %s, Previous datapoint: %s, Last datapoint: %s <-- AFTER RESET" % (reset_datapoint(first_datapoint), reset_datapoint(previous_datapoint), reset_datapoint(datapoint)))

    logger.debug("Volume: %s" % (volume))
    return volume





# Connect to Puck.js
logger.debug("Connecting...")
p = btle.Peripheral("C3:25:1D:C7:EF:BD", btle.ADDR_TYPE_RANDOM)
logger.debug("Connected to: %s" % (p))

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
            new_volume = transform_data_to_volume(new_datapoint)
            if new_volume != last_volume:
                # Only send on volume change
                last_volume = new_volume
                datapoint_of_last_volume_change = new_datapoint
                send_volume(new_volume)

        #TODO: Play with time interval between reads
        time.sleep(interval)

except KeyboardInterrupt:
    logger.debug("Bye")
except Exception:
    raise
finally:
    if p: p.disconnect()
    logger.debug("Disconnected")
