import serial
import serial.tools.list_ports as port_list
from py_UART02 import find_serial_port
COM_PORT = find_serial_port()
# 設定串口參數，使用你自己的串口號
ser = serial.Serial(COM_PORT, 115200)  # 串口端口設置

# 初始化緩衝區
buffer = b''  # 用來存儲未處理的數據

# 數據處理函數
buffer = b''  # 用來存儲未處理的數據

# 處理接收的二進制數據，並檢查是否為完整的ECG數據包
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
        else:
            print("Error: Invalid packet structure")

# 從串口讀取數據的主循環
while True:
    data = ser.read(ser.in_waiting or 1)  # 等待接收數據
    if data:
        process_data(data)  # 將接收到的數據傳入處理函數
