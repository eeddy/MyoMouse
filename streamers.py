import socket
from pyomyo import Myo, emg_mode

def stream_myo():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    m = Myo(mode=emg_mode.FILTERED)
    m.connect()

    def write_to_socket(emg, movement):
        sock.sendto(bytes(str(emg), "utf-8"), ('127.0.0.1', 12345))
    m.add_emg_handler(write_to_socket)

    m.vibrate(1)

    while True:
        try:
            m.run()
        except:
            print("Worker Stopped")
            quit() 