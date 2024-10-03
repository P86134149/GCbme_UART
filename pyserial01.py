import time ,serial
import serial.tools.list_ports as port_list

ports = list(port_list.comports())
if len(ports) == 0:
    print("No serial ports found")
    exit()
port = ports[0].device

ser = serial.Serial()
ser.port = port
print("serial port = ", port)

#115200,N,8,1
ser.baudrate = 115200
ser.bytesize = serial.EIGHTBITS #number of bits per bytes
ser.parity = serial.PARITY_NONE #set parity check
ser.stopbits = serial.STOPBITS_ONE #number of stop bits
  
ser.timeout = 0.5          #non-block read 0.5s
ser.writeTimeout = 0.5     #timeout for write 0.5s
ser.xonxoff = False    #disable software flow control
ser.rtscts = False     #disable hardware (RTS/CTS) flow control
ser.dsrdtr = False     #disable hardware (DSR/DTR) flow control

try: 
    ser.open()
except Exception as ex:
    print ("open serial port error " + str(ex))
    exit()  


def send_data(data):
    try:
        ser.write(data.encode())
        print(f"Sent: {data}")
    except Exception as ex:
        print("Error sending data: " + str(ex))

def receive_data():
  try:
    while True:
      if ser.in_waiting:
        raw_data = ser.read(2)  # Read 2 bytes for int16
        if len(raw_data) == 2:
          data = int.from_bytes(raw_data, byteorder='little', signed=True)
          print(f"Received: {data}")
  except Exception as ex:
    print("Error receiving data: " + str(ex))
# Example usage
# send_data("Hello UART")
time.sleep(1)
receive_data()

ser.close()