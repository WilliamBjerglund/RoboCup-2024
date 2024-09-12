#!/usr/bin/env pybricks-micropython
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor, ColorSensor, UltrasonicSensor
from pybricks.parameters import Port, Color, Direction
from pybricks.robotics import DriveBase
from pybricks.tools import wait

def Follow_line():
    while True:
        ColorData = Colorsensor.reflection()
        print(Threshhold2-Colorsensor.reflection()+5)
        sign = -1
        if Threshhold2-ColorData+5 < 0:
            for i in range(0,180,5):
                for j in range(i):
                    DBase.turn(sign)
                    print(Threshhold2-Colorsensor.reflection()+5)
                    if Threshhold2-Colorsensor.reflection()+5 > 0:
                        DBase.turn(3*sign)
                        break
                if Threshhold2-Colorsensor.reflection()+5 > 0:
                    break
                if sign >=0:
                    sign=-1
                else:
                    sign=1
                if i == 175:
                    DBase.turn(0,-80)
        if ColorData-Threshhold1 < 0:
            break

        DBase.drive(Dspeed,0)
        wait(10)
    return
def Find_line():
    DBase.drive(Dspeed,0)
    while True:
        if Threshhold2-Colorsensor.reflection()+5 >0:
            break
    DBase.stop()
    return

Motor_R = Motor(Port.A)
Motor_L = Motor(Port.D)
EV3 = EV3Brick()
Colorsensor = ColorSensor(Port.S1)



Black = 5
White = 62
Grey = 37
Threshhold1 = (Black+Grey)/2
Threshhold2 = (Grey+White)/2
Dspeed = -150
DBase=DriveBase(Motor_R, Motor_L, wheel_diameter=70, axle_track=195)

# første sektion af banen (Brudt streg)
Follow_line()


DBase.turn(-30)
Find_line()
wait(100)
# anden sektion af banen (Brudt streg)
Follow_line()

DBase.turn(30)
Find_line()
wait(100)

# følg banen hen til flasken (3 sektion curve)
Follow_line()


    





