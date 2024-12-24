from __future__ import annotations
import dudraw
import math
from dudraw import Color
import random

"""
    A program that uses dudraw to make a particle system consisting of fireworks, fire, marbles, and sparklers
    Author: Jackson Sanger
    Date: 3-15-2023
    Course: COMP 1352
    Assignment: Project 7 - Particle System (Conga Line)
    Collaborators: none
    Internet Source: none
"""

#copied vector class from project description
class Vector:
    def __init__(self, some_x=0, some_y=0):
        self.x = some_x
        self.y = some_y

    def limit(self, l):
        if(self.length() >= l):
            self.resize(l)

    def resize(self, l):
        length = math.sqrt(self.x ** 2 + self.y**2)
        self.x *= (l/length)
        self.y *= (l/length)

    def __add__(self, other_vector):
        return Vector(self.x+other_vector.x, self.y + other_vector.y)

    def __sub__(self, other_vector):
        return Vector(self.x-other_vector.x, self.y - other_vector.y)

    def __isub__(self, other_vector):
        self.x -= other_vector.x
        self.y -= other_vector.y
        return self

    def __iadd__(self, other_vector):
        self.x += other_vector.x
        self.y += other_vector.y
        return self

    def divide(self, s):
        self.x /= s
        self.y /= s

    def length(self):
        return math.sqrt(self.x**2 + self.y**2)

    def angle_in_radians(self):
        return math.tan((self.y/self.x))

#define our parent class for a general Particle
class Particle:
    #in the constructor, take vectors for the position and velocity, as well as values for the particle size and its lifetime
    def __init__(self, pos: Vector, vel: Vector, size: float, lifetime: int):
        self.pos = pos
        self.vel = vel
        self.size = size
        #set the color to be random by default
        self.color = Color(random.randint(0,255), random.randint(0, 255), random.randint(0, 255))
        self.lifetime = lifetime
    #define a method to determine if the particle's lifetime is over
    def has_expired(self)->bool:
        #return whether or not its lifetime is 0
        return self.lifetime == 0
    #define a method to move the particle
    def move(self):
        #if it hasn't expired:
        if not self.has_expired():
            #add the velocity vector to the position and decrease the liftime by 1
            self.pos += self.vel
            self.lifetime -= 1

#create an accelerating particle class that inherits from particle
class AcceleratingParticle(Particle):
    #have all of the same parameters for the constructor, but add one more for an acceleration vector
    def __init__(self, pos: Vector, vel: Vector, acc: Vector, size: float, lifetime: int):
        #call the parent constructor
        Particle.__init__(self, pos, vel, size, lifetime)
        #construct the acceleration vector
        self.acc = acc
    #override the move method from the parent class
    def move(self):
        #call the parent move method, but then also add the acceleration vector to the velocity vector
        Particle.move(self)
        self.vel += self.acc

#create a class for a sparkler particle, inheriting from the base particle class
class SparkParticle(Particle):
    def __init__(self, pos: Vector, vel: Vector, size: float, lifetime: int):
        #call the parent constructor, and just override the color so that it is a golden color
        Particle.__init__(self, pos, vel, size, lifetime)
        self.color = Color(255, 215, 0) #gold
    #define a draw method
    def draw(self):
        #set the pen color to gold, and then draw each particle with a line in the direction of its velocity
        dudraw.set_pen_color(self.color)
        dudraw.line(self.pos.x, self.pos.y, self.pos.x + self.vel.x, self.pos.y + self.vel.y)

#create a class for a Fire particle that inherits from the base particle class
class FireParticle(Particle):
    def __init__(self, pos: Vector, vel: Vector, size: float, lifetime: int):
        #call the parent constructor, and just override the color to start at yellow
        Particle.__init__(self, pos, vel, size, lifetime)
        self.color = Color(255, 255, 0) #yellow
    #define a draw method
    def draw(self):
        #set the pen color, and then draw the particle as a circle
        dudraw.set_pen_color(self.color)
        dudraw.filled_circle(self.pos.x, self.pos.y, self.size)
        #everytime draw is called, decrease the "green" component of color
        self.color._g -= 4
    #override the parent move method
    def move(self):
        #call the parent's move method, but also decrease the particle size everytime this is called
        Particle.move(self)
        self.size -= 0.0001

#now create a Firework particle class, this time inheriting from Accelerating particle, since this type of particle accelerates
class FireworkParticle(AcceleratingParticle):
    #define a draw method
    def draw(self):
        #set the pen color (which will be random), and draw as a square
        dudraw.set_pen_color(self.color)
        dudraw.filled_square(self.pos.x, self.pos.y, self.size)

#create another accelerating particle, a marble, which inherits from accelerating particle
class MarbleParticle(AcceleratingParticle):
    def draw(self):
        #set the pen color (which will be random), and draw as a circle
        dudraw.set_pen_color(self.color)
        dudraw.filled_circle(self.pos.x, self.pos.y, self.size)

#define a general particle container class. These are the actual containers where the particles live
class ParticleContainer:
    #take a position vector as a parameter
    def __init__(self, pos: Vector):
        #construct the position attribute, and then also initialize an emptylist which will contain particles
        self.pos = pos
        self.particles = []
    #define an animate method
    def animate(self):
        #initialize an empty list which will contain the particles that are expiered
        particles_to_remove = []
        #loop through the particles list:
        for particle in self.particles:
            #if the particle still has life, draw it on the canvas and move it
            if not particle.has_expired():
                particle.draw()
                particle.move()
            #otherwise, meaning its expired, add it to the list of particles to be removed
            else:
                particles_to_remove.append(particle)
        #once we're done checking, loop through the particles to remove list and remove every one
        #we do it in this way to avoid altering the length of the list as we are looping through it
        for particle in particles_to_remove:
            self.particles.remove(particle)

#define a Firework, which is a type of particle container
class Firework(ParticleContainer):
    def __init__(self, pos: Vector):
        #call the parent constructor
        ParticleContainer.__init__(self, pos)
        #add 500 firework particles to the particles list upon creation
        for i in range(500):
            #we calculate a random radius and angle to use in our velocity, so that our firework is not square
            radius = random.random() * 0.04
            angle = random.random() * 2 * math.pi
            #each particle starts at the middle of the container, has velocity that is a random direction around the unit circle, and acceleration that is 0 for x, and betweem -0.012 and -0.08 for y
            #it also has a size of 0.004 and a lifetime of 50
            self.particles.append(FireworkParticle(Vector(self.pos.x, self.pos.y), Vector(radius * math.cos(angle), radius * math.sin(angle)), Vector(0, random.random() * -0.004 - 0.008), 0.004, 50))

#create a container for our marble particles
class Marbles(ParticleContainer):
    def __init__(self, pos: Vector):
        #call the parent constructor
        ParticleContainer.__init__(self, pos)
        #add 10 marbles to the particles list upon creation
        for i in range(10):
            #each marble has a random position anywhere on the screen, a random velocity between -0.04 and 0.04 for x and y, and an acceleration of 0 for x, and random between -0.002 and -0.001 for y (gravity)
            #they also have a size of 0.05, and a lifetime of 500
            self.particles.append(MarbleParticle(Vector(random.random() * 0.9 + 0.05, random.random() * 0.9 + 0.05), Vector(random.random()*0.08 - 0.04, random.random()*0.08 - 0.04), Vector(0, random.random() * 0.001 - 0.002), 0.05, 500))
    #override the animate metod:   
    def animate(self):
        # loop through all marbles
        for i in range(len(self.particles)):
            # loop through every marble after the one we're currently on
            for j in range(i+1, len(self.particles)):
                # calculate the distance between each marble by subtracting the position vectors
                distance_vector = self.particles[i].pos - self.particles[j].pos
                # if the distance vector is less than the length of both marbles radii, they have collided. also make sure we are not comparing the same marble:
                if distance_vector.length() < self.particles[i].size + self.particles[j].size and i != j:
                    # add the distance vector to the velocity vector of one, and subtract from the other
                    self.particles[i].vel += distance_vector
                    self.particles[j].vel -= distance_vector
                # each time through, check to make sure the velocity doesn't get too high
                self.particles[i].vel.limit(0.02)
                self.particles[j].vel.limit(0.02)
            #after all of the velocities have been adjusted, add controls for bouncing off the edges:
            if self.particles[i].pos.x + self.particles[i].size > 1 or self.particles[i].pos.x - self.particles[i].size < 0:
                self.particles[i].vel.x *= -1
            if self.particles[i].pos.y + self.particles[i].size > 1 or self.particles[i].pos.y - self.particles[i].size < 0:
                self.particles[i].vel.y *= -1
        # call the animate method of the parent class to update and draw the particles after we have changed all of the velocities
        ParticleContainer.animate(self)

#define a general emitter class, which is a type of container
class Emitter(ParticleContainer):
    def __init__(self, pos: Vector, fire_rate: int):
        #call the parent constructor, and just add an attribute for the fire rate of the emitter(how many particles continue come out of the emitter)
        ParticleContainer.__init__(self, pos)
        self.fire_rate = fire_rate
#create a fire particle container, which is an emitter
class Fire(Emitter):
    #override the animate method
    def animate(self):
        #call the parent method
        ParticleContainer.animate(self)
        #every time this method is called, we add "fire rate" particles to the list. This allows the emitter to constantly emit, which is why it doesn't disappear
        for i in range(self.fire_rate):
            #add "fire rate" particles. They start at the location of the container, have random velocity between -0.002 and 0.002 for x and 0.002 and 0.005 for y (which is why they only move up)
            #the size is random between 0.01 and 0.03, and they have a lifetime of 50
            self.particles.append(FireParticle(Vector(self.pos.x, self.pos.y), Vector(random.random() * 0.004 - 0.002, random.random() * 0.003 + 0.002), random.random()*0.02 + 0.01, 50))
#create a sparkler container, which is a type of emitter
class Sparkler(Emitter):
    #override the animate method
    def animate(self):
        #each time, we start by redrawing the sparkler "holder"
        dudraw.set_pen_color(dudraw.WHITE)
        dudraw.set_pen_width(0.005)
        dudraw.line(self.pos.x, self.pos.y, self.pos.x, self.pos.y - 0.25)
        #reset the pen_width so it isn't so thick
        dudraw.set_pen_width()
        #call the parent method
        ParticleContainer.animate(self)
        #add "fire rate" sparkler particles each time animate is called. 
        for i in range(self.fire_rate):
            #calculate a random radius and angle to be used for our velocity. this makes our sparkler circular
            radius = random.random() * 0.04
            angle = random.random() * 2 * math.pi
            #add the particles to the list. each particle starts at the center of the sparkler, has a velocity of a random value around the unit circle
            #also has a size of 0.04 and a liftime of 5
            self.particles.append(SparkParticle(Vector(self.pos.x, self.pos.y), Vector(radius * math.cos(angle), radius * math.sin(angle)), 0.04, 5))

#main code block

#create an empty containers list
containers = []
#add a fire in the middle of the screen towards the bottom, fire rate of 30
containers.append(Fire(Vector(0.5, 0.15), 30))
#add 2 sparklers with fire rates of 200, one in the top right and one in the top left
containers.append(Sparkler(Vector(0.75, 0.75), 200))
containers.append(Sparkler(Vector(0.25, 0.75), 200))

#create an empty key variable for our while loop condition
key = ''
#continue while "q" has not been pressed
while key != 'q':
    #clear the screen each time
    dudraw.clear(dudraw.DARK_GRAY)
    #loop through the containers list, and then animate each one
    for container in containers:
        container.animate()
    
    #check if a key has been pressed:
    if dudraw.has_next_key_typed():
        #get the key that was pressed
        key = dudraw.next_key_typed()
        #if it was an "f", then add a firework to the containers list at the mouse location
        if key == 'f':
            containers.append(Firework(Vector(dudraw.mouse_x(), dudraw.mouse_y())))
    #if the mouse is clicked, add marbles to the containers list at the mouse location (though the marbles will appear in random locations)
    if dudraw.mouse_clicked():
        containers.append(Marbles(Vector(dudraw.mouse_x(), dudraw.mouse_y())))
    #show the screen
    dudraw.show(20)