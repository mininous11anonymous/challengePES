"""Data Loading and Preprocessing"""

import numpy as np
import pandas as pd
import torch
from torch.utils.data import Dataset, DataLoader


class BatteryDataset(Dataset):
    """PyTorch Dataset for battery data"""

    def __init__(self, X, y=None, transform=None):
        self.X = torch.tensor(X, dtype=torch.float32)
        self.y = torch.tensor(y, dtype=torch.float32) if y is not None else None
        self.transform = transform

    def __len__(self):
        return len(self.X)

    def __getitem__(self, idx):
        x = self.X[idx]
        if self.transform:
            x = self.transform(x)

        if self.y is not None:
            return x, self.y[idx]
        return x


class BatteryDataLoader:
    """Utilities for loading battery data"""

    @staticmethod
    def load_from_csv(filepath):
        """Load battery data from CSV"""
        return pd.read_csv(filepath)

    @staticmethod
    def create_sequences(data, sequence_length, stride=1):
        """Create sequences from time series data"""
        sequences = []
        targets = []

        for i in range(0, len(data) - sequence_length, stride):
            seq = data[i : i + sequence_length]
            target = data[i + sequence_length]
            sequences.append(seq)
            targets.append(target)

        return np.array(sequences), np.array(targets)

    @staticmethod
    def normalize_data(X, mean=None, std=None):
        """Normalize data using z-score normalization"""
        if mean is None:
            mean = np.mean(X, axis=0)
        if std is None:
            std = np.std(X, axis=0)

        X_normalized = (X - mean) / (std + 1e-8)
        return X_normalized, mean, std

    @staticmethod
    def create_dataloader(X, y=None, batch_size=32, shuffle=True):
        """Create PyTorch DataLoader"""
        dataset = BatteryDataset(X, y)
        return DataLoader(dataset, batch_size=batch_size, shuffle=shuffle)
