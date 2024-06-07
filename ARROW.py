#!/usr/bin/env micropython

from ev3dev2.motor import OUTPUT_A, OUTPUT_B, OUTPUT_C, OUTPUT_D, LargeMotor, MediumMotor
from ev3dev2.sensor import INPUT_1, INPUT_2
from ev3dev2.sensor.lego import InfraredSensor, GyroSensor
from ev3dev2.led import Leds
from ev3dev2.button import Button
from time import sleep
from threading import Thread
import os
os.system('setfont Lat15-TerminusBold14')

leds = Leds()
btn = Button()

gyro = GyroSensor(INPUT_2)
irMid = InfraredSensor(INPUT_1)

mRight = LargeMotor(OUTPUT_A)
mMid = LargeMotor(OUTPUT_B)
mLeft = LargeMotor(OUTPUT_C)
mRamp = MediumMotor(OUTPUT_D)

distMid = 0
direction = 1  # -1 -> LEFT | 1 -> RIGHT
angle = 0

MAX_DIST = 97
counter = 6
speed = 45


### MISS CHECK ###

def check_if_missed():
    sleep(0.1)
    while True:
        global direction
        global distMid
        global counter

        if distMid < MAX_DIST and counter <= 0:
            slow.start()
            direction = -direction
            while distMid < MAX_DIST:
                sleep(0.000001)

check = Thread(target=check_if_missed)

### SLOW DOWN ###


def slow_down(strength, toggle):
    global speed

    if toggle:
        toggle = False
        speed -= strength
        for i in range(strength):
            speed = speed + 1
            sleep(0.07)

        toggle = True

slow = Thread(target=slow_down, args=(speed / 2, True))

### RAMP ###

def when_stuck():
    sleep(0.3)

    while True:
        global distMid
        sleep(0.6)
        if abs(gyro.rate) < 5 and distMid > MAX_DIST:
            mRamp.on_for_degrees(100, -15, brake = True)
            sleep(0.05)
            mRamp.on_for_degrees(100, 15, brake = False)

stuck = Thread(target=when_stuck)

def ramp():
    mRamp.on_for_degrees(100, 90, brake=True)
    mRamp.off(brake=False)


ramp_down = Thread(target=ramp)

### GOTO ANGLE ###

def goto(angle):
    global distMid
    global counter

    if angle < 0 and angle != -1: # right
        ramp_down.start()
        direction = -1
        while gyro.angle > angle:
            if distMid < MAX_DIST:
                if counter <= 0:
                    break
                counter -= 1
            mRight.on(-90)
            mLeft.on(90)

    elif angle > 0 and angle != -1: # left
        ramp_down.start()
        direction = 1
        while gyro.angle < angle:
            if distMid < MAX_DIST:
                if counter <= 0:
                    break
                counter -= 1
            mRight.on(90)
            mLeft.on(-90)
    elif angle == 0:
        ramp_down.start()
        sleep(0.2)

    elif angle == -1:
        mRight.on(100)
        mMid.on(100)
        mLeft.on(100)
        ramp_down.start()
        sleep(0.3)



    gyro.mode = 'GYRO-RATE'

    if angle != 0:
        mRight.off(brake=True)
        mLeft.off(brake=True)
        sleep(0.04)

### TRACKING ###

def mid():
    global distMid
    while True:
        distMid = irMid.proximity

prox = Thread(target=mid)

def tracking():
    check.start()
    stuck.start()

    while True:
        global distMid
        global direction
        global speed
        global counter

        if distMid < MAX_DIST:
            if counter <= 0:
                mRight.on(-100)
                mMid.on(-100)
                mLeft.on(-100)
            counter -= 1

        elif direction == -1:
            mRight.on(-speed)
            mMid.on(0)
            mLeft.on(speed)

        elif direction == 1:
            mRight.on(speed)
            mMid.on(0)
            mLeft.on(-speed)

    print("Stopped")

### MAIN ###

leds.set_color('LEFT', (1, 0))
leds.set_color('RIGHT', (1, 0))

while not btn.enter:
    btn.process()   

    if btn.up:
        angle = angle - 5
        print(angle)
        while btn.up:
            sleep(0.00001)

    if btn.down:
        angle = angle + 5
        print(angle)
        while btn.down:
            sleep(0.00001)

    if btn.right:
        leds.set_color('LEFT', (1, 1))
        leds.set_color('RIGHT', (1, 1))
        print("Calibrating...")

        gyro.reset()
        gyro.calibrate()

        print("Done")
        leds.set_color('LEFT', (1, 0))
        leds.set_color('RIGHT', (1, 0))

    if btn.left:
        angle = -1
        print("Reverse then go")
        while btn.left:
            sleep(0.00001)

print("Started")

leds.set_color('LEFT', (0 , 1))
leds.set_color('RIGHT', (0 , 1))

irMid.mode = 'IR-PROX'

gyro.mode = 'GYRO-ANG'
gyro.reset()

sleep(4.88)

prox.start()

goto(angle)
tracking()
