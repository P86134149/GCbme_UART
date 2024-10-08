import serial
import serial.tools.list_ports as port_list
import os
import time

# 查找可用的串口
def find_serial_port():
    ports = list(port_list.comports())
    if len(ports) == 0:
        print("No serial ports found")
        exit()
    # 打印每個可用端口的設備名稱
    for port in ports:
        print(f"Serial port found: {port.device}")
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
        ser.write(data.encode())
        print(f"Sent: {data}")
    except Exception as ex:
        print(f"Error sending data: {ex}")

# 接收並處理資料
def receive_data(ser, is_binary):
    try:
        while True:
            if ser.in_waiting:
                if is_binary:
                    # 接收二進制數據，並將其傳入 process_data 進行處理
                    data = ser.read(ser.in_waiting)
                    process_data(data)
                else:
                    # 接收文本數據
                    data = ser.readline().decode('utf-8').strip()
                    print(f"Received: {data}")
                    return data
    except Exception as ex:
        print(f"Error receiving data: {ex}")

# 開始信號
# def wait_for_signal(ser):
#     print("Waiting for start signal...")
#     while True:
#         data = ser.read(1)  # 讀取一個字節
#         if data == b'\x03':
#             print("Start signal '0x03' received!")
#             break

buffer = b''  # 用來存儲未處理的數據

def process_data(data):
    global buffer
    buffer += data  # 將新的數據加入緩衝區

    # 檢查是否有完整的數據包（每個包5字節）
    while len(buffer) >= 5:
        # 檢查數據包是否以0x03開頭，並以0xFC結尾
        start_index = buffer.find(b'\x03')
        if start_index == -1:
            # 沒有找到0x03開頭的標識符，丟棄無效的數據
            buffer = b''
            return

        if len(buffer) < start_index + 5:
            # 數據包還不完整，等待更多數據
            return

        packet = buffer[start_index:start_index + 5]  # 提取前5字節的數據包
        buffer = buffer[start_index + 5:]  # 剩餘的數據留在緩衝區

        # 解析數據包
        if packet[0] == 0x03 and packet[4] == 0xFC:
            ecg_high = packet[1]
            ecg_low = packet[2]
            ecg_value = (ecg_high << 8) | ecg_low  # 合併高低位為16位ECG數據
            heart_rate = packet[3]

            # 處理二補碼，如果超過32767，說明是負數
            if ecg_value > 32767:
                ecg_value = ecg_value - 65536

            print(f"ECG Value: {ecg_value}, Heart Rate: {heart_rate}")
            # 將數據存成 txt 檔案
            save_data_to_file(ecg_value, heart_rate)  
        else:
            print("Error: Invalid packet structure")

# 將接收到的資料存成 txt 檔案的函式
def save_data_to_file(ecg_value, heart_rate, filename="ecg_data.txt"):
    with open(filename, "a") as file:
        file.write(f"ECG Value: {ecg_value}, Heart Rate: {heart_rate}\n")

# 測試收發流程
def test_uart():
    port = find_serial_port()
    ser = init_serial(port)

    # 等待開發板傳來開始信號
    # wait_for_signal(ser)
    
    # 發送資料給開發板
    # send_data(ser, 'PC ready to receive data')
    
    # 接收開發板傳來的分類結果
    # 如果是ECG數據，設定is_binary=True
    while True:
        receive_data(ser, is_binary=False)  # 這裡設為True來接收二進制數據
    
    ser.close()

# 呼叫測試函數
if __name__ == "__main__":
    test_uart()
