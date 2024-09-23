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



FfDistance = 50
Dspeed = -180
GENERAL_TURN = 18
GYRO_THRESHOLD = 20
grip_is_open = True
GRIP_WAIT_TIME = 2500

DBase=DriveBase(Motor_R, Motor_L, wheel_diameter=56, axle_track=100)





def Gripper_debug(grip_is_open):
    if grip_is_open:
    
        Motor_Grip.run(300)
        wait(GRIP_WAIT_TIME)
        grip_is_open = False
    else:
            Motor_Grip.run(-300)
            wait(GRIP_WAIT_TIME)
            grip_is_open = True
    return grip_is_open

grip_is_open = Gripper_debug(grip_is_open)

grip_is_open = Gripper_debug(grip_is_open)

# def Fflaske():
#     while True:
#         print("entered")
#         print(Ucensor.distance())
#         if Ucensor.distance() <= FfDistance:
#             Motor_Grip.run(200)
#             wait(4000)
#             Motor_Grip.stop()
#             DBase.straight(120)
#             Motor_Grip.run(-200)
#             wait(4000)
#             Motor_Grip.stop()
#         if Ucensor.distance() > FfDistance:
#             print("exited")
#             break
#     return





