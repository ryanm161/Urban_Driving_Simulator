import numpy as np

class Action(object):
    def get_action(self):
        raise NotImplementedError

    def get_array(self):
        raise NotImplementedError
class KeyboardAction(Action):
    """
    This action passes control to keyboard input
    """
    pass

class SteeringVelAction(Action):
    """
    This action provides steering and velocity control

    Parameters
    ----------
    steer: float in range (-1, 1)
    vel: float in range (0, 1)
    """
    def __init__(self, steer, vel):
        self.steer = steer
        self.vel = vel
    def get_action(self):
        return self.steer, self.vel
    def get_array(self):
        return np.array([self.steer, self.vel])

class WaypointVelAction(Action):
    """
    This action provides waypoint and velocity control

    Parameters
    ----------
<<<<<<< HEAD
    waypoint: tuple of (x, y, angle, distance) all relative to car
=======
    waypoint: tuple of (x, y, angle)
>>>>>>> 7052fce75670c2eef64ce3b70a935ca7c18c0e04
    vel: float in range (0, 1)
    """
    def __init__(self, waypoint, vel):
        self.waypoint = waypoint
        self.vel = vel
    def get_action(self):
        return self.waypoint, self.vel
    def get_array(self):
        return np.array([self.waypoint[0], self.waypoint[1], self.waypoint[2], self.waypoint[3], self.vel])

class SteeringAccAction(Action):
    """
    This action provides both steering and acceleration control.

    Parameters
    ----------
    steer: float in range (-1, 1)
    acc: float in range (-1, 1)
    """

    def __init__(self, steer, acc):
        self.steer = steer
        self.acc = acc
    def get_action(self):
        return self.steer, self.acc
    def get_array(self):
        return np.array([self.steer, self.acc])

    def asSteeringAction(self):
        return SteeringAction(self.steer)

class SteeringAction(Action):
    """
    This action provides a steering control. The supervisor will control the acceleration
    
    Parameters
    ----------
    steer: float in range (-1, 1)
    """
    def __init__(self, steer):
        self.steer = steer
    def get_action(self):
        return self.steer
    def get_array(self):
        return np.array([self.steer])

class VelocityAction(Action):
    """
    This action provides a target velocity for the car to track

    Parameters
    ----------
    vel: float in range (0, 1)
    """
    def __init__(self, vel):
        self.vel = vel
    def get_action(self):
        return self.vel
    def get_array(self):
        return np.array([self.vel])

    

class LastValidAction(Action):
    """
    This action causes car to replay its last valid action.
    This is useful when testing coarse planning methods.
    """
    def __init__(self):
        pass
