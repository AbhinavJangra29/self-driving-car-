import gym
from gym import spaces
from pygame.locals import K_w, K_a, K_d
from cargame import PyRace2D
import numpy as np

class PyRace2DEnv(gym.Env):
    def __init__(self):
        super(PyRace2DEnv, self).__init__()

        # Define action and observation spaces
        self.action_space = spaces.Discrete(3)  # Actions: {0: Accelerate, 1: Turn Left, 2: Turn Right}
        self.observation_space = spaces.Box(low=np.array([0, 0, 0, 0, 0]), high=np.array([10, 10, 10, 10, 10]), dtype=int)

        # Create an instance of PyRace2D
        self.game = PyRace2D(is_render=False)

    def step(self, action):
        # Perform the action in the game
        self.game.action(action)

        # Evaluate the game and get the reward
        reward = self.game.evaluate()

        # Check if the game is done
        done = self.game.is_done()

        # Observe the new state
        state = self.game.observe()

        # Return the observation, reward, whether the episode is done, and additional information
        return state, reward, done, {}

    def reset(self):
        # Reset the game
        self.game = PyRace2D(is_render=False)

        # Observe the initial state
        state = self.game.observe()

        return state

    def render(self, mode='human'):
        # Render the game (you can customize rendering based on the mode)
        self.game.view()

    def close(self):
        # Close the environment
        pass
