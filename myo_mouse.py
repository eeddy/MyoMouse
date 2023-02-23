from enum import Enum
import socket
import math
import datetime

class MyoMouse:
    def __init__(self, velocity=15, proportional_control=True):
        # Set up default values 
        self.VEL = velocity
        self.proportional_control = proportional_control

        # Set the mouse state 
        self.mouse_active = False
        self.action = Action.REST
        self.previous_action = Action.REST
        # The number of subsequent decisions that agree with eachother
        self.steady_state = 0
        self.button_debounce = datetime.datetime.now()

        # Socket for reading EMG
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
        self.sock.bind(('127.0.0.1', 12346))
        while True:
            self.read_data()

    def read_data(self):
        # Read data from the specific socket
        data, _ = self.sock.recvfrom(1024)
        data = str(data.decode("utf-8"))
        if data:
            input_class = float(data.split(' ')[0])
            multiplier = 1
            if self.proportional_control:
                multiplier = float(data.split(' ')[1])
                multiplier = multiplier * math.exp(multiplier)
            
            # Maintaining a steady-state buffer for debouncing
            self.steady_state += 1
            if self.action != Action(input_class) and self.action != Action.REJECT:
                self.steady_state = 0
            # Update the action
            self.previous_action = self.action
            self.action = Action(input_class)
                        
            self.deal_with_state(multiplier)
    
    def deal_with_state(self, multiplier):
        import pyautogui # Was causing issues with TKinter

        # Turn on/off mouse 
        if self.action == Action.FINGER_GUN:
            # Check for 3 consecutive actions with a 1 second debounce
            if self.steady_state >= 3 and (datetime.datetime.now() - self.button_debounce).total_seconds() > 2:
                self.mouse_active = not self.mouse_active
                self.steady_state = 0
                self.button_debounce = datetime.datetime.now() 
                print("Mouse Active: " + str(self.mouse_active))

        if self.state == self.mouse_active:
            if self.action == Action.FINGER_TAP:
                # Button Click
                if self.steady_state >= 3 and (datetime.datetime.now() - self.button_debounce).total_seconds() > 0.5:
                    self.steady_state = 0
                    self.button_debounce = datetime.datetime.now() 
                    pyautogui.click()
            
            # Deal with continuous inputs 
            if self.action == Action.HAND_CLOSE:
                # Move Down
                pyautogui.moveRel(0, self.VEL * multiplier)
            elif self.action == Action.HAND_OPEN:
                # Move Up
                pyautogui.moveRel(0, -self.VEL * multiplier)
            elif self.action == Action.EXTENSION:
                # Move Right
                pyautogui.moveRel(self.VEL * multiplier, 0)
            elif self.action == Action.FLEXION:
                # Move Left
                pyautogui.moveRel(-self.VEL * multiplier, 0)


class Action(Enum):
    REJECT = -1
    FINGER_GUN = 0
    HAND_CLOSE = 1
    HAND_OPEN = 2
    FINGER_TAP = 3 
    REST = 4
    EXTENSION = 5
    FLEXION = 6 
    