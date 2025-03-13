#!/usr/bin/env python3
from scpi_interface import setup_redpitaya
from DeviceManager import DeviceManager
import sys
import time
def main():
    # Create an instance of the DeviceManager class
    dev_man = DeviceManager()
    setup_redpitaya(dev_man.rp_s, dev_man.trigger_level, dev_man.decimation)
    # Setup Red Pitaya
    print("Red Pitaya is set up")

    try:
        # Keep the main thread alive while the DeviceManager threads are running
        while dev_man.run:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping Program")
        dev_man.run = False

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)