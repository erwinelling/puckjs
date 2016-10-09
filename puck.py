from bluepy import btle


# TODO: Catch exception when Puck is not around
p = btle.Peripheral("C3:25:1D:C7:EF:BD", btle.ADDR_TYPE_RANDOM)
p.connect()
print "connected to %s" % (p)

# for c in chars:
# print c.uuid, c.getHandle(), c.propertiesToString(), c.read()


ble_datapoint = p.readCharacteristic(11)
first_ble_datapoint = ble_datapoint
last_ble_datapoint = ble_datapoint

def transform_data(ble_datapoint):
    # transform
    # - het verschil tussen de nieuwe angle en oude omzetten naar een teller die iets van 500 graden is (iets minder dan twee keer de dop draaien zeg maar)
    # - afvangen wanneer hij van 0 naar 359 rolt zodat je geen rare effecten krijgt :]
    # - Die teller omzetten naar het volume getal (tussen de 0 en de 22)
    # - Dit uitsturen over netwerk in die ascii code die in het Bash script staat.
    if ble_datapoint:
        last_ble_datapoint = ble_datapoint
        return ble_datapoint
    return False



while True:
    try:
        transformed_data = transform_data(p.readCharacteristic(11))
        if transformed_data:
            print first_ble_datapoint, last_ble_datapoint, transformed_data
        #TODO: maybe sleep for a short while here
    finally:
        p.disconnect()
