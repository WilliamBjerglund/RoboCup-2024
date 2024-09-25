#!/usr/bin/env pybricks-micropython
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import (Motor, TouchSensor, ColorSensor,
                                 InfraredSensor, UltrasonicSensor, GyroSensor)
from pybricks.parameters import Port, Stop, Direction, Button, Color
from pybricks.tools import wait, StopWatch, DataLog
from pybricks.robotics import DriveBase
from pybricks.media.ev3dev import SoundFile, ImageFile

# Initiation of motors and sensors
Motor_R = Motor(Port.B)
Motor_L = Motor(Port.C)
Motor_Grip = Motor(Port.D)
Colorsensor = ColorSensor(Port.S1)
Gyrosensor = GyroSensor(Port.S4)
Ucensor = UltrasonicSensor(Port.S3)

# Initiation of various global variables 
DRIVE_SPEED = -200
GENERAL_TURN = 10
GYRO_THRESHOLD = 20
GYRO_OFFSET_FACTOR = 0.0005
gyro_offset = 0
robot_body_angle = 0
my_stop_watch = StopWatch()
timestamp = my_stop_watch.time()

# Initiation of functional classes
EV3 = EV3Brick()
DBase = DriveBase(Motor_R, Motor_L, wheel_diameter = 56, axle_track = 100)

# Creation and allocation of funtions
def calibrate():
    """
    Calibrates the value, that determines where the edge of the line begins, to follow the correct path
    And checks the gyro for drift to auto correct
    Returns target value of the edge as an int
    """
    EV3.speaker.beep()
    print("Starting calibration")
    gyro_early = Gyrosensor.angle()
    
    wait(1000)
    
    target_val = Colorsensor.reflection()
    gyro_drift = abs(gyro_early - Gyrosensor.angle())
    
    EV3.speaker.beep()
    print("Gyro drift: " + str(gyro_drift))
    print("Color sensor edge calibration value: ", target_val)
    
    # if gyro is not stable, try and fix it first, slightly taken from: https://pybricks.com/ev3-micropython/examples/gyro_boy.html
    if False:
        GYRO_CALIBRATION_LOOP_COUNT = 200
        global gyro_offset
        while True:
            gyro_minimum_rate, gyro_maximum_rate = 440, -440
            gyro_sum = 0
            for _ in range(GYRO_CALIBRATION_LOOP_COUNT):
                gyro_sensor_value = Gyrosensor.speed()
                gyro_sum += gyro_sensor_value
                if gyro_sensor_value > gyro_maximum_rate:
                    gyro_maximum_rate = gyro_sensor_value
                if gyro_sensor_value < gyro_minimum_rate:
                    gyro_minimum_rate = gyro_sensor_value
                wait(5)
            if gyro_maximum_rate - gyro_minimum_rate < 2:
                break
        gyro_offset = gyro_sum / GYRO_CALIBRATION_LOOP_COUNT
    return target_val

def get_angle():
    """
    Very experimental, if it doesnt work, jsut kill it 
    """
    global gyro_offset, robot_body_angle, timestamp
    timespan = timestamp - my_stop_watch.time()
    timestamp = my_stop_watch.time()
    gyro_sensor_value = Gyrosensor.speed()
    gyro_offset *= (1 - GYRO_OFFSET_FACTOR)
    gyro_offset += GYRO_OFFSET_FACTOR * gyro_sensor_value
    robot_body_rate = gyro_sensor_value - gyro_offset
    robot_body_angle += robot_body_rate * timespan
    return robot_body_angle

def follow_line(sign=1, time=0):
    """ 
    Follows the given or default line edge
    Input defines which edge of the line to follow, where 1 (Default) is the right side and -1 is left side
    Returns void
    """
    # Sanity check to not give wildly to large numbers and ensure good code
    if abs(sign) != 1:
        raise Exception("follow_line got to big input value: " + str(sign) + ", limit is between '1' or '-1'")
    
    if time != 0:
        stop_timer = StopWatch()

    correction_counter = 0
    correction_counter_max = 10
    correction_multiplier = 3
    while True:
        # Get new sensor data
        current_val = Colorsensor.reflection()

        # Determine if black line has been reached, and thus next stage
        if current_val < 30:
            DBase.stop()
            break
        
        # correction counter used to drive faster in turn, currently it is effectively not limited, probably should have a limit, but where?
        if current_val < target_val:
            if correction_counter < correction_counter_max:
                correction_counter += 1
        else:
            correction_counter = 0

        # Determine the amount of correction to stay on path, (probably doesn't do much tbh)
        if target_val > current_val:
            local_error = (target_val - current_val)/2
        else:
            local_error = (current_val - target_val)/2

        # verify if this is not equivlant to above   
        #local_error = abs(target_val - current_val)/2

        # Debg statement
        #print("Corection counter is: " + str(correction_counter))

        # Apply correction in drive module and which edge of the line to follow
        turn_rate = GENERAL_TURN + local_error + correction_counter * correction_multiplier
        if current_val < target_val:
            DBase.drive(DRIVE_SPEED, -sign * turn_rate) # right
        else:
            DBase.drive(DRIVE_SPEED, sign * turn_rate) # left

        if time != 0:
            # print("Time left in follow_line" + str(time - stop_timer.time()))
            if stop_timer.time() > time:
                return

    return

def move_bottle(drive_for:int): # Renamed, sorry patrik, it had a shit name
    """
    Will go straight until, presumably, a bottle is within threshold, after which it will lift up the bottle and drive given distance
    Input the driving distance after it has grabbed the bottle
    """
    distance_threshold = 35
    counter = 0
    last_reading = 0
    slack_allowance = 1

    while True:
        current_reading = Ucensor.distance() 
        print("The distance to presumed bottle: " + str(Ucensor.distance()))
        if  current_reading <= distance_threshold or counter >= 5:
            Motor_Grip.run(200)
            wait(4000)
            Motor_Grip.stop()
            DBase.straight(drive_for)
            Motor_Grip.run(-200)
            wait(4000)
            Motor_Grip.stop()
            return
        else:
            DBase.straight(15)

            # Experimental, it has been very inconsistent with sensing the bottle, this should get a better feel for it
            if current_reading <= last_reading + slack_allowance and current_reading >= last_reading - slack_allowance:
                counter += 1 
            else:
                counter == 0

        last_reading = current_reading

def lineup(angle:int = 0):
    """
    Depending on version it will attempt to lineup with a bottle or with a angle
    """
    # This is the ultrasonic scanner version
    if True:
        correction = 0
        distancethreshold = 350
        while True:
            reading = Ucensor.distance()
            print('The correction value is: ' + str(correction) + ' and the ultrasensor is: ' + str(reading))
            if reading < distancethreshold:
                if correction >= 20:
                    DBase.turn(25)
                    return
                    
            else:
                DBase.turn(1)
            
            if reading < distancethreshold:
                correction += 1
            else:
                correction = 0
            wait(10)
            

# Setup
target_val = calibrate()

# First challagne
# Are the wait statements neccesary, i dont feel like they are but idk
# The if statements with hard coded bools in them may seem unnessecary, because they are, but they make it easy to change where the robot can be placed to start, so that it doesnt have to run the whole route to test one thing
if True:
    follow_line(-1)
    wait(300)
    DBase.straight(-10)
    DBase.turn(30)

    # First freespace
    while Colorsensor.reflection() > 50: 
        DBase.drive(DRIVE_SPEED, 0)
    
    follow_line(1)
    wait(300)
    DBase.straight(-10)
    DBase.turn(-30)
    
    # Second freespace
    while Colorsensor.reflection() > 50: 
        DBase.drive(DRIVE_SPEED, 0)

# First turn 
if True:
    follow_line(-1)
    wait(300)

# Grab Bottle and move over line
if True:
    DBase.straight(-250) #worked val 
    DBase.turn(-140)
    DBase.straight(150)
    lineup()
#    DBase.straight(250)

    move_bottle(250)

    DBase.straight(-500)
    DBase.turn(90)

# The vippen challenge
if True:
    follow_line(-1)
    DBase.straight(-280)
    DBase.turn(-95)

    print("step 1, black line")
    follow_line(-1)
    wait(300)
    print("step 3, hitting ramp")
    DBase.straight(-100)
    print("step 4, on ramp")
    follow_line(-1)
    wait(200)
    print("step 5, off ramp")
    DBase.straight(-560)
    DBase.turn(115)

    follow_line(-1, time=12000)
    DBase.turn(190)
    follow_line(1)
    wait(300)


# Barcode challenge
if True:
    DBase.turn(-38)
    DBase.straight(-300)

    stamp = GENERAL_TURN
    GENERAL_TURN = 10
    follow_line()
    wait(300)
    GENERAL_TURN = stamp


    # Bulls eye bottle 


    follow_line()
    #Rundt om flaske 1
    DBase.turn(60)
    follow_line(-1)


# Black wall
if True:
    DBase.turn(-150)
    counts = 0
    while True:
        if Ucensor.distance() <100:
            counts+=1 
        if counts>10:
            break
        DBase.straight(10)
    DBase.turn(-45)
