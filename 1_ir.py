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

MAX_DIST = 97
counter = 8
speed = 40


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

toggle = True

def slow_down(strength, nothing):
    global speed
    global toggle

    if toggle:
        toggle = False
        speed -= strength
        for i in range(strength):
            speed = speed + 1
            sleep(0.07)

        toggle = True

slow = Thread(target=slow_down, args=(speed / 2, 1))

### RAMP ###

def when_stuck():
    sleep(0.3)

    while True:
        global distMid
        sleep(0.6)
        if abs(gyro.rate) < 5 and distMid > MAX_DIST:
            mRamp.on_for_degrees(100, -15, brake = True)
            mRamp.on_for_degrees(100, 15, brake = False)

stuck = Thread(target=when_stuck)

def ramp():
    mRamp.on_for_degrees(100, 90, brake=False)


ramp_down = Thread(target=ramp)

### TRACKING ###

def tracking():

    ramp_down.start()
    check.start()
    stuck.start()

    while True:
        global distMid
        global direction
        global speed
        global counter

        distMid = irMid.proximity

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

    print("Stoped")

### MAIN ###

leds.set_color('LEFT', (1, 0))
leds.set_color('RIGHT', (1, 0))

while True:
    btn.process()
    if btn.up:
        print("Started")
        direction = -1
        break
    if btn.down:
        print("Started")
        direction = 1
        break
    if btn.right:
        leds.set_color('LEFT', (1, 1))
        leds.set_color('RIGHT', (1, 1))
        print("Calibrating...")
        gyro.reset()
        gyro.calibrate()
        print("Done")
        leds.set_color('LEFT', (1, 0))
        leds.set_color('RIGHT', (1, 0))

leds.set_color('LEFT', (0 , 1))
leds.set_color('RIGHT', (0 , 1))

irMid.mode = 'IR-PROX'

sleep(4.9)

tracking()