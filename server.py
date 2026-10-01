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

class Golf_ball_simulation:

    """Models the aerodynamic flight path of a golf ball
    this class acts as a physical engine using a 4th order Runge-kutta numerical method
    to simulat trajectory by calculating all the force on the ball 
    at discrete time steps and updating the opisition accordingly. 
    """

    def __init__(self, mph_speed, takeoff_angle, raw_spin):

        """initialized the golf ball object with the given speed, angle,
        and spin rate. it also sets up the initial conditions for global constants, converstions,
        and initial states.
        arguments : speed (mph), takeoff_angle (degrees), raw_spin (rpm)
    
        """
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
        self.ball_x_array = [self.ball_xpos]
        self.ball_ypos = 0
        self.ball_y_array = [self.ball_ypos]
        self.ball_spin = self.takeoff_spin

    def calculate_force_x(self, current_xspeed, current_yspeed, current_spin):
        """this function calculates the rsultant magnus effect and air resistance 
        on the ball in the horizontal direction.
        it uses the current y-speed to determine the perpendicular magnus force, and subtracts
        the opposing aerodynamic drag force which is caluclated from the current x-speed.
        arguments :
            current_xspeed (float): the current horizontal speed of the ball
            current_yspeed (float): the current vertical speed of the ball
            current_spin (float): the current spin rate of the ball
        returns:
            float: the resultant horizontal force acting on the ball
        """

        air_resistance = self.drag_coefficient * current_xspeed * abs(current_xspeed)
        Xmagnus_force = -self.magnus_coefficient * current_yspeed * current_spin   #see 2.2.4 - cycle 4 to learn why taking the ySpeed is usefull for finding the horizontal magnus force.
        
        return -air_resistance + Xmagnus_force

    def calculate_force_y(self, current_yspeed, current_xspeed, current_spin):  
        """this function calculates the rsultant magnus effect, air resistance, and gravity
        on the ball in the vertical direction.
        it uses the current x-speed to determine the perpendicular magnus force, and subtracts
        the opposing aerodynamic drag force which is caluclated from the current y-speed.
        arguments :
            current_yspeed (float): the current vertical speed of the ball
            current_xspeed (float): the current horizontal speed of the ball
            current_spin (float): the current spin rate of the ball
        returns:
            float: the resultant vertical force acting on the ball
        """

        gravity_force = self.mass * self.gravity_const
        air_resistance = self.drag_coefficient * current_yspeed * abs(current_yspeed)
        Ymagnus_force = self.magnus_coefficient * current_xspeed * current_spin  #see 2.2.4 - cycle 4 to learn why taking the xSpeed is usefull for finding the vertical magnus force.
        
        return gravity_force - air_resistance + Ymagnus_force

    def run_RK4(self):
        """this function implements the 4th order Runge-Kutta numerical methods to simulate the trajectory of the golf ball.
        it uses the current position, its speed, and the magnus functions above to calculate the next position of the ball 
        in discrete time steps untill the ball hits the ground (ypos<0).
        
        it does this process by calculating 4 "guesses" of the next position , and then taking a weighted average of those guesses to 
        determine the final position of the ball at the next time step. each time step is a small increment of time (dt) which is set to 0.1 seconds.
        
        other processes of this function :
            it updates the ball's spin rate at the end of every time step by multiplying it by a decay rate since real golf balls lose spin over their flight.
            it appends the new position of the ball at the end of every time step to the ball_xArray and ball_yArray which are used to plot the trajectory of the ball at the end of the simulation.
        
            
        to see the maths and greater explination behind the 4th order Runge-Kutta method, see 2.2.4 - cycle 4 in the course material.
        """
        while self.ball_ypos >= 0:
            # GUESS 1
            k1_currentAccelX = self.calculate_force_x(self.ball_xspeed, self.ball_yspeed, self.ball_spin) / self.mass
            k1_currentAccelY = self.calculate_force_y(self.ball_yspeed, self.ball_xspeed, self.ball_spin) / self.mass
            
            k1_changeXspeed = k1_currentAccelX * self.dt
            k1_changeYspeed = k1_currentAccelY * self.dt
            k1_changeXpos = self.ball_xspeed * self.dt
            k1_changeYpos = self.ball_yspeed * self.dt

            # GUESS 2
            k2_halfwayXspeed = self.ball_xspeed + (k1_changeXspeed / 2)
            k2_halfwayYspeed = self.ball_yspeed + (k1_changeYspeed / 2)
            k2_halfway_AccelX = self.calculate_force_x(k2_halfwayXspeed, k2_halfwayYspeed, self.ball_spin) / self.mass
            k2_halfway_AccelY = self.calculate_force_y(k2_halfwayYspeed, k2_halfwayXspeed, self.ball_spin) / self.mass
            
            k2_changeXspeed = k2_halfway_AccelX * self.dt
            k2_changeYspeed = k2_halfway_AccelY * self.dt
            k2_changeXpos = k2_halfwayXspeed * self.dt
            k2_changeYpos = k2_halfwayYspeed * self.dt

            # GUESS 3
            k3_halfwayXspeed = self.ball_xspeed + (k2_changeXspeed / 2)
            k3_halfwayYspeed = self.ball_yspeed + (k2_changeYspeed / 2)
            k3_halfway_AccelX = self.calculate_force_x(k3_halfwayXspeed, k3_halfwayYspeed, self.ball_spin) / self.mass
            k3_halfway_AccelY = self.calculate_force_y(k3_halfwayYspeed, k3_halfwayXspeed, self.ball_spin) / self.mass
            
            k3_changeXspeed = k3_halfway_AccelX * self.dt
            k3_changeYspeed = k3_halfway_AccelY * self.dt
            k3_changeXpos = k3_halfwayXspeed * self.dt
            k3_changeYpos = k3_halfwayYspeed * self.dt

            # GUESS 4
            k4_endXspeed = self.ball_xspeed + k3_changeXspeed
            k4_endYspeed = self.ball_yspeed + k3_changeYspeed
            k4_end_AccelX = self.calculate_force_x(k4_endXspeed, k4_endYspeed, self.ball_spin) / self.mass
            k4_end_AccelY = self.calculate_force_y(k4_endYspeed, k4_endXspeed, self.ball_spin) / self.mass
            
            k4_changeXspeed = k4_end_AccelX * self.dt
            k4_changeYspeed = k4_end_AccelY * self.dt
            k4_changeXpos = k4_endXspeed * self.dt
            k4_changeYpos = k4_endYspeed * self.dt

            # FINAL STEP
            self.ball_xspeed += (k1_changeXspeed + 2*k2_changeXspeed + 2*k3_changeXspeed + k4_changeXspeed) / 6
            self.ball_yspeed += (k1_changeYspeed + 2*k2_changeYspeed + 2*k3_changeYspeed + k4_changeYspeed) / 6
            self.ball_xpos += (k1_changeXpos + 2*k2_changeXpos + 2*k3_changeXpos + k4_changeXpos) / 6
            self.ball_ypos += (k1_changeYpos + 2*k2_changeYpos + 2*k3_changeYpos + k4_changeYpos) / 6

            # append the new positon of the ball to the arrays for plotting later. 
            self.ball_x_array.append(self.ball_xpos)
            self.ball_y_array.append(self.ball_ypos)

            # update spin rate to simualate spin decay over time.
            self.ball_spin *= self.spin_decay_rate

    def get_apex(self):
        """returns the maximum height of the ball during its flight by finding the largest value in the ball_yArray.
        """
        return max(self.ball_y_array)

    def get_distance(self):
        """returns the horizontal distance of the ball when it hits the ground by taking the average of the last two values in the ball_xArray.
        
        see 2.2.7 -cycle 7 (post development thoughts to see how this coule be improved upon)
        """
        return (self.ball_x_array[-1] + self.ball_x_array[-2]) / 2

    def generate_plot(self):
        """generates a plot of the ball's trajectory using matplotlib and returns it as a base64 encoded PNG image.
        """
        fig, ax = plt.subplots(figsize=(8, 4.5))
        ax.plot(self.ball_x_array, self.ball_y_array, color='blue', linewidth=2)
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
    trajectory_sim = Golf_ball_simulation(mph_speed, takeoff_angle, raw_spin)
    trajectory_sim.run_RK4()

    # Generate feedback
    angle_Feedback = []
    if takeoff_angle > 15:
        angle_Feedback.append("The launch angle is too high, consider lowering it for more distance.")
    elif takeoff_angle < 10:
        angle_Feedback.append("The launch angle is too low, consider increasing it for more distance.")
    else:
        angle_Feedback.append("The launch angle is good for distance.")

    spin_Feedback = []
    if raw_spin > 3000:
        spin_Feedback.append("The spin rate is too high, consider lowering it for more distance.")
    elif raw_spin < 1800:
        spin_Feedback.append("The spin rate is too low, consider increasing it for more distance.")
    else:
        spin_Feedback.append("The spin rate is good for distance.")

    # Send the result back via JSON
    return jsonify({
        'trajectory_png': trajectory_sim.generate_plot(),
        'apex': round(trajectory_sim.get_apex(), 2),
        'distance': round(trajectory_sim.get_distance(), 2),
        'angleFeedback': " ".join(angle_Feedback),
        'spinFeedback': " ".join(spin_Feedback)
    })

if __name__ == '__main__':
    # Run the server on port 5000
    app.run(port=5000)