from bluepy import btle


# TODO: Catch exception when Puck is not around
conn = btle.Peripheral("C3:25:1D:C7:EF:BD", btle.ADDR_TYPE_RANDOM)


# for c in chars:
# print c.uuid, c.getHandle(), c.propertiesToString(), c.read()


ble_data = p.readCharacteristic(11)
first_ble_datapoint = ble_data
last_ble_datapoint = ble_data

def transform_data(ble_data):
    # transform
    return ble_data

while True:
    print transform_data(p.readCharacteristic(11))
    #TODO: maybe sleep for a short while here
