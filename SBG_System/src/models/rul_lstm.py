"""LSTM Model for Remaining Useful Life (RUL) Prediction"""

import torch
import torch.nn as nn


class RULLSTM(nn.Module):
    """LSTM network for RUL prediction"""

    def __init__(
        self,
        input_size=5,
        hidden_size=64,
        num_layers=2,
        output_size=1,
        dropout=0.2,
    ):
        """
        Args:
            input_size: number of input features
            hidden_size: LSTM hidden state size
            num_layers: number of LSTM layers
            output_size: RUL output
            dropout: dropout rate
        """
        super(RULLSTM, self).__init__()

        self.input_size = input_size
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.output_size = output_size

        # LSTM layers
        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout if num_layers > 1 else 0,
        )

        # Attention mechanism
        self.attention = nn.Sequential(
            nn.Linear(hidden_size, hidden_size // 2),
            nn.ReLU(inplace=True),
            nn.Linear(hidden_size // 2, 1),
            nn.Softmax(dim=1),
        )

        # Dense layers
        self.fc = nn.Sequential(
            nn.Linear(hidden_size, 128),
            nn.ReLU(inplace=True),
            nn.Dropout(dropout),
            nn.Linear(128, 64),
            nn.ReLU(inplace=True),
            nn.Dropout(dropout),
            nn.Linear(64, output_size),
            nn.ReLU(inplace=True),  # RUL is non-negative
        )

    def forward(self, x):
        """
        Forward pass
        Args:
            x: input tensor (batch_size, seq_length, input_size)
        Returns:
            output: RUL predictions (batch_size, output_size)
        """
        # LSTM forward
        lstm_out, (h_n, c_n) = self.lstm(x)

        # Attention weights
        attn_weights = self.attention(lstm_out)  # (batch_size, seq_length, 1)
        attn_out = torch.sum(
            lstm_out * attn_weights, dim=1
        )  # (batch_size, hidden_size)

        # Dense layers
        output = self.fc(attn_out)

        return output

    def predict(self, x):
        """Get RUL predictions"""
        with torch.no_grad():
            output = self.forward(x)
        return output

    def save(self, filepath):
        """Save model weights"""
        torch.save(self.state_dict(), filepath)

    def load(self, filepath):
        """Load model weights"""
        self.load_state_dict(torch.load(filepath))
