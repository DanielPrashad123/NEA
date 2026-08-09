from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64

app = Flask(__name__)
# This allows your JS file to talk to the Flask API without security blockages
CORS(app) 


# Global Constants
mass = 0.05 
drag_coefficient = 0.00001 
gravityconst = -9.8
dt = 0.01  # time step (10 milliseconds)
magnus_coefficient = 0.00025  # Magnus effect coefficient
spinDecayRate = 0.998 # decreases the spin rate by 0.2% 



@app.route('/projection', methods=['POST'])
def projection_numbers():
    

    # Receive the JSON data sent by the JavaScript client
    incoming_data = request.get_json()
    


    # define starting values for golf ball using data from frontend
    mph_speed = incoming_data['speed']
    takeoff_speed = mph_speed * 0.44704  # convert mph to m/s
    takeoff_angle = incoming_data['angle']
    takeoff_spin = incoming_data['spin']/60
    ball_xspeed = takeoff_speed * np.cos(np.radians(takeoff_angle))
    ball_yspeed = takeoff_speed * np.sin(np.radians(takeoff_angle))
    ball_xpos = 0
    ball_xArray = [ball_xpos]
    ball_ypos = 0
    ball_yArray = [ball_ypos]
    ball_spin = takeoff_spin
    
    # accellerate functions to reduce repeated code in the main loop 
    def calculateForceX(current_xspeed, current_yspeed,current_spin):
        # calculates forces on the ball, in the x direction there will only be one force
        
        # abs() is used to take into consideration the direction of speed so air resistance opposes motion
        air_resistance = drag_coefficient * current_xspeed * abs(current_xspeed)
        
        # magnus force calculation using Yspeed
        Xmagnus_force = -magnus_coefficient * current_yspeed * current_spin
        
        return -air_resistance + Xmagnus_force

    def calculateForceY(current_yspeed, current_xspeed, current_spin):  
        
        # calculates forces on the ball, in the y direction there will be two forces
        # FIX: Gravity is an acceleration, so Force = Mass * Gravity
        gravity_force = mass * gravityconst
        
        # abs() is used to take into consideration the direction of speed so air resistance opposes motion
        air_resistance = drag_coefficient * current_yspeed * abs(current_yspeed)
        
        # magnus force calculation using Xspeed
        Ymagnus_force = magnus_coefficient * current_xspeed * current_spin
        
        return gravity_force - air_resistance + Ymagnus_force

    # THE MAIN RK4 LOOP 
    while ball_ypos >= 0:
        
        # GUESS 1 K1, exactly what is happening at start of time step
        # this will calculate the entire time step (0.01), basically just one Euler loop. 
        k1_currentAccelX = calculateForceX(ball_xspeed,ball_yspeed,ball_spin)/mass
        k1_currentAccelY = calculateForceY(ball_yspeed,ball_xspeed,ball_spin)/mass
        
        k1_changeXspeed = k1_currentAccelX * dt
        k1_changeYspeed = k1_currentAccelY * dt
        k1_changeXpos = ball_xspeed * dt
        k1_changeYpos = ball_yspeed * dt

        # GUESS 2 K2, the halfway prediction using K1
        k2_halfwayXspeed = ball_xspeed + (k1_changeXspeed / 2)
        k2_halfwayYspeed = ball_yspeed + (k1_changeYspeed / 2)
        
        # calculate forces at that halfway speed
        k2_halfway_AccelX = calculateForceX(k2_halfwayXspeed,k2_halfwayYspeed,ball_spin)/mass
        k2_halfway_AccelY = calculateForceY(k2_halfwayYspeed,k2_halfwayXspeed,ball_spin)/mass
        
        # calculate changes
        k2_changeXspeed = k2_halfway_AccelX * dt
        k2_changeYspeed = k2_halfway_AccelY * dt
        k2_changeXpos = k2_halfwayXspeed * dt
        k2_changeYpos = k2_halfwayYspeed * dt

        # GUESS 3 (K3): the refined halfway prediction using K2
        k3_halfwayXspeed = ball_xspeed + (k2_changeXspeed / 2)
        k3_halfwayYspeed = ball_yspeed + (k2_changeYspeed / 2)
        
        #  calculate forces at this refined halfway speed
        k3_halfway_AccelX = calculateForceX(k3_halfwayXspeed,k3_halfwayYspeed,ball_spin)/mass
        k3_halfway_AccelY = calculateForceY(k3_halfwayYspeed,k3_halfwayXspeed,ball_spin)/mass
        
        #  calculate changes
        k3_changeXspeed = k3_halfway_AccelX * dt
        k3_changeYspeed = k3_halfway_AccelY * dt
        k3_changeXpos = k3_halfwayXspeed * dt
        k3_changeYpos = k3_halfwayYspeed * dt

        # GUESS 4 K4, The finish prediction using K3
        k4_endXspeed = ball_xspeed + k3_changeXspeed
        k4_endYspeed = ball_yspeed + k3_changeYspeed
        
        #  calculate forces at the finish line
        k4_end_AccelX = calculateForceX(k4_endXspeed,k4_endYspeed,ball_spin)/mass
        k4_end_AccelY = calculateForceY(k4_endYspeed,k4_endXspeed,ball_spin)/mass
        
        #  calculate changes
        k4_changeXspeed = k4_end_AccelX * dt
        k4_changeYspeed = k4_end_AccelY * dt
        k4_changeXpos = k4_endXspeed * dt
        k4_changeYpos = k4_endYspeed * dt

        # FINAL STEP, The average
        ball_xspeed += (k1_changeXspeed + 2*k2_changeXspeed + 2*k3_changeXspeed + k4_changeXspeed) / 6
        ball_yspeed += (k1_changeYspeed + 2*k2_changeYspeed + 2*k3_changeYspeed + k4_changeYspeed) / 6
        
        ball_xpos += (k1_changeXpos + 2*k2_changeXpos + 2*k3_changeXpos + k4_changeXpos) / 6
        ball_ypos += (k1_changeYpos + 2*k2_changeYpos + 2*k3_changeYpos + k4_changeYpos) / 6
        
        # record the new coordinates for graphing
        ball_xArray.append(ball_xpos)
        ball_yArray.append(ball_ypos)
        ball_spin *= spinDecayRate  # apply spin decay for the next RK4 loop
    
    # RK4 CALCULATIONS COMPLETE 


    #variables for summary page
    apexHeight= max(ball_yArray)
    totaldistance=(ball_xArray[-1]+ball_xArray[-2])/2

    angleFeedback=[]
    if takeoff_angle>15:
        angleFeedback.append("The launch angle is too high, consider lowering it for more distance.")
    elif takeoff_angle<10:
        angleFeedback.append("The launch angle is too low, consider increasing it for more distance.")
    else:
        angleFeedback.append("The launch angle is good for distance.")

    spinFeedback=[]
    rawSpin=incoming_data['spin']
    if rawSpin>3000:
        spinFeedback.append("The spin rate is too high, consider lowering it for more distance.")
    elif rawSpin<1800:
        spinFeedback.append("The spin rate is too low, consider increasing it for more distance.")
    else:
        spinFeedback.append("The spin rate is good for distance.")

    angleFeedbackString=" ".join(angleFeedback)
    spinFeedbackString=" ".join(spinFeedback)


    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.plot(ball_xArray, ball_yArray, color='blue', linewidth=2)
    ax.set_title('Golf Ball Trajectory')
    ax.set_xlabel('Horizontal Distance (m)')
    ax.set_ylabel('Height (m)')
    ax.grid(True, linestyle='--', alpha=0.4)
    plt.tight_layout()
    buffer = io.BytesIO()
    fig.savefig(buffer, format='png')
    plt.close(fig)
    buffer.seek(0)
    image_trajectory = base64.b64encode(buffer.getvalue()).decode('ascii')

    # Send the result back via JSON
    return jsonify({
        'trajectory_png': image_trajectory,
        'apex': round(apexHeight, 2),
        'totaldistance': round(totaldistance, 2),
        'angleFeedback': angleFeedbackString,
        'spinFeedback': spinFeedbackString
    })

if __name__ == '__main__':
    # Run the server on port 5000
    app.run(port=5000)


    