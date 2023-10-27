import os
import struct

# Define the structure format for each header field


# Function to interpret the on/off status
def get_channel_status(status):
    return "ON" if status == 1 else "OFF"


def convert_magnitude_index(index):
    magnitudes = ['YOCTO', 'ZEPTO', 'ATTO', 'FEMTO', 'PICO', 'NANO', 'MICRO', 'MILLI', '(1)', 'KILO', 'MEGA', 'GIGA', 'TERA', 'PETA', 'EXA', 'ZETTA', 'YOTTA']
    
    if 0 <= index < len(magnitudes):
        return f"{index} to {magnitudes[index]}"
    else:
        return "Index out of range"

def convert_unitsystem_index(index):
    unitsystems = ['V A S', 'dBV', 'dBA', 'dB', 'VPP', 'VDC', 'DBM', 'SA', 'DT_DIV', 'PTS', 'NULL_SENSE', 'DEGREE', 'PERCENT']
    
    if 0 <= index < len(unitsystems):
        return f"{index} to {unitsystems[index]}"
    else:
        return "Index out of range"

def read_unit_data_structure(data):

    header_format = '<dIIIIIIII'
    f_value, magnitude, unit_selector, V_num, V_denum, A_num, A_denum, S_num, S_denum  = struct.unpack(header_format, data)

    print(f"  BaseValue: {f_value}")
    print(f"  Magnitude: {convert_magnitude_index(magnitude)}")
    print(f"  Unit system: {convert_unitsystem_index(unit_selector)}")
    print(f"  V pow: {V_num} / {V_denum}")
    print(f"  A pow: {A_num} / {A_denum}")
    print(f"  S pow: {S_num} / {S_denum}")

    return 0


# Function to read and print the header values
def read_header_values(file_path):
    if os.path.getsize(file_path) < 36:
        print("File size is less than 36 bytes. Cannot unpack the header.")
        return

    with open(file_path, 'rb') as file:

        header_data = file.read(24)  # Read the first 24 bytes (header data)
        header_format = '<IIIIII'
        version, data_offset, ch1_status, ch2_status, ch3_status, ch4_status = struct.unpack(header_format, header_data)

        # Print the interpreted values
        print(f"Version: {version}")
        print(f"Data Offset: {data_offset}")

        analog_channels = ["CH1", "CH2", "CH3", "CH4"]
        for ch in analog_channels:
            print(f"{ch} Status:")
            print(f" Status: {get_channel_status(ch1_status)}")

        for ch in analog_channels:
            print(f"{ch} Volt/Div:")

            header_data = file.read(40)  # Read the first 24 bytes (header data)
            header_format = '<dIIIIIIII'
            f_value, magnitude, unit_selector, V_num, V_denum, A_num, A_denum, S_num, S_denum  = struct.unpack(header_format, header_data)

            print(f"  BaseValue: {f_value}")
            print(f"  Magnitude: {convert_magnitude_index(magnitude)}")
            print(f"  Unit system: {unit_selector}")
            print(f"  V pow: {V_num} / {V_denum}")
            print(f"  A pow: {A_num} / {A_denum}")
            print(f"  S pow: {S_num} / {S_denum}")

        for ch in analog_channels:
            print(f"{ch} Vertical offset:")

            header_data = file.read(40)  # Read the first 24 bytes (header data)
            header_format = '<dIIIIIIII'
            f_value, magnitude, unit_selector, V_num, V_denum, A_num, A_denum, S_num, S_denum  = struct.unpack(header_format, header_data)

            print(f"  BaseValue: {f_value}")
            print(f"  Magnitude: {convert_magnitude_index(magnitude)}")
            print(f"  Unit system: {unit_selector}")
            print(f"  V pow: {V_num} / {V_denum}")
            print(f"  A pow: {A_num} / {A_denum}")
            print(f"  S pow: {S_num} / {S_denum}")

        header_data = file.read(4)  # Read the first 24 bytes (header data)
        header_format = '<I'
        digital_status = struct.unpack(header_format, header_data)
        print(f"Digital channels: {get_channel_status(digital_status)}")

        header_data = file.read(64)  # Read the first 24 bytes (header data)
        header_format = '<IIIIIIIIIIIIIIII'
        digital_ch_status = struct.unpack(header_format, header_data)

        digital_channels = ["D1", "D2", "D3", "D4", "D5", "D6", "D7", "D8", "D9", "D10", "D11", "D12", "D13", "D14", "D15", "D16"]


        print(f"Digital channels: {get_channel_status(digital_status)}")
        for index, ch in enumerate(digital_channels):
            print(f"  {ch} Status: {get_channel_status(digital_ch_status[index])}")


        print(f"Time base:")
        header_data = file.read(40)
        time_div = read_unit_data_structure(header_data)

        print(f"Time delay:")
        header_data = file.read(40)
        time_delay = read_unit_data_structure(header_data)

        header_data = file.read(4)
        header_format = '<I'
        [analog_points] = struct.unpack(header_format, header_data)
        print(f"Analog data points: {analog_points}")

        position = file.tell()  # Get the updated file position
        print(f"File Pointer Position: {hex(position)}")

        print(f"Sample rate:")
        header_data = file.read(40)
        time_delay = read_unit_data_structure(header_data)

        header_data = file.read(4)
        header_format = '<I'
        [digital_points] = struct.unpack(header_format, header_data)
        print(f"Digital data points: {digital_points}")

        print(f"Digital sample rate:")
        header_data = file.read(40)
        time_delay = read_unit_data_structure(header_data)

        print(f"Probe values:")
        for ch in analog_channels:
            header_data = file.read(8)        
            header_format = '<d'
            [probe] = struct.unpack(header_format, header_data)
            print(f"  {ch} probe: {probe}")

        header_data = file.read(1)
        header_format = 'B'
        [data_width] = struct.unpack(header_format, header_data)
        print(f"Data width: {data_width}")

        header_data = file.read(1)
        header_format = 'B'
        [byte_order] = struct.unpack(header_format, header_data)
        print(f"Byte order: {byte_order}")


if __name__ == "__main__":
    file_path = 'usr_wf_data.bin'  # Replace with the actual file path
    read_header_values(file_path)