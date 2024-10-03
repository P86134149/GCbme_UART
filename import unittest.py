import unittest
from unittest.mock import patch, MagicMock
from uart_receive import read_from_uart, process_data

class TestUARTReceive(unittest.TestCase):

  @patch('uart_receive.serial.Serial')
  def test_read_from_uart(self, mock_serial):
    # Mock the serial instance
    mock_serial_instance = MagicMock()
    mock_serial.return_value = mock_serial_instance
    
    # Mock the in_waiting and readline behavior
    mock_serial_instance.in_waiting = 1
    mock_serial_instance.readline.return_value = b'CMD123\n'
    
    # Call the function
    read_from_uart('COM1', 115200)
    
    # Check if the serial port was opened with correct parameters
    mock_serial.assert_called_with('COM1', 115200, timeout=1)
    
    # Check if the data was processed correctly
    mock_serial_instance.readline.assert_called_once()
    self.assertTrue(mock_serial_instance.close.called)
    
  def test_process_data(self):
    with patch('builtins.print') as mocked_print:
      process_data('CMD123')
      mocked_print.assert_any_call('Command received: CMD123')
      
      process_data('12345')
      mocked_print.assert_any_call('Numeric data received: 12345')
      
      process_data('Hello')
      mocked_print.assert_any_call('Other data received: Hello')

if __name__ == '__main__':
  unittest.main()