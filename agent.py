import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import random
import gym
from pyrace2d_env import  PyRace2DEnv

class QNetwork(nn.Module):
    def __init__(self, input_size, output_size):
        super(QNetwork, self).__init__()
        self.fc1 = nn.Linear(input_size, 64)
        self.fc2 = nn.Linear(64, 32)
        self.fc3 = nn.Linear(32, output_size)

    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        return self.fc3(x)

class DQNAgent:
    def __init__(self, env, learning_rate=0.00006, discount_factor=0.99, epsilon_start=1.0, epsilon_end=0.01, epsilon_decay=0.995):
        self.env = env
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.epsilon = epsilon_start
        self.epsilon_end = epsilon_end
        self.epsilon_decay = epsilon_decay

        self.state_size = 5
        self.action_size = 3

        self.q_network = QNetwork(self.state_size, self.action_size)
        self.target_network = QNetwork(self.state_size, self.action_size)
        self.target_network.load_state_dict(self.q_network.state_dict())
        self.target_network.eval()

        self.optimizer = optim.Adam(self.q_network.parameters(), lr=learning_rate)

    def choose_action(self, state):
        if np.random.rand() < self.epsilon:
            return np.random.choice(self.action_size)
        else:
            with torch.no_grad():
                state_tensor = torch.FloatTensor(state).unsqueeze(0)
                q_values = self.q_network(state_tensor)
                return torch.argmax(q_values).item()

    def update_q_network(self, state, action, reward, next_state, done):
        state_tensor = torch.FloatTensor(state).unsqueeze(0)
        next_state_tensor = torch.FloatTensor(next_state).unsqueeze(0)

        q_value = self.q_network(state_tensor)[0, action]

        if done:
            target = reward
        else:
            with torch.no_grad():
                max_next_q_value = torch.max(self.target_network(next_state_tensor))
                target = reward + self.discount_factor * max_next_q_value.item()

        loss = nn.MSELoss()(q_value.float(), torch.tensor(target).float())
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

    def update_target_network(self):
        self.target_network.load_state_dict(self.q_network.state_dict())

    def decay_epsilon(self):
        self.epsilon = max(self.epsilon_end, self.epsilon * self.epsilon_decay)

def train_dqn_agent():
    env = PyRace2DEnv()
    agent = DQNAgent(env)

    total_episodes = 1000
    max_steps = 6000

    for episode in range(total_episodes):
        state = env.reset()
        total_reward = 0

        for step in range(max_steps):
            action = agent.choose_action(state)
            next_state, reward, done, _ = env.step(action)

            agent.update_q_network(state, action, reward, next_state, done)

            total_reward += reward
            state = next_state
            env.render()

            if done:
                break

        agent.update_target_network()
        agent.decay_epsilon()

        print(f"Episode: {episode + 1}, Total Reward: {total_reward}, Epsilon: {agent.epsilon}")

    env.close()

if __name__ == "__main__":
    train_dqn_agent()
