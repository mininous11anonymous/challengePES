"""Acoustic Fault Detection Classifier"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import librosa


class AcousticClassifier(nn.Module):
    """Neural network for acoustic fault detection using spectrograms"""

    def __init__(self, input_shape=(13, 173), num_classes=2, dropout_rate=0.3):
        """
        Args:
            input_shape: (n_mfcc, time_steps)
            num_classes: binary classification (normal/fault)
            dropout_rate: dropout probability
        """
        super(AcousticClassifier, self).__init__()

        self.input_shape = input_shape
        self.num_classes = num_classes

        # Reshape to (batch, channels, length) for Conv1D
        # Input: (n_mfcc, time_steps) -> treat n_mfcc as channels
        self.conv_layers = nn.Sequential(
            nn.Conv1d(13, 32, kernel_size=3, stride=1, padding=1),  # Changed from 1 to 13 input channels
            nn.BatchNorm1d(32),
            nn.ReLU(inplace=True),
            nn.MaxPool1d(kernel_size=2, stride=2),
            nn.Dropout(dropout_rate),
            nn.Conv1d(32, 64, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm1d(64),
            nn.ReLU(inplace=True),
            nn.MaxPool1d(kernel_size=2, stride=2),
            nn.Dropout(dropout_rate),
            nn.Conv1d(64, 128, kernel_size=3, stride=1, padding=1),
            nn.BatchNorm1d(128),
            nn.ReLU(inplace=True),
            nn.MaxPool1d(kernel_size=2, stride=2),
            nn.Dropout(dropout_rate),
        )

        # Calculate the flattened size after conv layers
        self.flat_size = self._get_flat_size()

        # Dense layers
        self.dense = nn.Sequential(
            nn.Linear(self.flat_size, 256),
            nn.ReLU(inplace=True),
            nn.Dropout(dropout_rate),
            nn.Linear(256, 128),
            nn.ReLU(inplace=True),
            nn.Dropout(dropout_rate),
            nn.Linear(128, num_classes),
        )

    def _get_flat_size(self):
        """Calculate flattened size after conv layers"""
        # Input shape is (n_mfcc, time_steps), batch format is (batch, n_mfcc, time_steps)
        # For conv1d, it expects (batch, channels, length)
        # So we treat n_mfcc as channels and time_steps as length
        x = torch.zeros(1, *self.input_shape)  # (1, 13, 173)
        x = self.conv_layers(x)
        return int(np.prod(x.shape[1:]))

    def forward(self, x):
        """Forward pass"""
        # x shape: (batch_size, n_mfcc, time_steps)
        # Conv1d expects (batch, channels, length), so x is already in correct format
        x = self.conv_layers(x)
        x = x.view(x.size(0), -1)  # Flatten
        x = self.dense(x)
        return x

    def extract_mfcc(self, audio, sr=44100, n_mfcc=13):
        """Extract MFCC features from audio"""
        mfcc = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=n_mfcc)
        return torch.tensor(mfcc, dtype=torch.float32)

    def predict(self, x):
        """Get predictions"""
        with torch.no_grad():
            logits = self.forward(x)
            probs = F.softmax(logits, dim=1)
            predictions = torch.argmax(probs, dim=1)
        return predictions, probs

    def save(self, filepath):
        """Save model weights"""
        torch.save(self.state_dict(), filepath)

    def load(self, filepath):
        """Load model weights"""
        self.load_state_dict(torch.load(filepath))
