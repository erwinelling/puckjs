from bluepy import btle
import time


# TODO: Catch exception when Puck is not around
p = btle.Peripheral("C3:25:1D:C7:EF:BD", btle.ADDR_TYPE_RANDOM)
print "connected to %s" % (p)

# for c in chars:
# print c.uuid, c.getHandle(), c.propertiesToString(), c.read()


def read_datapoint():
    """
    """
    return int(p.readCharacteristic(11))

def reset_datapoint(datapoint):
    """
    Het eerste datapunt dat binnenkomt wordt ons uitgangspunt, dus 0.
    """
    return datapoint - first_datapoint

def transform_data(datapoint):

    # - het verschil tussen de nieuwe angle en oude omzetten naar een teller die iets van 500 graden is (iets minder dan twee keer de dop draaien zeg maar)
    # - afvangen wanneer hij van 0 naar 359 rolt zodat je geen rare effecten krijgt :]
    # - Die teller omzetten naar het volume getal (tussen de 0 en de 22)
    # - Dit uitsturen over netwerk in die ascii code die in het Bash script staat.
    global last_datapoint

    if datapoint:
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
        return datapoint
    return False

first_datapoint = read_datapoint()
last_datapoint = first_datapoint
# Deze wordt als volume 0 bestempeld; Je moet dus beginnen met uitlezen als hij dicht zit.
print "First datapoint: %s" % (first_datapoint)

try:
    while True:
        transformed_data = transform_data(read_datapoint())
        if transformed_data:
            print "Transformed data: %s" % (transform_data)
        #TODO: maybe sleep for a shorter while here
        #TODO: send value via network in ascii code
        time.sleep(0.5)
finally:
    p.disconnect()
