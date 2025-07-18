import serial.tools.list_ports
import serial
import sys
import threading
import time
import random
from scripts.generated_pb2 import LedCommands, AhtTelemetry
from google.protobuf.message import DecodeError

def get_serial_port():
    ports = serial.tools.list_ports.comports()

    if not ports:
        print("could not find usbserial")

    ports_len = len(ports)
    if ports_len > 1:
        for index, port in enumerate(ports):
            print(f"{index}: {port}")

        while True:
            idx = input("Enter a port number: ")
            try:
                port = ports[int(idx)]
                return port
            except Exception as err:
                print(f"{err}")
    else:
        return ports[0]

def main():
    args = sys.argv
    verbose = len(args) > 1 and (args[1] == "--verbose" or args[1] == "--v")

    if verbose:
        print("running in verbose mode")

    serial_port = get_serial_port()
    if not serial_port:
        return;

    print(f"using `{serial_port}`")

    try:
        with serial.Serial(
            port = serial_port.device,
            baudrate = 9600,
            bytesize = serial.EIGHTBITS,
            parity = serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            rtscts=False,
            dsrdtr=False,
            timeout=0,
            write_timeout=0,
        ) as serial_device:
            if verbose:
                print(f"serial port `{serial_device} opened successfully`")
            read_thread = threading.Thread(target=read_routine, args=(serial_device, verbose))
            read_thread.start()
            write_routine(serial_device, verbose)

    except Exception as e:
        print(f"error opening serial port: {e}")

def read_routine(serial_dev, verbose):
    while True:
        try:
            if not serial_dev.is_open:
                print("device suddenly disconnected")
                return
            bytes = serial_dev.read(8)

            
            bytes_len = len(bytes)

            if len(bytes) == 0:
                continue

            print(bytes_len)
            telemetry = AhtTelemetry()
            telemetry.ParseFromString(bytes)

            # from the AHM spec sheet
            humidity = (telemetry.humidity / (1 << 20)) * 100
            temperature = (telemetry.temperature / (1 << 20)) * 200 - 50

            print(f"humidity: {humidity}%")
            print(f"temperature: {temperature} C")
        except DecodeError as err:
            print(f"decoding error: {err}")
        except Exception as err:
            print(f"error during reading: {err}")
            return

def write_routine(serial_dev, verbose):
    while True:
        if not serial_dev.is_open:
            print("device suddenly disconnected")
            return
        timeout_dur = random.randint(500, 2000)
        time.sleep(timeout_dur / 1000)
        outgoing = LedCommands()
        outgoing.brightness_1 = random.randint(0, 4095)
        outgoing.brightness_2 = random.randint(0, 4095)
        outgoing.brightness_3 = random.randint(0, 4095)
        if verbose:
            print(f"sending {outgoing}")
        bytes = outgoing.SerializeToString()
        try:
            serial_dev.write(bytes)
        except Exception as err:
            print(f"error during writing: {err}")
            return

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("")
