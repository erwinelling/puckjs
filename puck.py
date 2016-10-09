from bluepy import btle
import time
import socket
import sys

# Settings
max_volume = 22

def read_datapoint():
    """
    Read the data from the characteristic from Puck.js we need.
    Found out the correct handle for this characteristic with:
    # chars = p.getCharacteristics()
    # for c in chars:
    # print c.uuid, c.getHandle(), c.propertiesToString(), c.read()
    """
    try:
        # Read datapoint and cast to int
        datapoint = int(p.readCharacteristic(11))
        print "Read: %s, %s" % (type(datapoint), datapoint)
        return datapoint
    except:
        # Sometimes no integer, but '<- Serial1\r\n>' is returned.
        print "No valid datapoint read. Try it with nRF UART."
        return 0

def reset_datapoint(datapoint):
    """
    Het eerste datapunt dat binnenkomt wordt ons uitgangspunt, dus 0.
    """
    return datapoint - first_datapoint

def send_volume(volume):
    """
    Versturen via netwerk

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
    global last_datapoint


    # TODO:
    # - het verschil tussen de nieuwe angle en oude omzetten naar een teller die iets van 500 graden is (iets minder dan twee keer de dop draaien zeg maar)
    # - afvangen wanneer hij van 0 naar 359 rolt zodat je geen rare effecten krijgt :]
    # - Die teller omzetten naar het volume getal (tussen de 0 en de 22)
    if not datapoint:
        volume = 0
    elif datapoint == -1:
        volume = max_volume
    else:
        # TODO: afvangen als ik iets anders krijg dan integer 0-359? (i.e. -1?)
        previous_datapoint = last_datapoint
        last_datapoint = datapoint
        difference_with_previous = datapoint - previous_datapoint
        difference_with_first = datapoint - first_datapoint
        print "First datapoint: %s, Previous datapoint: %s, Last datapoint: %s, Difference: %s (and %s with first)" % (first_datapoint, previous_datapoint, datapoint, difference_with_first, difference_with_previous)

        # RESET
        print "First_datapoint: %s, Previous datapoint: %s, Last datapoint: %s <-- AFTER RESET" % (reset_datapoint(first_datapoint), reset_datapoint(previous_datapoint), reset_datapoint(datapoint))
        # 506/23 = 22
        # 22
        # Return volume here
        volume = datapoint
    print "Volume: %s" % (volume)
    return volume

try:
    # Connect to Puck.js
    # TODO: Catch exception when Puck is not around
    p = btle.Peripheral("C3:25:1D:C7:EF:BD", btle.ADDR_TYPE_RANDOM)
    print "Connected to: %s" % (p)

    # Get first data
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
        if volume: send_volume(volume)

        #TODO: sleep for a shorter while here
        time.sleep(2)

except KeyboardInterrupt:
    print "Bye"
except:
    print "Error: ", sys.exc_info()[0]
    raise
finally:
    p.disconnect()
    print "Disconnected"
