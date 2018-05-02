#!/usr/bin/python
# Import the device reading library
from evdev import InputDevice, categorize, ecodes, KeyEvent, list_devices
# Import the Sleep library
from time import sleep
# Import Adafruit Motor HAT Library
from Adafruit_MotorHAT import Adafruit_MotorHAT, Adafruit_DCMotor
# Import additional libraries that support MotorHAT
import time
import atexit
# Import library that allows parallel processing
from multiprocessing import Process, Queue
import os
# Create Camera Object
##frontCamera = PiCamera()
# recommended for auto-disabling motors on shutdown!
def turnOffMotors():
  mh.getMotor(1).run(Adafruit_MotorHAT.RELEASE)
  mh.getMotor(2).run(Adafruit_MotorHAT.RELEASE)
  mh.getMotor(3).run(Adafruit_MotorHAT.RELEASE)
  mh.getMotor(4).run(Adafruit_MotorHAT.RELEASE)


# Complete this function so:
# 1. values in the range 1 to 32768 make the motor spin forward faster and faster.
# 2. values in the range -1 to -32768 make the motor spin backward faster and faster.
# 3. any value equal to 0 makes the motor BRAKE.
# 4. any values less than -32768 and greater than 32768 are rejected.
def runMotor(motor, speed):
  """ motor - the motor object to control.
      speed - a number from -32768 (reverse) to 32768 (forward) """
  if speed < -32768 or speed > 32768:
    pass
  elif speed < 0:
    motor.setSpeed(int(speed/-128.0))
    motor.run(Adafruit_MotorHAT.FORWARD)
  elif speed > 0:
    motor.setSpeed(int(speed/128.0))
    motor.run(Adafruit_MotorHAT.BACKWARD)
  else:
    motor.setSpeed(0)
    motor.run(Adafruit_MotorHAT.BRAKE)  

# Get the name of the Logitech Device
def getInputDeviceByName(name):
  devices = [InputDevice(fn) for fn in list_devices()]
  for device in devices:
    if device.name == name:
      return InputDevice(device.fn)
  return None


# create a default MotorHAT object, no changes to I2C address or frequency
mh = Adafruit_MotorHAT(addr=0x60)
lmotor = mh.getMotor(1)
rmotor = mh.getMotor(2)

# Import our gamepad.
gamepad = getInputDeviceByName('Logitech Gamepad F710')

# Process the Queue of Motor Speeds
def motorProcess(q):
  while True:
    msg = None
    # Get the most recent message
    while not q.empty():
      msg = q.get()
    # As long as the motor isn't None.
    if msg == None:
      # If there is no message, continue
      continue
    elif msg[0]==None and msg[1]==None:
      # Quit this function if the message is [None,None]
      # This is the indicator to stop this function
      return
    else:
      runMotor(lmotor,msg[0])
      runMotor(rmotor,msg[1])

# Process the GamePad
def gamepadProcess():
  # Create variables to keep track of the joystick state.
  joyLR = 0
  joyUD = 0
  # Create Variable to see if Camera is Recording
  Recording = False
  # Loop over the gamepad's inputs, reading it.
  for event in gamepad.read_loop():
    if event.type == ecodes.EV_KEY:
      keyevent = categorize(event)
      if keyevent.keystate == KeyEvent.key_down:
        print(keyevent.keycode)
        # Key Detection
        if 'BTN_A' in keyevent.keycode:
          # Do Something when A Button Press
          pass
        elif 'BTN_START' in keyevent.keycode:
          # Do something here when the A button is pressed
          pass
    elif event.type == ecodes.EV_ABS:
      if event.code == 0:
        print('PAD_LR '+str(event.value))
      elif event.code == 1:
        print('PAD_UD '+str(event.value))
      elif event.code == 2:
        print('TRIG_L '+str(event.value))
      elif event.code == 3:
        print('JOY_LR '+str(event.value))
        joyLR = event.value
        # Send a message to the motorProcess when the joystick moves.
        q.put([joyUD-joyLR,joyUD+joyLR])
      elif event.code == 4:
        print('JOY_UD '+str(event.value))
        joyUD = event.value
        # Send a message to the motorProcess when the joystick moves.
        q.put([joyUD-joyLR,joyUD+joyLR])
      elif event.code == 5:
        print('TRIG_R '+str(event.value))
      elif event.code == 16:
        print('HAT_LR '+str(event.value))
      elif event.code == 17:
        print('HAT_UD '+str(event.value))
      else:
        pass


##########################################
## MAIN CODE
##########################################

# Create a queue for communication between the GamePad and the motorProcess. 
q = Queue()
# Create a Process that runs the motors, give it the queue.
p = Process(target=motorProcess, args=(q,))
# Start the motorPorcess
p.start()

# Ensure the motorProcess joins and the motors turn off.
def exitFunction():
  # Send a sign to the motorProcess to end
  q.put([None,None])
  # Wait for the motor process to end
  p.join()
  # Kill all the motors
  turnOffMotors()
# Register the exitFunction() to be called when this Python script ends.
atexit.register(exitFunction)

# Call the Gamepad Process function which runs forever (until Ctrl+C is entered)
gamepadProcess()


