#!/usr/bin/env micropython
from ev3dev2.sensor import INPUT_1
from ev3dev2.sensor.lego import InfraredSensor
from ev3dev2.motor import OUTPUT_A, OUTPUT_B, OUTPUT_C, LargeMotor

ir = InfraredSensor(INPUT_1)
mRight = LargeMotor(OUTPUT_A)
mMid = LargeMotor(OUTPUT_B)
mLeft = LargeMotor(OUTPUT_C)

mRight.position = 0
mLeft.position = 0

totalAngle = 0

def goto(angle):
    global totalAngle
    while abs(totalAngle) < abs(angle):
        print(totalAngle)
        totalAngle = (2.5 / 12) * (mRight.position - mLeft.position)
        mRight.on(50)
        mLeft.on(-50)

    mRight.off(brake = True)
    mLeft.off(brake = True)


while True:
    print(ir.proximity)

