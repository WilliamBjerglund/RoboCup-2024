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


FfDistance = 35 
Dspeed = -150
GENERAL_TURN = 20
GYRO_THRESHOLD = 20

Gyrosensor.reset_angle(0)

DBase=DriveBase(Motor_R, Motor_L, wheel_diameter=56, axle_track=100)

def calibrate():
    """
    Calibrates the value to determine where the edge of the line begins, to correct path
    Returns target value of the edge as an int
    """
    EV3.speaker.beep()
    print("Starting calibration")
    gyro_early = Gyrosensor.angle()
    wait(1000)
    target_val = Colorsensor.reflection()
    
    EV3.speaker.beep()
    print("Gyro driftet by: " + str(abs(gyro_early - Gyrosensor.angle())))
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
            #Gyrosensor.reset_angle(0)
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
            DBase.drive(Dspeed, -sign * (GENERAL_TURN + local_error)) # right
        if current_val > target_val:
            DBase.drive(Dspeed, sign * (GENERAL_TURN + local_error)) # left
    Gyrosensor.reset_angle(0)
            
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
            DBase.straight(250)
            Motor_Grip.run(-200)
            wait(4000)
            Motor_Grip.stop()
            return
        else:
            DBase.straight(15)
    return

def lineup(angle:int):
    correction = 0
    distancethreshold = 500
    while True:
#        print(Gyrosensor.angle())
#        if Gyrosensor.angle()==angle:
#            return
#        elif Gyrosensor.angle() < angle:
#            DBase.turn(1)
#        else:
#            DBase.turn(-1)
        print('The correction value is: ' + str(correction) + ' and the ultrasensor is: ' + str(Ucensor.distance()))
        if Ucensor.distance() < distancethreshold:
            if correction >= 10:
                DBase.turn(-8)
                return
                
        else:
            DBase.turn(-1)
        if Ucensor.distance() < distancethreshold:
            correction += 1
        else:
            correction = 0
        wait(5)



# Setup
target_val = calibrate()

# First challagne
if True:
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
if True:
    follow_line(-1, 'right')
    wait(300)

# Grab Bottle 1
if True:
    DBase.straight(-300)
    lineup(-90)
    DBase.straight(250)

    Fflaske()

    DBase.straight(-500)
    DBase.turn(120)

# The vippen challenge
follow_line(-1)

print(Gyrosensor.angle())




