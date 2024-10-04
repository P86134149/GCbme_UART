import serial # pip install pyserial
import serial.tools.list_ports as port_list

# 查找可用的串口
def find_serial_port():
    ports = list(port_list.comports())
    if len(ports) == 0:
        print("No serial ports found")
        exit()
    return ports[1].device

# 初始化串口
def init_serial(port, baudrate=115200, timeout=0.5):
    ser = serial.Serial()
    ser.port = port
    ser.baudrate = baudrate
    ser.bytesize = serial.EIGHTBITS  # 8 bits per byte
    ser.parity = serial.PARITY_NONE  # no parity bit
    ser.stopbits = serial.STOPBITS_ONE  # 1 stop bit
    ser.timeout = timeout  # read timeout
    ser.writeTimeout = timeout  # write timeout
    ser.xonxoff = False  # no software flow control
    ser.rtscts = False  # no hardware (RTS/CTS) flow control
    ser.dsrdtr = False  # no hardware (DSR/DTR) flow control
    
    try:
        ser.open()
        print(f"Serial port {port} opened.")
    except Exception as ex:
        print(f"Error opening serial port: {ex}")
        exit()
    
    return ser

# 傳送資料
def send_data(ser, data):
    try:
        ser.write(data.encode()) # default is utf-8
        print(f"Sent: {data}")
    except Exception as ex:
        print(f"Error sending data: {ex}")

def receive_data(ser, data_type):
    try:
        while True:
            if ser.in_waiting:
                # 讀取串口緩衝區中的所有可用數據
                raw_data = ser.read(ser.in_waiting)

                if data_type == "binary":
                    # 處理二進制數據
                    process_data(raw_data)  # 假設有 process_data 函數來處理二進制數據
                    print(f"Received binary data: {raw_data}")

                elif data_type == "hex":
                    # 將二進制數據轉換為十六進制字串
                    hex_data = raw_data.hex()
                    print(f"Received hex data: {hex_data}")
                    return hex_data

                elif data_type == "string":
                    # 將數據解碼為字串（處理UTF-8編碼數據）
                    try:
                        string_data = raw_data.decode('utf-8').strip()
                        print(f"Received string data: {string_data}")
                        return string_data
                    except UnicodeDecodeError:
                        print("Error decoding data as string. Not a valid UTF-8 sequence.")

                else:
                    print("Unsupported data type. Please specify 'binary', 'hex', or 'string'.")
                    return None

    except Exception as ex:
        print(f"Error receiving data: {ex}")


# 開始信號
def wait_for_signal(ser, signal='ready'):
    print("Waiting for start signal...")
    while True:
        data = receive_data(ser, data_type="binary")  # 等待ASCII格式的開始信號
        if data == signal:
            print("Start signal received!")
            break

buffer = b''  # 用來存儲未處理的數據

def process_data(data):
    global buffer
    buffer += data  # 將新的數據加入緩衝區

    # 檢查是否有完整的數據包（每個包5字節）
    while len(buffer) >= 5:
        packet = buffer[:5]  # 提取前5字節的數據包
        buffer = buffer[5:]  # 剩餘的數據留在緩衝區

        # 解析數據包
        ecg_high = packet[1]
        ecg_low = packet[2]
        ecg_value = (ecg_high << 8) | ecg_low  # 合併高低位為16位ECG數據
        heart_rate = packet[3]
        end_byte = packet[4]

        if end_byte == 0xFC:
            # 處理二補碼，如果超過32767，說明是負數
            if ecg_value > 32767:
                ecg_value = ecg_value - 65536
            print(f"ECG Value: {ecg_value}, Heart Rate: {heart_rate}")
        else:
            print("Error: Invalid packet ending")

# 測試收發流程
def test_uart():
    port = find_serial_port()
    ser = init_serial(port)
    
    # 等待開發板傳來開始信號
    wait_for_signal(ser)
    
    # 發送資料給開發板
    send_data(ser, 'PC ready to send data')
    
    # 接收開發板傳來的分類結果
    # 如果是ECG數據，設定is_binary=True
    receive_data(ser, is_binary=True)  # 這裡設為True來接收二進制數據
    
    ser.close()

# 呼叫測試函數
if __name__ == "__main__":
    test_uart()
