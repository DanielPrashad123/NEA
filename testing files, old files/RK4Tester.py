import matplotlib.pyplot as plt
import numpy as np

# testing values
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

# Added mass and drag variables to fix the Force vs Acceleration errors
mass = 0.05 
drag_coefficient = 0.00001 

dt = 0.01  #time step (10 milliseconds)

# accellerate functions to reduce repeated code in the main loop 
def calculateForceX(current_xspeed):
    # calculates forces on the ball, in the x direction there will only be one force
    # abs() is used to take into consideration the direction of speed so air resistance opposes motion
    air_resistance = drag_coefficient * current_xspeed * abs(current_xspeed)
    return -air_resistance

def calculateForceY(current_yspeed):  
    # calculates forces on the ball, in the y direction there will be two forces
    # FIX: Gravity is an acceleration, so Force = Mass * Gravity
    gravity_force = mass * gravityconst
    # abs() is used to take into consideration the direction of speed so air resistance opposes motion
    air_resistance = drag_coefficient * current_yspeed * abs(current_yspeed)
    return gravity_force - air_resistance

# THE MAIN RK4 LOOP 
# All k-steps must be inside the loop so they recalculate every time step (dt)
while ball_ypos >= 0:
    
    
    # GUESS 1 K1, exactly what is happening at start of time step
    # this will calculate the entire time step (0.01), basically just one Euler loop. 
    k1_currentAccelX = calculateForceX(ball_xspeed)/mass
    k1_currentAccelY = calculateForceY(ball_yspeed)/mass
    
    k1_changeXspeed = k1_currentAccelX * dt
    k1_changeYspeed = k1_currentAccelY * dt
    k1_changeXpos = ball_xspeed * dt
    k1_changeYpos = ball_yspeed * dt

    
    # GUESS 2 K2, the halfway prediction using K1
    
    # predict the speed at the halfway point using original speed and half of change in speed from k1
    k2_halfwayXspeed = ball_xspeed + (k1_changeXspeed / 2)
    k2_halfwayYspeed = ball_yspeed + (k1_changeYspeed / 2)
    
    # calculate forces at that halfway speed
    k2_halfway_AccelX = calculateForceX(k2_halfwayXspeed)/mass
    k2_halfway_AccelY = calculateForceY(k2_halfwayYspeed)/mass
    
    # calculate changes
    k2_changeXspeed = k2_halfway_AccelX * dt
    k2_changeYspeed = k2_halfway_AccelY * dt
    k2_changeXpos = k2_halfwayXspeed * dt
    k2_changeYpos = k2_halfwayYspeed * dt

    
    # GUESS 3 (K3): the refined halfway prediction using K2
  
    #  predict the speed at the halfway point again but using the better K2 data
    k3_halfwayXspeed = ball_xspeed + (k2_changeXspeed / 2)
    k3_halfwayYspeed = ball_yspeed + (k2_changeYspeed / 2)
    
    #  calculate forces at this refined halfway speed
    k3_halfway_AccelX = calculateForceX(k3_halfwayXspeed)/mass
    k3_halfway_AccelY = calculateForceY(k3_halfwayYspeed)/mass
    
    #  calculate changes
    k3_changeXspeed = k3_halfway_AccelX * dt
    k3_changeYspeed = k3_halfway_AccelY * dt
    k3_changeXpos = k3_halfwayXspeed * dt
    k3_changeYpos = k3_halfwayYspeed * dt

    

    # GUESS 4 K4, The finish prediction using K3
    
    #  predict the speed at the very END of the time-step using K3 data
    k4_endXspeed = ball_xspeed + k3_changeXspeed
    k4_endYspeed = ball_yspeed + k3_changeYspeed
    
    #  calculate forces at the finish line
    k4_end_AccelX = calculateForceX(k4_endXspeed)/mass
    k4_end_AccelY = calculateForceY(k4_endYspeed)/mass
    
    #  calculate changes
    k4_changeXspeed = k4_end_AccelX * dt
    k4_changeYspeed = k4_end_AccelY * dt
    k4_changeXpos = k4_endXspeed * dt
    k4_changeYpos = k4_endYspeed * dt

   
    # FINAL STEP, The average
   
    # combine the four guesses using the formula, giving double weight to k2 and k3 
    ball_xspeed += (k1_changeXspeed + 2*k2_changeXspeed + 2*k3_changeXspeed + k4_changeXspeed) / 6
    ball_yspeed += (k1_changeYspeed + 2*k2_changeYspeed + 2*k3_changeYspeed + k4_changeYspeed) / 6
    
    ball_xpos += (k1_changeXpos + 2*k2_changeXpos + 2*k3_changeXpos + k4_changeXpos) / 6
    ball_ypos += (k1_changeYpos + 2*k2_changeYpos + 2*k3_changeYpos + k4_changeYpos) / 6
    
    # record the new coordinates for graphing
    ball_xArray.append(ball_xpos)
    ball_yArray.append(ball_ypos)




plt.plot(ball_xArray, ball_yArray)
plt.xlabel('X Position')
plt.ylabel('Y Position')
plt.savefig('RK4.png')
