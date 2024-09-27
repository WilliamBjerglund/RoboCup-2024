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
Ucensor = UltrasonicSensor(Port.S3)

# Initiation of various global variables 
DRIVE_SPEED = -200
GENERAL_TURN = 10

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
    
    wait(1000)
    
    target_val = Colorsensor.reflection()
    
    EV3.speaker.beep()
    print("Color sensor edge calibration value: ", target_val)    
    return target_val

def follow_line(sign=1, time=0, precision=0):
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
        drive_speed = DRIVE_SPEED

        if precision != 0:
            turn_rate = local_error #* 0.8 
            drive_speed = -50

        if current_val < target_val:
            DBase.drive(drive_speed, -sign * turn_rate) # right
        else:
            DBase.drive(drive_speed, sign * turn_rate) # left

        if time != 0:
            # print("Time left in follow_line" + str(time - stop_timer.time()))
            if stop_timer.time() > time:
                return

    return

def move_bottle(drive_for:int, bullseye=False): # Renamed, sorry patrik, it had a shit name
    """
    Will go straight until, presumably, a bottle is within threshold, after which it will lift up the bottle and drive given distance
    Input the driving distance after it has grabbed the bottle
    """
    distance_threshold = 35
    counter = 0
    last_reading = 0
    slack_allowance = 1
    counter_clocks = 0

    while True:
        current_reading = Ucensor.distance() 
        print("The distance to presumed bottle: " + str(Ucensor.distance()))
        #if  current_reading <= distance_threshold or counter >= 3 or counter_clocks >= 5:
        if True: # it has ben changed as the new lineup is better, it therefore is hard coded to just pickup, hence it doesnt need to creep up
            DBase.straight(7)
            Motor_Grip.run(200)
            wait(4000)
            Motor_Grip.stop()
            DBase.straight(drive_for)

            if bullseye:
                DBase.turn(-10)
            
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
        counter_clocks += 1
            
def scanning_lineup():
    """
    Will lineup with a given object infront of its ultrasonic sensor, does not work if there isn't a relatively tall object infront
    """
    # Various variables
    count = 0
    count_best_not_improved = 0
    count_out_of_touch = 0
    last_reading = 0
    best = (count, 3000) # the first is index being rotation, the second is the value

    while True:
        current_reading = Ucensor.distance()

        # Evaluates best angle 
        if current_reading <= best[1]:
            best = (count, current_reading)

        # getting the count of equivalent readings for estimating center of readings        
        if current_reading == last_reading and best[1] == current_reading:
            count_best_not_improved += 1

        # Determining if the readings are too high and ready to exit
        if current_reading > best[1] * 1.1:
            count_out_of_touch += 1
            if count_out_of_touch > 10:
                break
        #print("Distance reading " + str(current_reading) + " Count " + str(count))
        
        # Incrementable rotation and updates to variables
        DBase.turn(1)
        last_reading = current_reading
        count += 1

    # The angle to turn back to allign with the bottle
    turn_back = (count - best[0] + count_best_not_improved/2)
    DBase.turn(-turn_back)
    #print("Total turned " + str(count) + " Determined turn back " + str(turn_back) + " Best reading " + str(best))
    return

def printnice(main='', secondary='', do_time=False):
    """
    Not particularly neccesary, but it is nice i suppose
    """
    if do_time:
        print("Time progress: " + str((start_time_watch.time() - start_time)/60000) + "min")
    if main != '':
        print('-'*5 + main + '-'*5)
    if secondary != '':
        print('-' + secondary + '-')        
    print()
    return

# Setup
target_val = calibrate()

current_settings = DBase.settings()
DBase.settings(current_settings[0] + 50, current_settings[1], current_settings[2], current_settings[3])

start_time_watch = StopWatch()
start_time = start_time_watch.time()

# First challagne
# Are the wait statements neccesary, i dont feel like they are but idk
# The if statements with hard coded bools in them may seem unnessecary, because they are, but they make it easy to change where the robot can be placed to start, so that it doesnt have to run the whole route to test one thing
if True:
    printnice("Lane Switch")
    follow_line(-1)
    wait(300)
    DBase.straight(-10)
    DBase.turn(40)

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


if True:
# First turn 
    printnice("First Turn", do_time=True)
    follow_line(-1)
    wait(300)

# Grab Bottle and move over line
    printnice("Grab Bottle", do_time=True)
    print("-Preparing for lineup")
    DBase.straight(-250) 
    DBase.turn(-105)
    DBase.straight(150)
    DBase.turn(-60)

    print("-Acutally lining up")
    scanning_lineup()
    DBase.straight(235)

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

# Barcode challenge
if True:
    follow_line(1)
    wait(300)

    DBase.turn(-38)
    DBase.straight(-330)
    DBase.turn(32)

    # Bulls eye bottle 
if True:
    follow_line(1)

    DBase.straight(-300)
    DBase.turn(-100)
    follow_line(-1, precision=199)

    DBase.straight(-800)
    DBase.turn(205) # bigger goes to the right
    DBase.straight(317)
    move_bottle(-570, True)

    DBase.drive(-200, 50)
    wait(1000)
    while Colorsensor.reflection() > 50:
        DBase.drive(-200, 20)
    
    DBase.straight(-150)
    DBase.turn(-90)
    follow_line(1)

    wait(300)
    follow_line()

    #Rundt om flaske 1
    DBase.turn(60)
    follow_line(-1, time=2700)
    wait(300)
    DBase.turn(-20)

    DBase.turn(60)
    DBase.drive(200, -30)
    while Colorsensor.reflection() > 50:
        print()

    follow_line(-1, time=8500)

# Black wall v2
if True:
    follow_line(-1, precision=1)
    DBase.straight(-550)
    DBase.turn(-55)
    
    DBase.drive(-200, 45)
    wait(2200)
    DBase.stop()

    DBase.straight(-250)
    DBase.turn(-25)

if True:
    #Rundt om flaske 2
    follow_line(-1)
    DBase.straight(-100)
    DBase.turn(-60)
    DBase.straight(-150)

    # Turn
    DBase.drive(-200, 30)
    wait(2400)
    DBase.stop()
    wait(300)
    
    DBase.turn(50)
    DBase.straight(-160)
    DBase.turn(-55)
    follow_line(1)

    #Landings bane
    DBase.straight(-200)
    follow_line(1, time=7900)

    DBase.turn(-100)
    DBase.straight(-100)
    DBase.turn(100)


print("It took " + str((start_time_watch.time() - start_time)/60000) + "min")