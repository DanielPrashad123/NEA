from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64

app = Flask(__name__)
# allows JS file to talk to API without security blockages
CORS(app) 

class GolfBallSimulation:
    def constructor(self, mph_speed, takeoff_angle, raw_spin):
        # Global Constants as attributes of the class and are encapsulated within the object once it is instantiated
        self.mass = 0.05 
        self.drag_coefficient = 0.00001 
        self.gravity_const = -9.8
        self.dt = 0.01  
        self.magnus_coefficient = 0.00025  
        self.spin_decay_rate = 0.998 

        # Conversions and initial states
        self.takeoff_speed = mph_speed * 0.44704  
        self.takeoff_spin = raw_spin / 60
        
        self.ball_xspeed = self.takeoff_speed * np.cos(np.radians(takeoff_angle))
        self.ball_yspeed = self.takeoff_speed * np.sin(np.radians(takeoff_angle))
        
        self.ball_xpos = 0
        self.ball_xArray = [self.ball_xpos]
        self.ball_ypos = 0
        self.ball_yArray = [self.ball_ypos]
        self.ball_spin = self.takeoff_spin

    def calculateForceX(self, current_xspeed, current_yspeed, current_spin):
        # this function calculates the rsultant magnus effect and air resistance on the ball in the horizontal direction 
        air_resistance = self.drag_coefficient * current_xspeed * abs(current_xspeed)
        Xmagnus_force = -self.magnus_coefficient * current_yspeed * current_spin   #see 2.2.4 - cycle 4 to learn why taking the ySpeed is usefull for finding the horizontal magnus force.
        #calculated the resultant horizontal force by subtracting the air resistance from the Magnus force
        return -air_resistance + Xmagnus_force

    def calculateForceY(self, current_yspeed, current_xspeed, current_spin):  
        # this function calculates the resultant magnus effect, air resistance and gravity on the ball in the vertical direction
        gravity_force = self.mass * self.gravity_const
        air_resistance = self.drag_coefficient * current_yspeed * abs(current_yspeed)
        Ymagnus_force = self.magnus_coefficient * current_xspeed * current_spin  #see 2.2.4 - cycle 4 to learn why taking the xSpeed is usefull for finding the vertical magnus force.
        #calculated the resultant vertical force by subtracting the air resistance from the magnus force and adding the gravity force
        return gravity_force - air_resistance + Ymagnus_force

    def runRK4(self):
        # THE MAIN RK4 LOOP 
        while self.ball_ypos >= 0:
            # GUESS 1
            k1_currentAccelX = self.calculateForceX(self.ball_xspeed, self.ball_yspeed, self.ball_spin) / self.mass
            k1_currentAccelY = self.calculateForceY(self.ball_yspeed, self.ball_xspeed, self.ball_spin) / self.mass
            
            k1_changeXspeed = k1_currentAccelX * self.dt
            k1_changeYspeed = k1_currentAccelY * self.dt
            k1_changeXpos = self.ball_xspeed * self.dt
            k1_changeYpos = self.ball_yspeed * self.dt

            # GUESS 2
            k2_halfwayXspeed = self.ball_xspeed + (k1_changeXspeed / 2)
            k2_halfwayYspeed = self.ball_yspeed + (k1_changeYspeed / 2)
            k2_halfway_AccelX = self.calculateForceX(k2_halfwayXspeed, k2_halfwayYspeed, self.ball_spin) / self.mass
            k2_halfway_AccelY = self.calculateForceY(k2_halfwayYspeed, k2_halfwayXspeed, self.ball_spin) / self.mass
            
            k2_changeXspeed = k2_halfway_AccelX * self.dt
            k2_changeYspeed = k2_halfway_AccelY * self.dt
            k2_changeXpos = k2_halfwayXspeed * self.dt
            k2_changeYpos = k2_halfwayYspeed * self.dt

            # GUESS 3
            k3_halfwayXspeed = self.ball_xspeed + (k2_changeXspeed / 2)
            k3_halfwayYspeed = self.ball_yspeed + (k2_changeYspeed / 2)
            k3_halfway_AccelX = self.calculateForceX(k3_halfwayXspeed, k3_halfwayYspeed, self.ball_spin) / self.mass
            k3_halfway_AccelY = self.calculateForceY(k3_halfwayYspeed, k3_halfwayXspeed, self.ball_spin) / self.mass
            
            k3_changeXspeed = k3_halfway_AccelX * self.dt
            k3_changeYspeed = k3_halfway_AccelY * self.dt
            k3_changeXpos = k3_halfwayXspeed * self.dt
            k3_changeYpos = k3_halfwayYspeed * self.dt

            # GUESS 4
            k4_endXspeed = self.ball_xspeed + k3_changeXspeed
            k4_endYspeed = self.ball_yspeed + k3_changeYspeed
            k4_end_AccelX = self.calculateForceX(k4_endXspeed, k4_endYspeed, self.ball_spin) / self.mass
            k4_end_AccelY = self.calculateForceY(k4_endYspeed, k4_endXspeed, self.ball_spin) / self.mass
            
            k4_changeXspeed = k4_end_AccelX * self.dt
            k4_changeYspeed = k4_end_AccelY * self.dt
            k4_changeXpos = k4_endXspeed * self.dt
            k4_changeYpos = k4_endYspeed * self.dt

            # FINAL STEP
            self.ball_xspeed += (k1_changeXspeed + 2*k2_changeXspeed + 2*k3_changeXspeed + k4_changeXspeed) / 6
            self.ball_yspeed += (k1_changeYspeed + 2*k2_changeYspeed + 2*k3_changeYspeed + k4_changeYspeed) / 6
            self.ball_xpos += (k1_changeXpos + 2*k2_changeXpos + 2*k3_changeXpos + k4_changeXpos) / 6
            self.ball_ypos += (k1_changeYpos + 2*k2_changeYpos + 2*k3_changeYpos + k4_changeYpos) / 6
            
            self.ball_xArray.append(self.ball_xpos)
            self.ball_yArray.append(self.ball_ypos)
            self.ball_spin *= self.spin_decay_rate

    def get_apex(self):
        return max(self.ball_yArray)

    def get_distance(self):
        return (self.ball_xArray[-1] + self.ball_xArray[-2]) / 2

    def generate_plot(self):
        fig, ax = plt.subplots(figsize=(8, 4.5))
        ax.plot(self.ball_xArray, self.ball_yArray, color='blue', linewidth=2)
        ax.set_title('Golf Ball Trajectory')
        ax.set_xlabel('Horizontal Distance (m)')
        ax.set_ylabel('Height (m)')
        ax.grid(True, linestyle='--', alpha=0.4)
        plt.tight_layout()
        
        buffer = io.BytesIO()
        fig.savefig(buffer, format='png')
        plt.close(fig)
        buffer.seek(0)
        return base64.b64encode(buffer.getvalue()).decode('ascii')


@app.route('/projection', methods=['POST'])
def projection_numbers():
    # Receive the JSON data sent by JavaScript
    incoming_data = request.get_json()
    
    # Type validation
    try:
        mph_speed = float(incoming_data['speed'])
        takeoff_angle = float(incoming_data['angle'])
        raw_spin = float(incoming_data['spin'])
    except (ValueError, TypeError, KeyError):
        return jsonify({
            'error': 'Invalid input type. Please ensure speed, angle, and spin are numeric values.'
        }), 400

    # Boundary validation
    if takeoff_angle < 0 or takeoff_angle > 90:
        return jsonify({'error': 'Invalid angle. Please provide an angle between 0 and 90 degrees.'}), 400
    if mph_speed < 0:
        return jsonify({'error': 'Invalid speed. Please provide a non-negative speed.'}), 400

    # Execute simulation
    trajectorysim = GolfBallSimulation(mph_speed, takeoff_angle, raw_spin)
    trajectorysim.runRK4()

    # Generate feedback
    angleFeedback = []
    if takeoff_angle > 15:
        angleFeedback.append("The launch angle is too high, consider lowering it for more distance.")
    elif takeoff_angle < 10:
        angleFeedback.append("The launch angle is too low, consider increasing it for more distance.")
    else:
        angleFeedback.append("The launch angle is good for distance.")

    spinFeedback = []
    if raw_spin > 3000:
        spinFeedback.append("The spin rate is too high, consider lowering it for more distance.")
    elif raw_spin < 1800:
        spinFeedback.append("The spin rate is too low, consider increasing it for more distance.")
    else:
        spinFeedback.append("The spin rate is good for distance.")

    # Send the result back via JSON
    return jsonify({
        'trajectory_png': trajectorysim.generate_plot(),
        'apex': round(trajectorysim.get_apex(), 2),
        'distance': round(trajectorysim.get_distance(), 2),
        'angleFeedback': " ".join(angleFeedback),
        'spinFeedback': " ".join(spinFeedback)
    })

if __name__ == '__main__':
    # Run the server on port 5000
    app.run(port=5000)