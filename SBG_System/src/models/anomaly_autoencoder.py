"""Autoencoder for Anomaly Detection"""

import torch
import torch.nn as nn


class AnomalyAutoencoder(nn.Module):
    """Autoencoder for real-time anomaly detection"""

    def __init__(self, input_size=10, hidden_size=5, num_layers=2):
        """
        Args:
            input_size: number of input features
            hidden_size: size of bottleneck layer
            num_layers: number of encoding/decoding layers
        """
        super(AnomalyAutoencoder, self).__init__()

        self.input_size = input_size
        self.hidden_size = hidden_size

        # Encoder
        encoder_layers = []
        prev_size = input_size
        for i in range(num_layers):
            next_size = hidden_size + (input_size - hidden_size) * (
                num_layers - i - 1
            ) // num_layers
            encoder_layers.append(nn.Linear(prev_size, next_size))
            if i < num_layers - 1:
                encoder_layers.append(nn.ReLU(inplace=True))
            prev_size = next_size

        self.encoder = nn.Sequential(*encoder_layers)

        # Decoder
        decoder_layers = []
        prev_size = hidden_size
        for i in range(num_layers):
            next_size = hidden_size + (input_size - hidden_size) * (i + 1) // num_layers
            decoder_layers.append(nn.Linear(prev_size, next_size))
            if i < num_layers - 1:
                decoder_layers.append(nn.ReLU(inplace=True))
            prev_size = next_size

        self.decoder = nn.Sequential(*decoder_layers)

    def forward(self, x):
        """Forward pass"""
        encoded = self.encoder(x)
        decoded = self.decoder(encoded)
        return decoded

    def encode(self, x):
        """Get encoded representation"""
        with torch.no_grad():
            encoded = self.encoder(x)
        return encoded

    def get_anomaly_score(self, x):
        """Calculate reconstruction error as anomaly score"""
        with torch.no_grad():
            reconstructed = self.forward(x)
            mse = torch.mean((x - reconstructed) ** 2, dim=1)
        return mse

    def save(self, filepath):
        """Save model weights"""
        torch.save(self.state_dict(), filepath)

    def load(self, filepath):
        """Load model weights"""
        self.load_state_dict(torch.load(filepath))
