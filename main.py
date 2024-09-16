#!/usr/bin/env pybricks-micropython
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import (Motor, TouchSensor, ColorSensor,
                                 InfraredSensor, UltrasonicSensor, GyroSensor)
from pybricks.parameters import Port, Stop, Direction, Button, Color
from pybricks.tools import wait, StopWatch, DataLog
from pybricks.robotics import DriveBase
from pybricks.media.ev3dev import SoundFile, ImageFile

Motor_R = Motor(Port.B)
Motor_L = Motor(Port.C)
Motor_Grip = Motor(Port.D)
EV3 = EV3Brick()
Colorsensor = ColorSensor(Port.S1)
Gyrosensor = GyroSensor(Port.S4)
Ucensor = UltrasonicSensor(Port.S3)


FfDistance = 100
Dspeed = -180
GENERAL_TURN = 18
GYRO_THRESHOLD = 20

DBase=DriveBase(Motor_R, Motor_L, wheel_diameter=56, axle_track=100)

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
    
def follow_line(sign=1,turn_direction='straight'):
    """ 
    Follows line edge
    Input defines which edge of the line to follow, where 1 (Default) is the right side and -1 is left side
    Returns void
    """
   # if abs(sign) == 1:
    #    raise Exception(f"follow_line got to big input value: '{sign}', limit it to '1' or '-1'")
    
    speed_multiplier = 1.15
    local_turn_rate = 45
    local_drive_speed = Dspeed
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
            #print("It hit me")
            #local_turn_rate = 45
            local_drive_speed *= speed_multiplier
        else:
            #local_turn_rate = GENERAL_TURN
            local_drive_speed = Dspeed
            
        # Determine the amount of correction to stay on path
        if target_val > current_val:
            local_error = (target_val - current_val)/2
        else:
            local_error = (current_val - target_val)/2
            
        # Apply correction in drive module and which edge of the line to follow
        if current_val < target_val:
            if turn_direction == 'right' and abs(gyro_angle) > GYRO_THRESHOLD:
                print("number 1")
                DBase.drive(Dspeed * speed_multiplier, -sign * (local_turn_rate + local_error)) # right
            else:
                print("number 2")
                DBase.drive(Dspeed, -sign * (GENERAL_TURN + local_error)) # right
        if current_val > target_val:
            if turn_direction == 'left' and abs(gyro_angle) > GYRO_THRESHOLD:
                print("number 3")
                DBase.drive(Dspeed * speed_multiplier, sign * (local_turn_rate + local_error)) # left
            else:
                print("number 4")
                DBase.drive(Dspeed, sign * (GENERAL_TURN + local_error)) # left
            
        # Debug
        #print(current_val)
        #print(gyro_angle)
    return

def Fflaske():
    while True:
        print("entered")
        print(Ucensor.distance())
        if Ucensor.distance() <= FfDistance:
            Motor_Grip.run(200)
            wait(4000)
            Motor_Grip.stop()
            DBase.straight(120)
            Motor_Grip.run(-200)
            wait(4000)
            Motor_Grip.stop()
        if Ucensor.distance() > FfDistance:
            print("exited")
            break
    return


# Setup
target_val = calibrate()

# First challagne
if False:
    follow_line(-1)
    wait(300)
    DBase.straight(-10)
    DBase.turn(30)
    while Colorsensor.reflection() > 50: # Første sving
        DBase.drive(Dspeed, 0)
    follow_line(1)
    wait(300)
    DBase.straight(-10)
    DBase.turn(-30)
    while Colorsensor.reflection() > 50: # Andet sving
        DBase.drive(Dspeed, 0)

# First turn 
follow_line(-1, 'right')
wait(300)

# Grab Bottle
DBase.straight(-255)
DBase.turn(-120)
DBase.straight(360)

Fflaske()


DBase.straight(-500)
