from time import sleep 
import RPi.GPIO as GPIO
from datetime import datetime as dt

XDIR = 14 # Sets direction of x-axis - false goes towards home
XSTEP = 15 # pin to alternate signal to step x-axis in direction specified by XDIR
YDIR = 17 # Sets the direction of the y-axis - false goes towards home
YSTEP = 18 # pin to alternate signal to step y-axis in direction specified by YDIR
XSWITCH = 22 # limit switch for x-axis. Goes to 0 when switch triggered
YSWITCH = 23 # limit switch for y-axis. Goes to 0 when switch triggered
NEEDLE = 11 # is True when needle is down
MAX_WIDTH_MM = 1600
MAX_HEIGHT_MM = 1600
stepsPerMM = 50
CENTER = (80*stepsPerMM,80*stepsPerMM)
 
delay=0.0002

last_needle = False # previous needle state
needle_change_time = dt.now().microsecond
def needle_up():
	state = GPIO.input(NEEDLE)
	if state != last_needle:
		sleep(0.0001)
		state2 = GPIO.input(NEEDLE)
		sleep(0.0001)
		state3 = GPIO.input(NEEDLE)
		if state == state2 and state2 == state3:
			last_needle = state
			return not state
		else:
			return not last_needle
	return not state
		
	#return GPIO.input(NEEDLE)

def step(pin):
	GPIO.output(pin,True)
	sleep(delay)
	GPIO.output(pin,False)
	sleep(delay)

def home(): #drive both axis home.
	while GPIO.input(YSWITCH) == 1 or GPIO.input(XSWITCH) == 1: # drive untol home limit switches triggered

	# set direction to home
		GPIO.output(XDIR, False)
		GPIO.output(YDIR, False)

	#drive axis home until switch triggered	
		if(GPIO.input(22) == 1):
			step(XSTEP)

		if(GPIO.input(23) == 1):
			step(YSTEP)
		
	currentX = 0 #setto zero!
	currentY = 0
#end of home

class RobostichBoundsError(Exception):
	def __init__(self,value):
		self.value = value
	def __str__(self):
		return repr(self.value)
	

def load_stitch_csv(csv_file):
	f = open(csv_file,"r")
	xlist = []
	ylist = []
	while True:
	   	line = f.readline()
	    	if not line:
      			break
		line = line.strip("\n").split(",")
    		x = line[2]
    		y = line[3]
    		xlist.append(float(x.strip('"')))
    		ylist.append(float(y.strip('"')))
	f.close()
	width = (max(xlist) - min(xlist))
	height = max(ylist) - min(ylist)
	if width > MAX_WIDTH_MM:
		raise RobostichBoundsError("Design width, "+str(width)+" excedes max allowed,"+str(MAX_WIDTH_MM))
	if height > MAX_HEIGHT_MM:
		raise RobostichBoundsError("Design height,"+str(height)+" excedes max allowed,"+str(MAX_HEIGHT_MM))
	
	xoffset = int((width/2.0 - xlist[0])*stepsPerMM)
	yoffset = int((height/2.0 - ylist[0])*stepsPerMM)
	xlist = [CENTER[0] - int(x*stepsPerMM) for x in xlist]
	ylist = [CENTER[1] - int(y*stepsPerMM) for y in ylist]
	print min(xlist),max(xlist)
	stitches = zip(xlist,ylist)
	start = (CENTER[0] - xoffset,CENTER[1] - yoffset)
	# make the center of the thing happen at the center of the stage
	return (stitches,start)

def move(xdir,xsteps,ydir,ysteps):
	GPIO.output(XDIR,xdir)
	GPIO.output(YDIR,ydir)
	for i in range(xsteps):
		step(XSTEP)
	for i in range(ysteps):
		step(YSTEP)
	
	


def drive(start,goal):
	currentX,currentY = start
	goalX,goalY = goal
	delay0 = 0.00045
	delay_min=0.0002
	delay_inc = 0.00001
	# set direction
	if goalX > currentX:
		xinc = 1
		GPIO.output(XDIR,True)
	else:
		xinc = -1
		GPIO.output(XDIR,False)
	if goalY > currentY:
		yinc = 1
		GPIO.output(YDIR,True)
	else:
		yinc = -1
		GPIO.output(YDIR,False)

	delay = delay0

	
	while currentX != goalX or currentY != goalY:
		while not needle_up(): # wait for the needle to come up
			sleep(0.0002)
		 
		if currentX != goalX:
			GPIO.output(XSTEP,True)
			currentX += xinc
		
		if currentY != goalY:
			GPIO.output(YSTEP,True)
			currentY += yinc

		sleep(delay)
		GPIO.output(XSTEP,False)
		GPIO.output(YSTEP,False)
		sleep(delay)
		if delay > delay_min:
			delay -= delay_inc
			
	
	# wait for the needle to come down
	while needle_up():
		sleep(0.0002)
	return (currentX,currentY)
