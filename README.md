# ble2mqtt
One-way ble-to-mqtt gateway for passive advertisments. It listens in on any passive ble advertisments from sensors/tracker and publish these to a mqtt broker. 

Primarily aimed for the Raspberry pi range of hardware with built-in bluetooth capabilities.

Packaged as a `armv7l` docker image for easy setup:

```
docker run --network=host ghcr.io/freol35241/ble2mqtt
```

## command-line options
````
positional arguments:
  host                  Hostname of MQTT broker
  port                  Port number of MQTT broker

optional arguments:
  -h, --help            show this help message and exit
  -u USERNAME, --username USERNAME
                        Username to use for accessing the MQTT broker
  -p PASSWORD, --password PASSWORD
                        Password to use for accessing the MQTT broker
  -b BASE_TOPIC, --base-topic BASE_TOPIC
                        Base topic onto which all advertisements will be published
  -d DEVICE, --device DEVICE
                        HCI device number to use for connecting to the bluetooth device
```
