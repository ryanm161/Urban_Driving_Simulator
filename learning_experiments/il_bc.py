import gym
import gym_urbandriving as uds
import cProfile
import time
import numpy as np
import numpy.linalg as LA

from gym_urbandriving.learner.trainer import Trainer
from gym_urbandriving.learner.plotter import Plotter

###A script to test behavior cloning 

##PARAMTERS FOR THE EXPERIMENT
NUM_DATA_PER_ITER = 2 #NUMBER OF TRAJECTORIES TO SAMPLE FROM THE SUPERVISOR 
NUM_EVAL_POINTS = 1 #NUMBER OF TRAJECTORIES TO SAMPLE FROM THE LEANRED POLICY (i.e. for Evaluation) 
NUM_ITERS = 2 #NNumber of iterations 
TIME_HORIZON = 100 #Time horizon for the learned policy
PLANNING_TIME = 3 #planning time limit for the supervisor 

#Path to save data

FILE_PATH = 'test_data/'

#Specifc experiment 
ALG_NAME = 'B_C'
FILE_PATH_ALG =  FILE_PATH + ALG_NAME 

#Trainer class
t_exp = Trainer(FILE_PATH_ALG,
                num_data_points = NUM_DATA_PER_ITER, 
                num_eval_points = NUM_EVAL_POINTS,
                time_horizon = TIME_HORIZON,
                time = PLANNING_TIME)

#Plotter class
plotter = Plotter(FILE_PATH_ALG)
stats = []


for i in range(NUM_ITERS):
	#Collect demonstrations 
    t_exp.collect_supervisor_rollouts()
    #update model 
    t_exp.train_model()
    #Evaluate Policy 
    stats.append(t_exp.get_stats())

#Save plots
plotter.save_plots(stats)












