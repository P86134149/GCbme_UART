
# Ensure that the serial module is imported

import serial
import serial.tools.list_ports as port_list

ports = list(port_list.comports())
print(ports[0].device)


def read_from_uart(port, baudrate):

    ser = serial.Serial(port, baudrate, timeout=1)

    if ser.in_waiting:

        data = ser.readline().decode('utf-8').strip()

        process_data(data)

    ser.close()



def process_data(data):

    if data.startswith('CMD'):

        print(f'Command received: {data}')

    elif data.isdigit():

        print(f'Numeric data received: {data}')

    else:

        print(f'Other data received: {data}')
