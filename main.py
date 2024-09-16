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
Gyrosensor = GyroSensor(Port. S4)



Dspeed = -100
GENERAL_TURN = 15
GYRO_THRESHOLD = 30

DBase=DriveBase(Motor_R, Motor_L, wheel_diameter=70, axle_track=195)

def calibrate():
    """
    Calibrates the value to determine where the edge of the line begins, to correct path
    Returns target value of the edge as an int
    """
    EV3.speaker.beep()
    print("Starting calibration")
    wait(1000)
    target_val = Colorsensor.reflection()
    EV3.speaker.beep()
    print("Calibration: ", target_val)
    return target_val
    
def follow_line(sign=1):
    """ 
    Follows line edge
    Input defines which edge of the line to follow, where 1 (Default) is the right side and -1 is left side
    Returns void
    """
   # if abs(sign) == 1:
    #    raise Exception(f"follow_line got to big input value: '{sign}', limit it to '1' or '-1'")
    
    local_turn_rate = GENERAL_TURN
    while True:
        # Get new sensor data
        current_val = Colorsensor.reflection()
        gyro_angle = Gyrosensor.angle()
        # Determine if black line has been reached, and thus next stage
        if current_val < 30:
            Gyrosensor.reset_angle(0)
            DBase.stop()
            break
        
        # Determine if in a turn and increase turn rate to drive faster without failing
        if abs(gyro_angle) > GYRO_THRESHOLD:
            local_turn_rate = 30
        else:
            local_turn_rate = GENERAL_TURN
            
        # Determine the amount of correction to stay on path
        if target_val > current_val:
            local_error = (target_val - current_val)/2
        else:
            local_error = (current_val - target_val)/2
            
        # Apply correction in drive module and which edge of the line to follow
        if current_val < target_val:
            DBase.drive(Dspeed, sign * local_turn_rate + local_error)
        if current_val > target_val:
            DBase.drive(Dspeed, -sign * (local_turn_rate + local_error))
            
        # Debug
        #print(current_val)
        print(gyro_angle)
    return



# Setup
target_val = calibrate()

# First challagne
follow_line(-1)
wait(300)
DBase.turn(-30)
while Colorsensor.reflection() > 50: # Første sving
    DBase.drive(Dspeed, 0)
follow_line(1)
wait(300)
DBase.turn(30)
while Colorsensor.reflection() > 50: # Andet sving
    DBase.drive(Dspeed, 0)
follow_line(-1)
wait(300)
