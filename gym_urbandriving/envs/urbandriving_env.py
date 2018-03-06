import gym
from copy import deepcopy
from gym_urbandriving.agents import *
import numpy as np
import ray

@ray.remote
class RayNode:
    def __init__(self, agent_type, agent_num):
        self.agent = agent_type(agent_num)

    def eval_policy(self, state):
        return self.agent.eval_policy(state)

class UrbanDrivingEnv(gym.Env):
    """
    This class controls the evolution of a world state.
    While the :class:`PositionState` represents the layout of objects in the scene,
    the :class:`UrbanDrivingEnv` controls the evolution of the scene, and manages background
    actors.

    Note
    -----
        This class is used both to represent the true, global state of the world, and
        as a search agent's internal view of the world.

    Parameters
    ----------
    init_state : PositionState
        The starting state for this environment
    visualizer :
        A visualizer object, if provided, which this env will use to display the scene
    reward_fn :
        A function which takes in one parameter, the :class:`PositionState`,
        and returns the reward for the 0th controllable object in that scene
    max_time : int
        If set > 1, the environment will return "done" after this many ticks
    randomize : bool
        Sets whether :func:`env._reset()` returns the environment to the initial state,
        or if it returns it to a random state generated by the state's :func:`randomize()`
        function
    use_ray : bool
        Sets whether we parallelize agent planning using Ray
    agent_mappings : dict
        Specify the types of agents this environment will use to control background objects
    """
    metadata = {'render.modes': ['human']}

    def __init__(self,
                 init_state,
                 visualizer=None,
                 reward_fn=lambda x: 0,
                 max_time=500,
                 randomize=False,
                 use_ray=False,
                 agent_mappings={}):
        self.visualizer = visualizer
        self.reward_fn = reward_fn
        self.init_state = deepcopy(init_state)
        self.agent_mappings = agent_mappings
        self.max_time = max_time
        self.randomize = randomize
        self.statics_rendered = False
        self.use_ray = use_ray
        if use_ray:
            ray.init()
        self.dynamic_collisions, self.static_collisions, self.last_col = [], [], -1
        if (self.init_state):
            self._reset()

    def _step_test(self, car_actions, agentnum=0):
        assert(self.current_state is not None)
        # Get actions for all objects
        actions = [None]*len(self.current_state.dynamic_objects)
        
        
        assert(all([type(bgagent) != RayNode for i, bgagent in self.bg_agents.items()]))
        
        for i in range(len(car_actions)):
            actions[i] = car_actions[i]
        for i, dobj in enumerate(self.current_state.dynamic_objects):
            dobj.step(actions[i])

        self.current_state.time += 1
        dynamic_coll, static_coll = self.current_state.get_collisions()
        state = self.current_state
        reward = self.reward_fn(self.current_state)
        done = (self.current_state.time == self.max_time) or len(dynamic_coll) or len(static_coll)

        info_dict = {"saved_actions": actions, "static_coll" : static_coll, "dynamic_coll" : dynamic_coll}

        return state, reward, done, info_dict


    def _step(self, action, agentnum=0):
        """
        The step function accepts a control for the 0th agent in the scene. Then, it queries
        all the background agents to determine their actions. Then, it updates the scene
        and returns.
        
        Parameters
        ----------
        action :
            An action for the agentnum object in the scene.
        agentnum : int
            The index for the object which the action is applied for.

        Returns
        -------
        PositionState
            State of the world after this step;
        float
            Reward calculated by :func:`self.reward_fn`,
        bool
            Whether we have timed out, or there is a collision)
        dict

        """
        assert(self.current_state is not None)
        # Get actions for all objects
        actions = [None]*len(self.current_state.dynamic_objects)
        actions[agentnum] = action
     

        if self.use_ray:
            assert(all([type(bgagent) == RayNode for i, bgagent in self.bg_agents.items()]))
            stateid = ray.put(self.current_state)
            actionids = {}
            for i, agent in self.bg_agents.items():
                if i is not agentnum:
                    actionids[i] = agent.eval_policy.remote(stateid)
            for i, aid in actionids.items():
                action = ray.get(aid)
                actions[i] = action
        else:
            assert(all([type(bgagent) != RayNode for i, bgagent in self.bg_agents.items()]))
            for i, agent in self.bg_agents.items():
                if i is not agentnum:
                    actions[i] = agent.eval_policy(self.current_state)
        for i, dobj in enumerate(self.current_state.dynamic_objects):
            dobj.step(actions[i])

        self.current_state.time += 1
        dynamic_coll, static_coll = self.current_state.get_collisions()
        state = self.current_state
        reward = self.reward_fn(self.current_state)
        done = (self.current_state.time == self.max_time) or len(dynamic_coll) or len(static_coll)

        info_dict = {"saved_actions": actions}

        return state, reward, done, info_dict


    def _reset(self, new_state=None):
        """
        Resets the environment to its initial state, or a new state
        
        Parameters
        ----------
        new_state : PositionState
            If specified, the environment will reset to this state
        """
        self.last_col = -1
        if new_state:
            self.init_state = new_state
            self.statics_rendered = False
        if self.randomize:
            self.init_state.randomize()
        self.current_state = deepcopy(self.init_state)

        self.bg_agents = {}
        for i, obj in enumerate(self.current_state.dynamic_objects):
            if type(obj) in self.agent_mappings:
                if self.use_ray:
                    self.bg_agents[i] = RayNode.remote(self.agent_mappings[type(obj)], i)
                else:
                    self.bg_agents[i] = self.agent_mappings[type(obj)](i)

        return

    def _render(self, mode='human', close=False, waypoints=[]):
        """
        If the renderer was specifed at construction, renders the current state of the world
        
        Parameters
        ----------
        mode : str
            For OpenAI Gym compatibility
        waypoints :
            Extra points you would like to render over top of the the scene, for debugging
        """
        if close:
            return
        if self.visualizer:
            window = [0, self.current_state.dimensions[0],
                      0, self.current_state.dimensions[1]]
            self.visualizer.render(self.current_state, window,
                                   rerender_statics=not self.statics_rendered,
                                   waypoints=waypoints)
            self.statics_rendered = True

    def get_state_copy(self):
        return deepcopy(self.current_state)
