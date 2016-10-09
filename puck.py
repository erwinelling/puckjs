from bluepy import btle
import time


# TODO: Catch exception when Puck is not around
p = btle.Peripheral("C3:25:1D:C7:EF:BD", btle.ADDR_TYPE_RANDOM)
print "connected to %s" % (p)

# for c in chars:
# print c.uuid, c.getHandle(), c.propertiesToString(), c.read()


ble_datapoint = p.readCharacteristic(11)

first_ble_datapoint = ble_datapoint
last_ble_datapoint = ble_datapoint
print "First datapoint: %s" % (first_ble_datapoint)

def transform_data(ble_datapoint):
    # afvangen als ik iets anders krijg dan 0-359
    # - het verschil tussen de nieuwe angle en oude omzetten naar een teller die iets van 500 graden is (iets minder dan twee keer de dop draaien zeg maar)
    # - afvangen wanneer hij van 0 naar 359 rolt zodat je geen rare effecten krijgt :]
    # - Die teller omzetten naar het volume getal (tussen de 0 en de 22)
    # - Dit uitsturen over netwerk in die ascii code die in het Bash script staat.
    global last_ble_datapoint
    
    if ble_datapoint:
        previous_ble_datapoint = last_ble_datapoint
        last_ble_datapoint = ble_datapoint
        difference = ble_datapoint - last_ble_datapoint
        print "Previous datapoint: %s, Last datapoint: %s, Difference: %s" % (previous_ble_datapoint, ble_datapoint, difference)

        # 506/23 = 22
        # 22
        return ble_datapoint
    return False


try:
    while True:
        transformed_data = transform_data(p.readCharacteristic(11))
        if transformed_data:
            print "Transformed data: %s" % (transform_data)
        #TODO: maybe sleep for a shorter while here
        #TODO: send value via network in ascii code
        time.sleep(0.5)
finally:
    p.disconnect()
