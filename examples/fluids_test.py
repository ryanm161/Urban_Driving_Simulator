import fluids
import pygame
import numpy as np

simulator = fluids.FluidSim(visualization_level=1,        # How much debug visualization you want to enable. Set to 0 for no vis
                            background_cars=10,           # How many background cars
                            controlled_cars=1,            # How many cars to control. Set to 0 for background cars only
                            fps=0,                        # If set to non 0, caps the FPS. Target is 30
                            obs_space=fluids.OBS_BIRDSEYE,# OBS_BIRDSEYE, OBS_GRID, or OBS_NONE
                            background_control=fluids.BACKGROUND_CSP) # BACKGROUND_CSP or BACKGROUND_NULL

controlled_keys = simulator.get_control_keys()

while True:
    actions = {}

    # Uncomment any of these lines.
    # VelocityAction is vel for car to move along trajectory
    # SteeringAction is steer, acc control
    # KeyboardAction is use keyboard input

#    actions = {k:fluids.VelocityAction(1) for k in controlled_keys}
#    actions = {k:fluids.SteeringAction(0, 1) for k in controlled_keys}
#    actions = {k:fluids.KeyboardAction() for k in controlled_keys}
    rew = simulator.step(actions)
    obs = simulator.get_observations(controlled_keys)
    simulator.render()
