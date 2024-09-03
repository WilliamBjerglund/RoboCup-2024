#!/usr/bin/env pybricks-micropython
#import packages
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor
from pybricks.parameters import Port, Direction
from pybricks.robotics import DriveBase

# Initialize the EV3 Brick & everything else.
ev3 = EV3Brick()

# Initialize motors (left motor set to run counterclockwise)
left_motor = Motor(Port.B)
right_motor = Motor(Port.A)
gripper_motor = Motor(Port.D)  # Make sure to use a different port for the arm motor

# Initialize the drive base
robot = DriveBase(left_motor, right_motor, wheel_diameter=55.5, axle_track=104)

# Go forward and backwards for one meter.
robot.straight(1000)
ev3.speaker.beep()

robot.straight(-1000)
ev3.speaker.beep()

# Turn clockwise by 360 degrees and back again.
robot.turn(360)
ev3.speaker.beep()

robot.turn(-360)
ev3.speaker.beep()

# Operate the gripper motor
gripper_motor.run_target(75, 300)  # Adjust speed and angle as necessary
gripper_motor.run_target(75, -300)
ev3.speaker.beep()  # Beep to confirm completion
