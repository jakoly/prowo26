import serial
import time


class HardwareInterface:
    def __init__(self, port: str, baudrate: int = 9600):
        self.port = port
        self.baudrate = baudrate
        self.serial_connection = None
        # FIX 10: Typen korrekt – werden in CALIBRATE zu float konvertiert
        self.distance: float | None = None
        self.speed: float | None = None

    def process_data(self, data: str):
        """Parse and handle incoming serial commands."""
        data_array = data.split(";")
        command = data_array[0]

        if command == "BOOT_UP":
            print("Boot up command received.")
            self.send_data("BOOT_UP_CMD_END")

        elif command in ("NOTE_ON", "NOTE_OFF"):
            # FIX 9: Debug-Kommentar entfernt; klarer Kommentar stattdessen
            # NOTE_ON/NOTE_OFF werden vom Arduino gespiegelt – kurze Pause vor Antwort
            time.sleep(0.1)
            self.send_data("NOTE_CMD_END")

        elif command == "WAS_WIRD":
            print("Ping received. Sending PONG response.")
            self.send_data("WAS_WIRD_CMD_END")

        elif command == "CALIBRATE":
            # FIX 8: Index-Check gegen malformed Nachrichten
            if len(data_array) < 3:
                print(f"Malformed CALIBRATE command (expected 3 fields, got {len(data_array)}): {data!r}")
                return
            try:
                # FIX 10: String zu float konvertieren
                self.distance = float(data_array[1])
                self.speed = float(data_array[2])
                print(f"Calibrate command received. Distance: {self.distance}, Speed: {self.speed}")
            except ValueError as e:
                print(f"Invalid CALIBRATE values: {e}")
                return
            self.send_data("CALIBRATE_CMD_END")

        else:
            print(f"Unknown command received: {command!r}")

    def listen(self):
        """Continuously read and process incoming serial lines."""
        if not (self.serial_connection and self.serial_connection.is_open):
            print("Serial connection is not open. Please connect first.")
            return

        while True:
            # FIX 7: readline() statt readlines() – verarbeitet Nachrichten sofort
            line = self.serial_connection.readline()
            if line:
                decoded_line = line.decode().strip()
                print(f"Received data: {decoded_line}")
                self.process_data(decoded_line)
            else:
                time.sleep(0.1)  # Avoid busy waiting when no data arrives

    def connect(self):
        """Open the serial connection to the hardware."""
        try:
            # FIX 6: Timeout direkt im Konstruktor setzen
            self.serial_connection = serial.Serial(
                self.port,
                self.baudrate,
                timeout=1,
            )
            print(f"Connected to hardware on {self.port} at {self.baudrate} baud.")
        except serial.SerialException as e:
            print(f"Error connecting to hardware: {e}")

    def send_data(self, data: str):
        """Send a string command over the serial connection."""
        if self.serial_connection and self.serial_connection.is_open:
            try:
                self.serial_connection.write(data.encode())
                print(f"Sent data: {data}")
            except serial.SerialException as e:
                print(f"Error sending data: {e}")
        else:
            print("Serial connection is not open. Please connect first.")

    def disconnect(self):
        """Close the serial connection."""
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.close()
            print("Disconnected from hardware.")