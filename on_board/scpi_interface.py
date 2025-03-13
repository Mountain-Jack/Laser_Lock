import time
import numpy as np
import sys

def setup_redpitaya(rp_s, trigger_level, decimation, timeout=5):
    """Set up the Red Pitaya with a timeout."""
    start_time = time.time()
    try:
        # Input Setup
        rp_s.tx_txt('ACQ:RST')
        rp_s.tx_txt('ACQ:DATA:FORMAT ASCII')  # Set data format
        rp_s.tx_txt('ACQ:DATA:Units VOLTS')   # Set data units
        rp_s.tx_txt(f'ACQ:DEC {decimation}')  # Set decimation
        rp_s.tx_txt(f'ACQ:TRIG:LEV {trigger_level}')
        
        # Output Setup  
        rp_s.tx_txt('GEN:RST')
        rp_s.tx_txt('SOUR1:FUNC DC')          # Set output 1 to DC mode
        rp_s.tx_txt('SOUR1:FREQ:FIX 2000')
        rp_s.tx_txt('SOUR1:VOLT 0')           # Initialize output 1 voltage to 0
        rp_s.tx_txt('OUTPUT1:STATE ON')       # Enable output 1

        # Check if the setup process exceeds the timeout
        if time.time() - start_time > timeout:
            raise TimeoutError("Setup process exceeded the timeout of 5 seconds.")

    except TimeoutError as e:
        print(f"Setup Timeout: {e}")
        raise
    except Exception as e:
        print(f"Setup Failed: {e}")
        raise

def acquire_data(rp_s, data_slice, retries=10, delay=5):
    """Acquire data from both input channels with retry logic."""
    for attempt in range(retries):
        try:
            rp_s.tx_txt('ACQ:START')
            rp_s.tx_txt('ACQ:TRIG EXT_PE')
            rp_s.tx_txt('ACQ:TRIG:DLY 8192')
            start_time = time.time()
            while time.time() - start_time < 5:
                rp_s.tx_txt('ACQ:TRIG:STAT?')
                if rp_s.rx_txt() == 'TD':
                    break
            else:
                raise TimeoutError("Timeout waiting for trigger")

            start_time = time.time()
            while time.time() - start_time < 5:
                rp_s.tx_txt('ACQ:TRIG:FILL?')
                if rp_s.rx_txt() == '1':
                    break
            else:
                raise TimeoutError("Timeout waiting for buffer to fill")

            # Acquire data from both channels
            rp_s.tx_txt('ACQ:SOUR1:DATA?')
            buff_string1 = rp_s.rx_txt()
            # Prepare data for NumPy Array
            buff_string1 = buff_string1.strip('{}\n\r').replace("  ", "").split(',')
            # Slice data
            buff_string1 = buff_string1[::data_slice]
            data1 = np.array(list(map(float, buff_string1)))

            rp_s.tx_txt('ACQ:SOUR2:DATA?')
            buff_string2 = rp_s.rx_txt()
            buff_string2 = buff_string2.strip('{}\n\r').replace("  ", "").split(',')
            buff_string2 = buff_string2[::data_slice]
            data2 = np.array(list(map(float, buff_string2)))
            
            return data1, data2

        except TimeoutError as e:
            print(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay} seconds...")
            time.sleep(delay)
        except Exception as e:
            print(f"An error occurred: {e}")
            break

    print("Failed to acquire data after multiple attempts.")
    sys.exit(1)
    return None, None

def output_feedback_voltage(rp_s, feedback):
    """Outputs a correction voltage on the Red Pitaya based on the feedback parameter."""
    try:
        # Convert feedback to a voltage level
        voltage = feedback / 1000  # Adjust scaling as necessary
        voltage = max(min(voltage, 1.0), -1.0)  # Clamp the voltage to [-1, 1]
        voltage = f"{voltage:.3f}"
        # Send the command to set the output voltage
        rp_s.tx_txt(f'SOUR1:VOLT:OFFS {voltage}')
        return voltage
    except Exception as e:
        print(f"Failed to set output voltage: {e}")
        return None