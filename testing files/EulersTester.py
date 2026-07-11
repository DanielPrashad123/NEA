
import matplotlib.pyplot as plt
import numpy as np

takeoff_angle = 23
takeoff_speed = 100

while type(takeoff_angle) != int or takeoff_angle <= 0 or takeoff_angle > 90:
    try:
        takeoff_angle = int(input("enter valid takeoff angle:"))
    except ValueError:
        takeoff_angle = 0

while type(takeoff_speed) != int or takeoff_speed <= 0:
    try:
        takeoff_speed = int(input("enter valid takeoff speed:"))
    except ValueError:
        takeoff_speed = 0


ball_xspeed = takeoff_speed * np.cos(np.radians(takeoff_angle))
ball_yspeed = takeoff_speed * np.sin(np.radians(takeoff_angle))
ball_xpos = 0
ball_xArray = [ball_xpos]
ball_ypos = 0
ball_yArray = [ball_ypos]
gravityconst = -9.8

def calculateAccelX(ball_xspeed):
    # air resistance is proportional to the square of the speed
    air_resistance = 0.01 * ball_xspeed**2
    return -air_resistance
def calculateAccelY(ball_yspeed):  
    # air resistance is proportional to the square of the speed
    air_resistance = 0.01 * ball_yspeed**2
    return gravityconst - air_resistance








while(ball_ypos>=0):
        
        # update y velocity with gravity 
        ball_yspeed += gravityconst*0.01
        #const air resistance
        ball_xspeed *= 0.99
        ball_yspeed *= 0.99
        ball_xpos += ball_xspeed*0.01
        ball_ypos += ball_yspeed*0.01
        
        ball_xArray.append(ball_xpos)
        ball_yArray.append(ball_ypos)

plt.plot(ball_xArray, ball_yArray)
plt.xlabel('X Position')
plt.ylabel('Y Position')
plt.savefig('Euler.png')