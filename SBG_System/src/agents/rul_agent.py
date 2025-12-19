"""RUL Prediction Agent using CrewAI"""

from typing import Dict, Any
import torch
import numpy as np
from src.models import RULLSTM
from src.utils import setup_logger

logger = setup_logger("RULAgent")


class RULPredictionAgent:
    """Agent for predicting Remaining Useful Life of batteries"""

    def __init__(self, config=None):
        self.config = config or {}
        self.model = RULLSTM(
            input_size=self.config.get("num_features", 5),
            hidden_size=self.config.get("hidden_units", 64),
            num_layers=self.config.get("num_layers", 2),
            output_size=1,
            dropout=self.config.get("dropout", 0.2),
        )
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)
        self.model.eval()

        logger.info(f"RULPredictionAgent initialized on {self.device}")

    def analyze(self, state_dict: Dict, capacity_fade: float) -> Dict[str, Any]:
        """
        Analyze RUL from state dictionary
        
        Args:
            state_dict: Dict with voltage, current, soc, temperature, etc.
            capacity_fade: Normalized capacity (0-1)
            
        Returns:
            Dictionary with RUL analysis
        """
        # Build feature sequence from state dict
        features = [
            state_dict.get('voltage', 3.7),
            state_dict.get('current', 0.0),
            state_dict.get('soc', 0.5),
            state_dict.get('temperature', 25.0),
            state_dict.get('impedance', 0.1)
        ]
        
        # Create a simple sequence (just use this one state repeated)
        sequence = np.array([features] * 5).astype(np.float32)  # 5-step sequence
        
        # Predict RUL
        result = self.predict(sequence)
        
        # Add risk level based on RUL
        rul_cycles = result['rul_cycles']
        if rul_cycles > 400:
            risk_level = 'LOW'
            risk_score = 0.2
        elif rul_cycles > 200:
            risk_level = 'MEDIUM'
            risk_score = 0.5
        elif rul_cycles > 50:
            risk_level = 'HIGH'
            risk_score = 0.7
        else:
            risk_level = 'CRITICAL'
            risk_score = 0.95
        
        return {
            'predicted_rul_cycles': rul_cycles,
            'capacity_fade': capacity_fade,
            'risk_level': risk_level,
            'risk_score': risk_score,
            'health_status': result['health_status'],
            'maintenance_recommendation': result['maintenance_recommendation']
        }

    def predict(self, sequence: np.ndarray) -> Dict[str, Any]:
        """
        Predict RUL from battery cycle sequence

        Args:
            sequence: Array of shape (sequence_length, num_features)

        Returns:
            Dictionary with RUL prediction and confidence
        """
        # Convert to tensor
        sequence_tensor = (
            torch.tensor(sequence, dtype=torch.float32).unsqueeze(0).to(self.device)
        )

        with torch.no_grad():
            rul_pred = self.model.predict(sequence_tensor)

        rul_value = max(0, rul_pred.item())

        result = {
            "predicted_rul": rul_value,
            "rul_cycles": int(rul_value),
            "confidence": self._estimate_confidence(rul_value),
            "health_status": self._get_health_status(rul_value),
            "maintenance_recommendation": self._get_maintenance_recommendation(
                rul_value
            ),
        }

        logger.info(f"RUL prediction: {rul_value:.2f} cycles")
        return result

    def batch_predict(self, sequences: np.ndarray) -> Dict[str, Any]:
        """Predict RUL for batch of sequences"""
        predictions = []
        rul_values = []

        for seq in sequences:
            result = self.predict(seq)
            predictions.append(result)
            rul_values.append(result["predicted_rul"])

        return {
            "num_sequences": len(sequences),
            "mean_rul": np.mean(rul_values),
            "min_rul": np.min(rul_values),
            "max_rul": np.max(rul_values),
            "std_rul": np.std(rul_values),
            "predictions": predictions,
        }

    def _estimate_confidence(self, rul: float) -> float:
        """Estimate prediction confidence"""
        # Higher RUL predictions have lower confidence (more uncertain)
        if rul < 10:
            return 0.95
        elif rul < 50:
            return 0.85
        elif rul < 100:
            return 0.70
        else:
            return 0.50

    def _get_health_status(self, rul: float) -> str:
        """Get battery health status"""
        if rul > 200:
            return "EXCELLENT"
        elif rul > 100:
            return "GOOD"
        elif rul > 50:
            return "FAIR"
        elif rul > 10:
            return "POOR"
        else:
            return "CRITICAL"

    def _get_maintenance_recommendation(self, rul: float) -> str:
        """Get maintenance recommendation based on RUL"""
        if rul > 200:
            return "No maintenance needed. Continue normal operation."
        elif rul > 100:
            return "Plan maintenance within next 100 cycles."
        elif rul > 50:
            return "Schedule maintenance within next 50 cycles."
        elif rul > 10:
            return "Urgent: Schedule maintenance within 10 cycles."
        else:
            return "CRITICAL: Battery replacement imminent!"

    def train(self, train_loader, val_loader, epochs=50, lr=0.001):
        """Train the RUL prediction model"""
        optimizer = torch.optim.Adam(self.model.parameters(), lr=lr)
        criterion = torch.nn.MSELoss()
        self.model.train()

        for epoch in range(epochs):
            total_loss = 0.0
            for sequences, targets in train_loader:
                sequences = sequences.to(self.device)
                targets = targets.to(self.device).unsqueeze(1)

                optimizer.zero_grad()
                outputs = self.model(sequences)
                loss = criterion(outputs, targets)
                loss.backward()
                optimizer.step()

                total_loss += loss.item()

            avg_loss = total_loss / len(train_loader)
            logger.info(f"Epoch [{epoch+1}/{epochs}], Loss: {avg_loss:.4f}")

    def save(self, filepath: str):
        """Save model checkpoint"""
        torch.save(self.model.state_dict(), filepath)
        logger.info(f"Model saved to {filepath}")

    def load(self, filepath: str):
        """Load model checkpoint"""
        self.model.load_state_dict(torch.load(filepath, map_location=self.device))
        logger.info(f"Model loaded from {filepath}")
