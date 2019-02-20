import random
from environment import Agent, Environment
from planner import RoutePlanner
from simulator import Simulator

# Imported by student
from collections import namedtuple
from itertools import product

# LearningAgent's state
LAState = namedtuple(
    'LearningAgentState',
    ['next_waypoint', 'light', 'oncoming'])


class LearningAgent(Agent):
    """An agent that learns to drive in the smartcab world."""

    # Learning rate
    ALPHA = 0.66
    # Discount factor
    GAMMA = 0.003

    def __init__(self, env):
        super(LearningAgent, self).__init__(env)  # sets self.env = env, state = None, next_waypoint = None, and a default color
        self.color = 'red'  # override color
        self.planner = RoutePlanner(self.env, self)  # simple route planner to get next_waypoint
        # TODO: Initialize any additional variables here
        self.state_prev = None
        self.action_prev = None
        self.reward_prev = None
        # Initialize Q-values w random values
        self.Q = {}
        for nwp, l, o, a in product(self.env.valid_actions,
                                    ('green', 'red'),
                                    self.env.valid_actions,
                                    self.env.valid_actions):
            self.Q[LAState(nwp, l, o), a] = random.uniform(1, 5)
        # Keep track of how many times the primary agent reached destination
        self.num_reached = 0

    def reset(self, destination=None):
        self.planner.route_to(destination)
        # TODO: Prepare for a new trip; reset any variables here, if required
        self.state_prev = None
        self.action_prev = None
        self.reward_prev = None

    def update(self, t):
        # Gather inputs
        self.next_waypoint = self.planner.next_waypoint()  # from route planner, also displayed by simulator
        inputs = self.env.sense(self)
        deadline = self.env.get_deadline(self)

        # TODO: Update state
        state = LAState(
            next_waypoint=self.next_waypoint,
            light=inputs['light'],
            oncoming=inputs['oncoming'])

        # TODO: Select action according to your policy
        # Basic driving agent
        #action = random.choice(self.env.valid_actions)
        # Action with highest Q score for current state
        action = max(self.env.valid_actions,
                     key=lambda a: self.Q[state, a])

        # Execute action and get reward
        reward = self.env.act(self, action)

        # TODO: Learn policy based on state, action, reward
        if self.state_prev is not None:
            self.Q[self.state_prev, self.action_prev] = \
                (1-self.ALPHA) * self.Q[self.state_prev, self.action_prev] + \
                self.ALPHA * (self.reward_prev + self.GAMMA * self.Q[state, action])

        # Update previous values for the next iteration
        self.state_prev = state
        self.action_prev = action
        self.reward_prev = reward

        # Update number of times that agent reached destination
        self.num_reached += self.env.done

        print "LearningAgent.update(): deadline = {}, inputs = {}, action = {}, reward = {}".format(deadline, inputs, action, reward)  # [debug]


def run():
    """Run the agent for a finite number of trials."""

    # Set up environment and agent
    e = Environment()  # create environment (also adds some dummy traffic)
    a = e.create_agent(LearningAgent)  # create agent
    e.set_primary_agent(a, enforce_deadline=True)  # set agent to track

    # Now simulate it
    sim = Simulator(e, update_delay=0, frame_delay=0)  # reduce update_delay to speed up simulation
    sim.run(n_trials=100)  # press Esc or close pygame window to quit
    print "Total completed: ", a.num_reached


if __name__ == '__main__':
    run()
