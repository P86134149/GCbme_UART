#數據傳輸（UART）：
當解析到ECG原始數據時，會將其存儲在ECG緩衝區中，並且根據數據的質量和濾波結果進行處理。

在 `#if DV_ENABLE` 區塊中，通過UART將ECG的數據傳送出去。這裡的數據結構是 `DVbuf[5] = {0x03, ECG_Raw[1], ECG_Raw[0], ECG_HeartRate, 0xFC}`，其中：

- `0x03` 是代碼，可能是標識ECG數據類型。
- `ECG_Raw[1]` 和 `ECG_Raw[0]` 是兩個字節的ECG原始數據。
- `ECG_HeartRate` 是心率數據。
- `0xFC` 作為結束字節。

通過 `SERCOM5_USART_Write(DVbuf, sizeof(DVbuf))` 發送數據到串口。
