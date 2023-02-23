import socket
import math

class MyoMouse:
    def __init__(self, velocity=100, proportional_control=True):
        # Socket for reading EMG
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
        self.sock.bind(('127.0.0.1', 12346))

        self.num_clicks = 0
        self.num_r_clicks = 0
        self.VEL = velocity
        self.proportional_control = proportional_control
        while True:
            self.read_data()

    def read_data(self):
        import pyautogui
        data, _ = self.sock.recvfrom(1024)
        data = str(data.decode("utf-8"))
        if data:
            input_class = float(data.split(' ')[0])
            if self.proportional_control:
                multiplier = float(data.split(' ')[1])
                multiplier = multiplier * math.exp(multiplier)
            else:
                multiplier = 1
            # 0 = Hand Closed = down
            if input_class == 0:
                pyautogui.moveRel(0, self.VEL * multiplier)
            # 1 = Hand Open
            elif input_class == 1:
                pyautogui.moveRel(0, -self.VEL * multiplier)
            # 2 = Pinch Index
            elif input_class == 2:
                self.num_clicks += 1
                # Adding debouncing
                if self.num_clicks == 3:
                    pyautogui.click()
            # 4 = Extension 
            elif input_class == 4:
                pyautogui.moveRel(self.VEL * multiplier, 0)
            # 5 = Flexion
            elif input_class == 5:
                pyautogui.moveRel(-self.VEL * multiplier, 0)

            # Reset left click count if another class is recognized
            if input_class != 2 and self.num_clicks != 0:
                self.num_clicks = 0