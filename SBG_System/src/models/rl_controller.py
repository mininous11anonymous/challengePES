"""Reinforcement Learning Controller for Charge/Discharge Optimization"""

import torch
import torch.nn as nn
import numpy as np


class DQNNetwork(nn.Module):
    """Deep Q-Network for battery control"""

    def __init__(self, state_size=8, action_size=5, hidden_size=128):
        """
        Args:
            state_size: size of state vector
            action_size: number of possible actions
            hidden_size: size of hidden layers
        """
        super(DQNNetwork, self).__init__()

        self.fc = nn.Sequential(
            nn.Linear(state_size, hidden_size),
            nn.ReLU(inplace=True),
            nn.Dropout(0.2),
            nn.Linear(hidden_size, hidden_size),
            nn.ReLU(inplace=True),
            nn.Dropout(0.2),
            nn.Linear(hidden_size, action_size),
        )

    def forward(self, state):
        """Forward pass"""
        return self.fc(state)

    def save(self, filepath):
        """Save model weights"""
        torch.save(self.state_dict(), filepath)

    def load(self, filepath):
        """Load model weights"""
        self.load_state_dict(torch.load(filepath))


class RLChargeController:
    """Reinforcement Learning controller for charge/discharge optimization"""

    def __init__(self, state_size=8, action_size=5, learning_rate=0.001, gamma=0.99):
        """
        Args:
            state_size: size of state vector (SOC, temp, voltage, etc.)
            action_size: number of charging rate levels
            learning_rate: learning rate for DQN
            gamma: discount factor
        """
        self.state_size = state_size
        self.action_size = action_size  # 0-5 representing charge rates from -100% to +100%
        self.gamma = gamma
        self.epsilon = 1.0  # Exploration rate
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995

        self.q_network = DQNNetwork(state_size, action_size)
        self.target_network = DQNNetwork(state_size, action_size)
        self.optimizer = torch.optim.Adam(
            self.q_network.parameters(), lr=learning_rate
        )
        self.loss_fn = nn.MSELoss()

    def get_action(self, state, training=True):
        """Get action based on epsilon-greedy strategy"""
        if training and np.random.random() < self.epsilon:
            # Explore
            action = np.random.randint(0, self.action_size)
        else:
            # Exploit
            with torch.no_grad():
                state_tensor = torch.tensor(state, dtype=torch.float32)
                q_values = self.q_network(state_tensor)
                action = torch.argmax(q_values).item()

        return action

    def action_to_charge_rate(self, action):
        """Convert discrete action to continuous charge rate"""
        # Action 0-4 maps to charge rates from -1.0 to +1.0
        charge_rate = (action - 2) / 2.0
        return np.clip(charge_rate, -1.0, 1.0)

    def train_step(self, state, action, reward, next_state, done):
        """Single training step"""
        state_tensor = torch.tensor(state, dtype=torch.float32)
        next_state_tensor = torch.tensor(next_state, dtype=torch.float32)

        # Current Q-value
        q_current = self.q_network(state_tensor)[action]

        # Target Q-value
        with torch.no_grad():
            q_next = self.target_network(next_state_tensor).max()
            q_target = reward + (self.gamma * q_next * (1 - int(done)))

        # Calculate loss and update
        loss = self.loss_fn(q_current, torch.tensor(q_target))
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

        # Decay epsilon
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

        return loss.item()

    def update_target_network(self):
        """Update target network weights"""
        self.target_network.load_state_dict(self.q_network.state_dict())

    def save(self, filepath):
        """Save controller weights"""
        torch.save(self.q_network.state_dict(), filepath)

    def load(self, filepath):
        """Load controller weights"""
        self.q_network.load(filepath)
        self.target_network.load_state_dict(self.q_network.state_dict())
