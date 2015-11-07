import RPi.GPIO as GPIO
from time import sleep
from embroidlib import *

GPIO.setmode(GPIO.BCM)

GPIO.setup(14, GPIO.OUT) #direction x , False goes home
GPIO.setup(15, GPIO.OUT) # step x
GPIO.setup(17, GPIO.OUT) # direction y, false goes home
GPIO.setup(18, GPIO.OUT) #step y
GPIO.setup(22, GPIO.IN, pull_up_down = GPIO.PUD_UP) #tied to axis on pin 14/15
GPIO.setup(23, GPIO.IN, pull_up_down = GPIO.PUD_UP) #tied to axis on pin 17/18
GPIO.setup(11, GPIO.IN, pull_up_down = GPIO.PUD_DOWN) #needle up trigger True is up

stepsPerMM = 50 
delay = 0.0002  #this controls the speed of the stepper motors
stepSize = 50 #not used 
goalXMM = 0
goalYMM = 0
goalX = 0
goalY = 0
currentX = 0
currentY = 0


home()



goalXMM = 80
goalYMM = 80
goalX = goalXMM * stepsPerMM
goalY = goalYMM * stepsPerMM
drive()
currentX = 0
currentY = 0


j=0
for i in xlist:
	while GPIO.input(11) == False:
		print("needle down!")
	goalXMM = xlist[j]
	goalYMM = ylist[j]
	goalX = int(goalXMM * stepsPerMM)
	goalY = int(goalYMM * stepsPerMM)
	drive()	
	j+=1
	sleep(0.05)
	while GPIO.input(11) == True:
		print("finished moving, waiting")
	sleep(0.05)

print(str(goalXMM) + " , "  +  str(goalYMM))
print( str(currentX) + " , "  +str( currentY))
print(str(goalX) + " , "  +  str(goalY))





GPIO.cleanup()
