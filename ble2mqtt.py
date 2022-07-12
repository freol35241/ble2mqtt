# MIT License

# Copyright (c) 2021 freol35241

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""ble2mqtt - simple python script acting as a one-way gateway for advertisement
packets from ble to mqtt"""

import asyncio
import logging
import argparse
from textwrap import wrap

import aioblescan as aiobs
from bleparser import BleParser
import paho.mqtt.client as mqtt


def run(config: argparse.Namespace):
    """Main function setting up and running the gateway functionality

    Args:
        config (argparse.Namespace): argparse command line config
    """

    ## Setup MQTT connection
    client = mqtt.Client()
    if config.username and config.password:
        client.username_pw_set(config.username, config.password)

    logging.info("Connecting to %s:%d", config.host, config.port)
    client.connect(config.host, config.port)
    client.loop_start()  # Will handle reconnections automatically

    ## Setup parser
    ble_parser = BleParser(discovery=True, filter_duplicates=True)

    ## Define callback
    def process_hci_events(data):
        sensor_data, tracker_data = ble_parser.parse_data(data)

        logging.debug("Received sensor data: %s", sensor_data)
        logging.debug("Received tracker data: %s", tracker_data)

        for parsed in (sensor_data, tracker_data):
            if parsed:
                mac = ":".join(wrap(parsed.pop("mac"), 2))

                logging.info("Received data from mac: %s", mac)
                logging.debug("%s", parsed)

                for key, value in parsed.items():
                    client.publish(f"{config.base_topic}/{mac}/{key}", value)

    ## Get everything connected
    loop = asyncio.get_event_loop()

    #### Setup socket and controller
    socket = aiobs.create_bt_socket(config.device)
    fac = getattr(loop, "_create_connection_transport")(
        socket, aiobs.BLEScanRequester, None, None
    )
    _, btctrl = loop.run_until_complete(fac)

    #### Attach callback
    btctrl.process = process_hci_events
    loop.run_until_complete(btctrl.send_scan_request(0))

    ## Run forever
    loop.run_forever()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="A one-way gateway for advertisement packets from ble to mqtt"
    )
    parser.add_argument("host", type=str, help="Hostname of MQTT broker")
    parser.add_argument("port", type=int, help="Port number of MQTT broker")
    parser.add_argument(
        "-u",
        "--username",
        type=str,
        default=None,
        help="Username to use for accessing the MQTT broker",
    )
    parser.add_argument(
        "-p",
        "--password",
        type=str,
        default=None,
        help="Password to use for accessing the MQTT broker",
    )
    parser.add_argument(
        "-b",
        "--base-topic",
        type=str,
        default="ble2mqtt",
        help="Base topic onto which all advertisements will be published",
    )
    parser.add_argument(
        "-d",
        "--device",
        type=int,
        default=0,
        help="HCI device number to use for connecting to the bluetooth device",
    )

    conf = parser.parse_args()
    run(conf)
