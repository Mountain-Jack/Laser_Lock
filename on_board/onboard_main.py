#!/usr/bin/env python3
from scpi_interface import setup_redpitaya
from DeviceManager import DeviceManager
import sys
def main():
    # Create an instance of the DeviceManager class
    dev_man = DeviceManager()
    setup_redpitaya(dev_man.rp_s, dev_man.trigger_level, dev_man.decimation)
    # Setup Red Pitaya
    print("Red Pitaya is set up")
    run = True

    while run:
        # Run Main Loop
        if dev_man.use_server:
            dev_man.main_loop_with_server()
        else: 
            dev_man.main_loop_no_server()
        run = dev_man.run

    print("Stopping Program")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)