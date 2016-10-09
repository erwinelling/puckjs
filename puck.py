from bluepy import btle
import time
import socket
import sys

# Settings
puck_mac = "C3:25:1D:C7:EF:BD" # mac address of BLE device
puck_char = 11 # characteristic of the BLE device to read
min_volume = 0
max_volume = 22
interval = 4 # in seconds
degrees_zero = False # set for static 0 point, i.e. lid = closed & volume = 0; Set to False to use value of first datapoint

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
        print "No valid datapoint read. Try it with nRF UART?"
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
    print "Sent: %s to %s:%s" % (message, UDP_IP, str(UDP_PORT))

def transform_data_to_volume(datapoint):
    """
    #pick max rotation, make it a hard cap
    #same for min rotation
    #set maximum allowed difference, so only real turning works
    #After -1 make sure to reset the heading var to first new heading coming in,
    #without comparing to old heading
    """

    global last_datapoint


    # TODO: het verschil tussen de nieuwe angle en oude omzetten naar een teller die iets van 500 graden is (iets minder dan twee keer de dop draaien zeg maar)
    # TODO: afvangen wanneer hij van 0 naar 359 rolt zodat je geen rare effecten krijgt :]
    if not datapoint:
        # Set volume to minimum when no datapoint was received.
        # Somehow, this never seems to happen :/
        volume = min_volume
    else:
        # if datapoint == -1:
        #     # Set volume to maximum when magnet is too far away.
        #     volume = max_volume
        #
        # elif previous_datapoint == -1 and datapoint != -1:
        #
        # difference_with_previous = datapoint - previous_datapoint
        #
        # if
        #
        # if difference_with_previous > max_turn_per_interval:
        #     # When rotation is more than max_turn_per_interval assume this is not a real turn
        #     return False

        #minimal turn is totaal/23 of zo
        previous_datapoint = last_datapoint
        last_datapoint = datapoint
        difference_with_first = datapoint - first_datapoint
        difference_with_previous = datapoint - previous_datapoint
        print "First datapoint: %s, Previous datapoint: %s, Last datapoint: %s, Difference: %s (and %s with first)" % (first_datapoint, previous_datapoint, datapoint, difference_with_first, difference_with_previous)

        # RESET
        print "First_datapoint: %s, Previous datapoint: %s, Last datapoint: %s <-- AFTER RESET" % (reset_datapoint(first_datapoint), reset_datapoint(previous_datapoint), reset_datapoint(datapoint))

        # TODO: Die teller omzetten naar het volume getal (tussen de 0 en de 22)
        # Plus of min het verschil met het vorige volume?

        # Return volume
        volume = datapoint//(max_volume-min_volume)
    print "Volume: %s" % (volume)
    return volume

try:
    # Connect to Puck.js
    # TODO: Catch exception when Puck is not around and keep on trying till it is found
    p = btle.Peripheral("C3:25:1D:C7:EF:BD", btle.ADDR_TYPE_RANDOM)
    print "Connected to: %s" % (p)

    # Read first data from Puck.js
    first_datapoint = read_datapoint()
    last_datapoint = first_datapoint
    print "First datapoint: %s" % (first_datapoint)

    # Setup UDP connection
    # As per https://wiki.python.org/moin/UdpCommunication
    UDP_IP = "169.254.3.101"
    UDP_PORT = 5555
    sock = socket.socket(socket.AF_INET, # Internet
                        socket.SOCK_DGRAM) # UDP

    # Check puck.js, transform data to volume, send, repeat
    while True:
        volume = transform_data_to_volume(read_datapoint())
        if volume:
            last_volume = volume
            send_volume(volume)

        #TODO: sleep for a shorter while here
        time.sleep(interval)

except KeyboardInterrupt:
    print "Bye"
except:
    print "Error: ", sys.exc_info()[0]
    raise
finally:
    p.disconnect()
    print "Disconnected"
