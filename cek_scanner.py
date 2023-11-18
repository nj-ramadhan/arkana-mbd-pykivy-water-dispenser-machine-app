import serial

ser = serial.Serial(baudrate=115200, port='COM3')

while True :
    data = ser.read_until(b'\r')

    print(str(data, 'UTF-8'))