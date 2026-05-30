import serial, time

class HardwareInterface:
    def __init__(self, port, baudrate=9600):
        self.port = port
        self.baudrate = baudrate
        self.serial_connection = None
        self.distance = None
        self.speed = None

    def process_data(self, data):
        # --- process serial commands ---


        data_array = data.split(";")
        
        if data_array[0] == "BOOT_UP":
            print("Boot up command received.")
            self.send_data("BOOT_UP_CMD_END")
        elif data_array[0] == "NOTE_ON" or data_array[0] == "NOTE_OFF":
            print("Wait...")
            time.sleep(0.1)
            print("this is supposed to be the other way around but it works so whatever")

            self.send_data("NOTE_CMD_END")
        elif data_array[0] == "WAS_WIRD":
            print("Ping received. Sending PONG response.")
            self.send_data("WAS_WIRD_CMD_END")
        elif data_array[0] == "CALIBRATE":
            print("Calibrate command received.")

            self.distance = data_array[1]
            self.speed = data_array[2]

            self.send_data("CALIBRATE_CMD_END")

    def listen(self):
        if self.serial_connection and self.serial_connection.is_open:
            while True:
                for line in self.serial_connection.readlines():
                    decoded_line = line.decode().strip()
                    print(f"Received data: {decoded_line}")
                    self.process_data(decoded_line)

                time.sleep(0.1)  # Avoid busy waiting

    def connect(self):
        try:
            self.serial_connection = serial.Serial(self.port, self.baudrate)
            print(f"Connected to hardware on {self.port} at {self.baudrate} baud.")

            self.serial_connection.timeout = 1 # timeout
        except serial.SerialException as e:
            print(f"Error connecting to hardware: {e}")

    def send_data(self, data):
        if self.serial_connection and self.serial_connection.is_open:
            try:
                self.serial_connection.write(data.encode())
                print(f"Sent data: {data}")
            except serial.SerialException as e:
                print(f"Error sending data: {e}")
        else:
            print("Serial connection is not open. Please connect first.")

    def disconnect(self):
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.close()
            print("Disconnected from hardware.")
