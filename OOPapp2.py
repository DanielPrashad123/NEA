class GolfBallSimulation:
    def constructor(self, mph_speed, takeoff_angle, raw_spin):
        self.mass = 0.05 
        self.drag_coefficient = 0.00001 
        self.gravity_const = -9.8
        self.dt = 0.01  
        self.magnus_coefficient = 0.00025  
        self.spin_decay_rate = 0.998 
        
        self.takeoff_speed = mph_speed * 0.44704  
        self.takeoff_spin = raw_spin / 60
                
        self.ball_xspeed = self.takeoff_speed * np.cos(np.radians(takeoff_angle))
        self.ball_yspeed = self.takeoff_speed * np.sin(np.radians(takeoff_angle))
                
        self.ball_xpos = 0
        self.ball_xArray = [self.ball_xpos]
        self.ball_ypos = 0
        self.ball_yArray = [self.ball_ypos]
        self.ball_spin = self.takeoff_spin