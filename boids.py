import random 			# Random starts
import math				# Absolute value calculations
import time 			# Timing features
from tkinter import *	# All visuals

# Constants - Should not change
WIDTH 	= 800		# Pixels wide
HEIGHT 	= 600		# Pixels height

BOIDS 		= 20	# Number of boids
BOID_RADIUS = 3		# Radius of pixels

WALL 		= 100	# Number of pixels from side
FORCE_BACK 	= 10	# Acceleration back from the wall when out of bounds
SPEED_LIMIT = 500	# Boid velocity limit

OFFSET_START = 20		# Pixel start offset from the screen
WIND_DIRECTION = 1, 5	# The direction to move the boid flock (Right 1, Down 5)

START_TIME = time.time() 	# Start time of program
WAIT_TIME = 10 			 	# Time to wait until next feature starts

################################################################################

'''
 ' Main function to start initialise and mainloop
 '
 ' Input:	None
 '
 ' Output: 	None
'''
def main():
	# Start the program
	initialise()
	mainloop()

'''
 ' TKinter functions to facilitate the building and drawing of the GUI Environment
'''

'''
 ' Initialise the graph and build the boids
 '
 ' Input:	None
 '
 ' Output:	None
'''
def initialise():
	build_boids()
	build_graph()

'''
 ' Build the graph for the interface using TKinter
 '
 ' Input:	None
 '
 ' Output:	None
'''
def build_graph():
	global graph
	root = Tk()
	root.overrideredirect(True)
	# Create the screen
	root.geometry('%dx%d+%d+%d' % (WIDTH, HEIGHT, (root.winfo_screenwidth() 
		- WIDTH) / 2, (root.winfo_screenheight() - HEIGHT) / 2))
	root.bind_all('<Escape>', lambda event: event.widget.quit())
	graph = Canvas(root, width=WIDTH, height=HEIGHT, background='white')
	graph.after(40, update)
	graph.pack()


'''
 ' Main loop for simulation, updates after 40 ticks
 '
 ' Input:	None
 '
 ' Output:	None
'''
def update():
	draw() # Draw boids
	move_all_boids_to_new_positions()
	graph.after(40, update)

'''
 ' Draw all the boids to the screen
 '
 ' Input:	None
 ' Output:	None
'''
def draw():
	global img
	# img = PhotoImage(file="duck.gif")
	graph.delete(ALL) # Remove and re-add
	for boid in boids:
		# These draw the 4 edges - up, down, left and right of each boid
		x1 = boid.position.x - BOID_RADIUS # Left
		y1 = boid.position.y - BOID_RADIUS # Up
		x2 = boid.position.x + BOID_RADIUS # Right
		y2 = boid.position.y + BOID_RADIUS # Down
		
		# Images overlap sometimes because issa square
		# graph.create_image(x1,y1, anchor=CENTER, image=img)
		# Draw the boids as an oval
		graph.create_oval((x1, y1, x2, y2), fill='red')
	
	graph.update() # Update again


'''
 ' Boid Functions
 '
 ' Includes features, building and moving of boids
'''

'''
 ' Create a specific number of boids 
 '
 ' Input:	None
 '
 ' Output:	None
'''
def build_boids():
	global boids
	boids = tuple(Boid(WIDTH, HEIGHT, OFFSET_START) for boid in range(BOIDS))

'''
 ' Move all the boids to new positions on the screen.
 ' Split all the main boid stuff into separate functions
 '
 ' Input:	None
 '
 ' Output:	None
'''
def move_all_boids_to_new_positions():
	# Main boid loop
	for boid in boids:
		# Check the boid limits on the screen
		boid.bound_position()
		# Update the boid velocity according to the rules
		boid.update_velocity(boids)
		# Move the boid to a new position
		boid.move_boid()


'''
 ' Boid objects
 ' This class defines a boid object and how they interact with each other.
 ' A boid starts with a random start somewhere on the screen and move together
 ' based on the rules defined.
'''
class Boid:
	'''
	 ' Constructor
	 '
	 ' Input:	width - The WIDTH of the screen in pixels
	 ' 			height - The HEIGHT of the screen in pixels
	 '			offset - The offset from the screen they will start from in pixels
	 '
	 ' Output:	None
	'''
	def __init__(self, width, height, offset):
		self.velocity = TwoDVector(0, 0) # Initial velocity is 0 
		# The `*` unpacks the sequence into positional arguments
		# random_start returns x, y because 
		# we want to put it into TwoDVector as x, y
		self.position = TwoDVector(*self.random_start(width, height, offset))
		self.perching = False
		# Minimum of 20 so it's noticeable
		self.perchTimer = random.randint(20, 100) # Random perching time

	'''
	 ' Starts the boid at a random place on an edge of the screen. It can start
	 ' on any edge but is drawn first off screen. Hence the use of `offset`.
	 '
	 ' Input:	width - The WIDTH of the screen in pixels
	 ' 			height - The HEIGHT of the screen in pixels
	 '			offset - The offset from the screen they will start from in pixels
	 '
	 ' Output:	x - The position on the x-axis to start the boid
	 '			y - The position on the y-axis to start the boid
	 '			x, y will be used as a vector placement
	'''
	def random_start(self, width, height, offset):
		if random.randint(0, 1): # 1 = Left and Right
			y = random.randint(1, height) # Random place along height
			if random.randint(0, 1):
				# Left edge
				x = -offset
			else:
				# Right edge
				x = width + offset
		else: # 0 = Top and Bottom
			x = random.randint(1, width) # Random place along width
			if random.randint(0, 1):
				# Top edge
				y = -offset
			else:
				# Bottom edge
				y = height + offset

		return x, y # To be used as a vector 

	'''
	 ' Updates the velocity of a boid according to defined rules.
	 ' Velocity is stored in temp_velocity because it will not
	 ' be assigned if the boid is perching.
	 '
	 ' Input:	boids - All the boids
	 '
	 ' Output:	None
	'''
	def update_velocity(self, boids):
		v1 = self.rule1(boids)
		v2 = self.rule2(boids)
		v3 = self.rule2(boids)
		v4 = self.ruleWind()
		# Add any additional velocity rules here
	
		# Don't return temp_velocity because it's for each specific boid
		self.temp_velocity = v1 + v2 + v3 + v4

	'''
	 ' Move the boids as well as add the new velocity to it. Also calls 
	 ' the speed limiting function to make sure we don't exceed a specific
	 ' velocity.
	 '
	 ' Input:	None
	 '
	 ' Output:	None (Returns if still perching)
	'''
	def move_boid(self):
		# Ground level perching for a random time
		if self.perching:
			if self.perchTimer > 0:
				self.perchTimer -= 1
				return # Don't allow velocity to be changed
			else:
				self.perching = False

		# Assign the temp velocity
		self.velocity += self.temp_velocity
		self.limit_speed() # Make sure we don't exceed a specific velocity
		# The lower `/ 100` is, the faster they move
		self.position += self.velocity / 100 # Move the posisiton of the boid

	'''
	 ' Rule 1 taken from Boids pseudocode. It deals with cohesion and the 
	 ' "centre of mass" for the entire flock. It moves all the boids together.
	 ' This rule averages positions.
	 '
	 ' Input:	boids - All the boid objects
	 '
	 ' Output:	A vector to add as a position vector
	'''
	def rule1(self, boids):
		vector = TwoDVector(0, 0)
		for boid in boids:
			if boid is not self:
				vector += boid.position
		vector /= len(boids) - 1
		# if `/ 100` it takes a long time to group up
		return (vector - self.position) / 10

	'''
	 ' Rule 2 taken from Boids pseudocode. It deals with separation and makes
	 ' sure the boids don't collide with each other. 
	 '
	 ' Input:	boids - All the boid objects
	 '
	 ' Output:	vector - A new vector to move the boid 
	'''
	def rule2(self, boids):
		vector = TwoDVector(0, 0)
		for boid in boids:
			if boid is not self:
				# The higher `< 40` is, the farther they stay from each other
				if abs(self.position - boid.position) < 40: 
					vector -= (boid.position - self.position)
		return vector

	'''
	 ' Rule 3 taken from Boids pseudocode. It deals with alignment. This rule
	 ' is similar to rule 1 but averages velocities instead of positions.
	 '
	 ' Input:	boids - All the boid objects
	 '
	 ' Output:	A vector to add as a velocity vector
	'''
	def rule3(self, boids):
		vector = TwoDVector(0, 0)
		for boid in boids:
			if boid is not self:
				vector += boid.velocity
		vector /= len(boids) - 1
		return (vector - self.velocity) / 2 # Makes it choppy otherwise

	'''
	 ' Feature #1 - Wind Rule
	 ' This rule takes into account wind so the boid flock moves in a certain 
	 ' direction.
	 ' +x = right; -x = left
	 ' +y = down; -y = up
	 '
	 ' Input:	None
	 '
	 ' Output:	wind_vector - A vector direction to move the boid in 
	'''
	def ruleWind(self):
		# Wait for 10 seconds before starting a new feature
		if (time.time() - START_TIME) > WAIT_TIME:
			# Unpack the wind x, y as a vector
			wind_vector = TwoDVector(*WIND_DIRECTION) # Down and Right Direction
		else: # No wind until WAIT_TIME
			wind_vector = TwoDVector(0, 0)

		return wind_vector

	'''
	 ' Feature #2 & #3 - Bound Position & Perching
	 ' The bounding feature makes sure the boids stay on screen by applying an
	 ' acceleration in the opposite direction when they get close to the edge.
	 ' WALL is used so the boids can be seen changing direction on screen.
	 ' The perching feature makes a boid sit on the bottom edge of the screen for 
	 ' a random amount of time if it's near the edge. HEIGHT-BOID_RADIUS is used
	 ' because we wanted to show that it activates when it's still on the screen.
	 '
	 ' There's a slight problem with perching where the boid bounces up and down
	 ' while it's above HEIGHT-BOID_RADIUS and it can be seen visually.
	 '
	 ' Input:	None
	 '
	 ' Output: 	None - Returns if the boid is perching
	'''
	def bound_position(self):
		# Ground Level Perching
		if self.position.y > HEIGHT-BOID_RADIUS:
			self.position.y = HEIGHT-7 # 7 so the entire boid is on the screen
			self.perching = True
			return # We don't want to adjust their bounding position

		# Create viewing boundaries
		# Not 0 otherwise they will completely go off screen
		# when we start changing direction
		if self.position.x < WALL:
			self.velocity.x += FORCE_BACK # How much to move away
		elif self.position.x > WIDTH - WALL:
			self.velocity.x -= FORCE_BACK
		if self.position.y < WALL:
			self.velocity.y += FORCE_BACK
		# Not HEIGHT otherwise they will completely go off screen
		# when we start changing direction
		elif self.position.y > HEIGHT - WALL:
			self.velocity.y -= FORCE_BACK

	'''
	 ' Feature #4 - Speed Limiting
	 ' The speed limiting feature makes sure the velocity of a boid does not exceed
	 ' a certain value.
	 ' The pseudocode code says to use `* SPEED_LIMIT` but if this was used, the 
	 ' boids' movement would become choppy and they would jerk around. Therefore, 
	 ' `/ SPEED_LIMIT` was used which gives them a more smooth motion. Not sure
	 ' why this works.
	 '
	 ' Input:	None
	 '
	 ' Output:	None
	'''
	def limit_speed(self):
		# Limit boid speed.
		if abs(self.velocity) > SPEED_LIMIT:
			self.velocity /= abs(self.velocity) / SPEED_LIMIT
			# Pseudocode says `* SPEED_LIMIT` but their movement is really choppy
			# self.velocity /= abs(self.velocity) * SPEED_LIMIT 


'''
 ' The TwoDVector class was adapted from: 
 ' http://hplgit.github.io/primer.html/doc/pub/class/._class-readable004.html
 ' It's use is to be able to treat the boids' velocity and position as vectors
 ' and to be able to do calculations based on these numbers.
'''
class TwoDVector:
	def __init__(self, x, y):
		self.x = float(x)
		self.y = float(y)

	'''
	 ' String function - `print`
	'''
	def __str__(self):
		return 'TwoDVector(%s, %s)' % (self.x, self.y)

	'''
	 ' Add function - `+`
	'''
	def __add__(self, other):
		return TwoDVector(self.x + other.x, self.y + other.y)

	'''
	 ' Subtraction function - `-`
	'''
	def __sub__(self, other):
		return TwoDVector(self.x - other.x, self.y - other.y)

	'''
	 ' Multiplication function - `*`
	'''
	def __mul__(self, other):
		return TwoDVector(self.x * other, self.y * other)

	'''
	 ' Division function - `/`
	 ' Python 3 doesn't have normal division, only truediv and floordiv
	 ' We only use truediv
	'''
	def __truediv__(self, other):
		return TwoDVector(self.x / other, self.y / other)

	'''
	 ' Inplace Add function - `+=`
	'''
	def __iadd__(self, other):
		self.x += other.x
		self.y += other.y
		return self

	'''
	 ' Inplace Subtraction function - `-=`
	'''
	def __isub__(self, other):
		self.x -= other.x
		self.y -= other.y
		return self

	'''
	 ' Inplace Division function - `/=`
	 ' Python 3 doesn't have normal division, only itruediv and ifloordiv
	 ' We only use itruediv
	'''
	def __itruediv__(self, other):
		if isinstance(other, TwoDVector):
			self.x /= other.x if other.x else 1
			self.y /= other.y if other.y else 1
		else:
			self.x /= other
			self.y /= other
		return self

	'''
	 ' Equals function - `=`
	'''
	def __eq__(self, other):
		return self.x == other.x and self.y == other.y

	'''
	 ' Not Equals function - `!=`
	 ' Reuse eq because it's just the opposite
	'''
	def __ne__(self, other):
		return not self.__eq__(other)

	'''
	 ' Absolute Value function - `abs()`
	'''
	def __abs__(self):
		return math.sqrt(self.x**2 + self.y**2)

################################################################################

# Start this bitch
if __name__ == '__main__':
	main()