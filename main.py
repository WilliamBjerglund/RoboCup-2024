#!/usr/bin/env pybricks-micropython
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import (Motor, TouchSensor, ColorSensor,
                                 InfraredSensor, UltrasonicSensor, GyroSensor)
from pybricks.parameters import Port, Stop, Direction, Button, Color
from pybricks.tools import wait, StopWatch, DataLog
from pybricks.robotics import DriveBase
from pybricks.media.ev3dev import SoundFile, ImageFile

Motor_R = Motor(Port.A)
Motor_L = Motor(Port.D)
EV3 = EV3Brick()
Colorsensor = ColorSensor(Port.S1)



Dspeed = -200
GENERAL_TURN = 20

DBase=DriveBase(Motor_R, Motor_L, wheel_diameter=70, axle_track=195)

def calibrate():
    EV3.speaker.beep()
    print("Starting calibration")
    wait(1000)
    target_val = Colorsensor.reflection()
    EV3.speaker.beep()
    print("Calibration: ", target_val)
    return target_val
    
def follow_line():
    while True:
        current_val = Colorsensor.reflection()
        if target_val > current_val:
            local_error = (target_val - current_val)/2
        else:
            local_error = (current_val - target_val)/2
            
        if current_val < target_val:
            DBase.drive(Dspeed, direction * GENERAL_TURN+local_error)
        if current_val > target_val:
            DBase.drive(Dspeed, -(direction * GENERAL_TURN+local_error))
        print(current_val) #debug
        if current_val < 15:
            break



    
target_val = calibrate()
follow_line()
while Colorsensor.reflection() > target_val:
    DBase.drive(Dspeed, 30)
follow_line()

