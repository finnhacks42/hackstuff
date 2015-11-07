import RPi.GPIO as GPIO
import pygame
from time import sleep
import sys

def step(pin):
	GPIO.output(pin,True)
	sleep(0.00005)
	GPIO.output(pin,False)
	sleep(0.00005)

def home(): #drive both axis home.
        correct = 0
	while GPIO.input(YSWITCH) == 1 or GPIO.input(XSWITCH) == 1 or correct < 10: # drive home until limit switches triggered lots of times...
                if GPIO.input(YSWITCH) == 1 and GPIO.input(XSWITCH) == 1:
                        correct +=1
		#print GPIO.input(YSWITCH),GPIO.input(XSWITCH)
                # set direction to home
		GPIO.output(XDIR, False)
		GPIO.output(YDIR, False)

	#drive axis home until switch triggered	
		if(GPIO.input(XSWITCH) == 1):
			step(XSTEP)

		if(GPIO.input(YSWITCH) == 1):
			step(YSTEP)
	print("Home!")	
	currentX = 0 #setto zero!
	currentY = 0


class RobostichBoundsError(Exception):
	def __init__(self,value):
		self.value = value
	def __str__(self):
		return repr(self.value)

def scale_stitches(xlist,ylist,largest_dim_mm):
	width = max(xlist) - min(xlist)
	height = max(ylist) - min(ylist)
	max_dim = max(width,height)
	scale = largest_dim_mm/float(max_dim)
	print "scaling by",scale
	xlist = [scale*x for x in xlist]
	ylist = [scale*y for y in ylist]
	return (xlist,ylist)
		

def load_stitch_csv(csv_file):
	f = open(csv_file,"r")
	xlist = []
	ylist = []
	count = 0
	while True:
	   	line = f.readline()
	    	if not line:
      			break
		line = line.strip("\n").strip('"')
		line = line.replace(" ","")
		line = line.split(",")
		line = [x.strip('"') for x in line]
		if line[0] == "*":
			line = line[1:]
			line[0] = "*"+line[0]
		if line[0].startswith("*"):
			try:
    				x = float(line[1])
    				y = float(line[2])
    				xlist.append(x)
    				ylist.append(y)
				#if x > 30:
				#	count+=1
				#	print line
				#	print line[1]
				#	print line[2]
			except:
				print "SKIPING",line
	f.close()
	xcenter,width = center(xlist)
	ycenter,height = center(ylist)
	print "Design size (mm)",width,"x",height
	if width > MAX_WIDTH_MM or height > MAX_HEIGHT_MM:
		print "Sorry your design was to big. Scaling to 100mm"
		xlist,ylist = scale_stitches(xlist,ylist,100)
		#raise RobostichBoundsError("Design width, "+str(width)+" excedes max allowed,"+str(MAX_WIDTH_MM))
	#if height > MAX_HEIGHT_MM:
	#	raise RobostichBoundsError("Design height,"+str(height)+" excedes max allowed,"+str(MAX_HEIGHT_MM))
	

	# now we want x center to be 0
	xlist = [x - xcenter for x in xlist]
	ylist = [y - ycenter for y in ylist]
	
	# now scale things to work in steps
	xlist = [int(x*stepsPerMM) for x in xlist]
	ylist = [int(y*stepsPerMM) for y in ylist]

	stitches = zip(xlist,ylist)

	# make the center of the thing happen at the center of the stage
	return (stitches)

def center(lst):
	minx,maxx = min(lst),max(lst)
	print "min",minx,"max",maxx
	range = max(lst)-min(lst)
	cent = minx+range/2.0
	return (cent,range)

def move(xdir,xsteps,ydir,ysteps):
	GPIO.output(XDIR,xdir)
	GPIO.output(YDIR,ydir)
	for i in range(xsteps):
		step(XSTEP)
	for i in range(ysteps):
		step(YSTEP)
	
	

class Driver():
	def __init__(self):
		self.last_state = 1
	
	def drive(self,start,goal,ignore_needle = False):
		currentX,currentY = start
		goalX,goalY = goal
		delay0 = 0.00008
		delay_min=0.000007
		delay_inc = 0.000001
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
			while (not self.needle_up()) and ignore_needle == False: # wait for the needle to come up
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
		while self.needle_up() and ignore_needle == False:
			sleep(0.0002)
		return (currentX,currentY)
	
	def needle_up(self):
		state = self.needle_state()
		return (state == 0)
	def needle_state(self):
		state = GPIO.input(NEEDLE)
		if state == self.last_state:
			return state
		num_measures = 2
		for i in range(num_measures):
			sleep(0.00001)
			next_state = GPIO.input(NEEDLE)
			if next_state != state:# inconsistant reading, probably a bounce
				return self.last_state 
		print "State changed",state
		self.last_state = state
		return state
		
		

XDIR = 14 # Sets direction of x-axis - false goes towards home
XSTEP = 15 # pin to alternate signal to step x-axis in direction specified by XDIR
YDIR = 17 # Sets the direction of the y-axis - false goes towards home
YSTEP = 18 # pin to alternate signal to step y-axis in direction specified by YDIR
XSWITCH = 23 # limit switch for x-axis. Goes to 0 when switch triggered
YSWITCH = 22 # limit switch for y-axis. Goes to 0 when switch triggered
NEEDLE = 11 # is True when needle is down
MAX_WIDTH_MM = 1600
MAX_HEIGHT_MM = 1600
stepsPerMM = 200
CENTER = (80*stepsPerMM,80*stepsPerMM)
delay=0.0002

last_needle = False # previous needle state


GPIO.setmode(GPIO.BCM)

GPIO.setup(XDIR, GPIO.OUT) #direction x , False goes home
GPIO.setup(XSTEP, GPIO.OUT) # step x
GPIO.setup(YDIR, GPIO.OUT) # direction y, false goes home
GPIO.setup(YSTEP, GPIO.OUT) #step y
GPIO.setup(XSWITCH, GPIO.IN, pull_up_down = GPIO.PUD_UP) #tied to axis on pin 14/15
GPIO.setup(YSWITCH, GPIO.IN, pull_up_down = GPIO.PUD_UP) #tied to axis on pin 17/18
GPIO.setup(NEEDLE, GPIO.IN, pull_up_down = GPIO.PUD_UP) #needle up trigger 0 is up

pygame.mixer.init()
sound = pygame.mixer.Sound("air_raid.wav")
clock = pygame.time.Clock()

driver = Driver()
in_file = sys.argv[1]
stitches = load_stitch_csv(in_file)

MOVE_STEP_MM = 2
MOVE = MOVE_STEP_MM*stepsPerMM
key = ""
print "type centering instruction key then enter. WARNING CODE ASSUMES NEEDLE IS UP. ENSURE NEEDLE IS CLEAR!!!"
while not (key == "h" or key == "d"): 
    key = raw_input("z=left, c=right, x=down, s=up, h=home, d = done :")
    if "z" == key: # left (assume X axis, away from home)
        driver.drive((0,0),(-MOVE,0),ignore_needle = True)
    if "c" == key:
        driver.drive((0,0),(MOVE,0),ignore_needle = True)
    if "x" == key:
        driver.drive((0,0),(0,-MOVE),ignore_needle = True)
    if "s" == key:
        driver.drive((0,0),(0,MOVE), ignore_needle = True)
    if "d" == key:
        pos = (0,0) # assume we are now centered
    if "h" == key:
        home()
	pos = (0,0)
	# drive to center
	driver.drive(pos,CENTER,ignore_needle=True)
	pos = (0,0)



print stitches[1]
for goal in stitches[1:]:
	print "driving to",goal
	pos = driver.drive(pos,goal)	

sound.play()
while pygame.mixer.get_busy():
	clock.tick(30)

GPIO.cleanup()

