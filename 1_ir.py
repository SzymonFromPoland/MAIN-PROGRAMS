#!/usr/bin/env micropython

from ev3dev2.motor import OUTPUT_A, OUTPUT_B, OUTPUT_C, OUTPUT_D, LargeMotor, MediumMotor
from ev3dev2.sensor import INPUT_1, INPUT_2
from ev3dev2.sensor.lego import InfraredSensor, GyroSensor
from ev3dev2.led import Leds
from ev3dev2.button import Button
from time import sleep
from threading import Thread

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
speed = 50


### MISS CHECK ###

def check_if_missed():
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
            sleep(0.1)

        toggle = True

slow = Thread(target=slow_down, args=(speed / 2 - 5, 1))

### RAMP DOWN ###

def ramp():
    mRamp.on_for_degrees(100, 82)

ramp_down = Thread(target=ramp)

### TRACKING ###

def tracking():
    
    check.start()
    while True:
        global distMid
        global direction
        global speed
        global counter

        print(distMid)

        # btn.process()

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

        # if btn.enter:
        #     break

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

irMid.mode = 'IR-PROX'

sleep(1)

ramp_down.start()

tracking()