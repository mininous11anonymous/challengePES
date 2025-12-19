"""Anomaly Detection Agent using CrewAI"""

from typing import Dict, Any
import torch
import numpy as np
from src.models import AnomalyAutoencoder
from src.utils import setup_logger

logger = setup_logger("AnomalyAgent")


class AnomalyDetectionAgent:
    """Agent for real-time anomaly detection using autoencoders"""

    def __init__(self, config=None):
        self.config = config or {}
        self.model = AnomalyAutoencoder(
            input_size=self.config.get("input_size", 10),
            hidden_size=self.config.get("hidden_size", 5),
            num_layers=self.config.get("num_layers", 2),
        )
        self.threshold = self.config.get("threshold", 0.75)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)

        # Anomaly score history for adaptive threshold
        self.score_history = []
        self.max_history = 1000

        logger.info(f"AnomalyDetectionAgent initialized on {self.device}")

    def analyze(self, features: np.ndarray) -> Dict[str, Any]:
        """
        Analyze features for anomalies
        
        Args:
            features: Feature vector (20-dimensional)
            
        Returns:
            Dictionary with anomaly analysis
        """
        # Ensure features are 10-dimensional for the model
        if len(features) > 10:
            features = features[:10]
        elif len(features) < 10:
            features = np.pad(features, (0, 10 - len(features)), mode='edge')
        
        # Detect anomalies
        result = self.detect(features)
        
        # Add risk level
        score = result['anomaly_score']
        if score < 0.3:
            risk_level = 'LOW'
            risk_score = 0.1
        elif score < 0.5:
            risk_level = 'MEDIUM'
            risk_score = 0.4
        elif score < 0.7:
            risk_level = 'HIGH'
            risk_score = 0.7
        else:
            risk_level = 'CRITICAL'
            risk_score = 0.9
        
        return {
            'anomalies_detected': 1 if result['is_anomalous'] else 0,
            'reconstruction_error': score,
            'risk_level': risk_level,
            'risk_score': risk_score,
            'anomaly_type': result['anomaly_level']
        }

    def detect(self, sensor_data: np.ndarray) -> Dict[str, Any]:
        """
        Detect anomalies in sensor readings

        Args:
            sensor_data: Array of shape (num_features,)

        Returns:
            Dictionary with anomaly detection results
        """
        # Convert to tensor
        data_tensor = (
            torch.tensor(sensor_data, dtype=torch.float32).unsqueeze(0).to(self.device)
        )

        # Get anomaly score
        anomaly_score = self.model.get_anomaly_score(data_tensor)
        score = anomaly_score.item()

        # Update history
        self.score_history.append(score)
        if len(self.score_history) > self.max_history:
            self.score_history.pop(0)

        # Adaptive threshold
        adaptive_threshold = self._calculate_adaptive_threshold()

        is_anomalous = score > adaptive_threshold
        anomaly_level = self._calculate_anomaly_level(score, adaptive_threshold)

        result = {
            "is_anomalous": is_anomalous,
            "anomaly_score": score,
            "adaptive_threshold": adaptive_threshold,
            "anomaly_level": anomaly_level,
            "z_score": self._calculate_zscore(score),
            "action": self._get_action(anomaly_level),
        }

        if is_anomalous:
            logger.warning(
                f"Anomaly detected! Score: {score:.4f}, Threshold: {adaptive_threshold:.4f}"
            )
        else:
            logger.debug(f"Normal operation. Score: {score:.4f}")

        return result

    def batch_detect(self, sensor_batch: np.ndarray) -> Dict[str, Any]:
        """Detect anomalies in batch of sensor data"""
        results = []
        anomaly_scores = []

        for data in sensor_batch:
            result = self.detect(data)
            results.append(result)
            anomaly_scores.append(result["anomaly_score"])

        return {
            "num_samples": len(sensor_batch),
            "num_anomalies": sum(r["is_anomalous"] for r in results),
            "mean_anomaly_score": np.mean(anomaly_scores),
            "max_anomaly_score": np.max(anomaly_scores),
            "anomaly_rate": sum(r["is_anomalous"] for r in results) / len(results),
            "results": results,
        }

    def _calculate_adaptive_threshold(self) -> float:
        """Calculate adaptive threshold based on history"""
        if len(self.score_history) < 100:
            return self.threshold

        mean_score = np.mean(self.score_history[-100:])
        std_score = np.std(self.score_history[-100:])

        # Adaptive threshold: mean + 2*std
        adaptive = mean_score + 2 * std_score

        return min(adaptive, 1.0)  # Cap at 1.0

    def _calculate_anomaly_level(self, score: float, threshold: float) -> str:
        """Calculate anomaly severity level"""
        normalized = score / (threshold + 1e-8)

        if normalized < 1.0:
            return "NORMAL"
        elif normalized < 1.5:
            return "MINOR"
        elif normalized < 2.0:
            return "MODERATE"
        else:
            return "SEVERE"

    def _calculate_zscore(self, score: float) -> float:
        """Calculate z-score of anomaly score"""
        if len(self.score_history) < 2:
            return 0.0

        mean = np.mean(self.score_history)
        std = np.std(self.score_history)

        if std == 0:
            return 0.0

        return (score - mean) / std

    def _get_action(self, anomaly_level: str) -> str:
        """Get recommended action"""
        actions = {
            "NORMAL": "Continue monitoring",
            "MINOR": "Increase monitoring frequency",
            "MODERATE": "Alert maintenance team. Prepare for inspection.",
            "SEVERE": "CRITICAL ALERT: Immediate action required!",
        }
        return actions.get(anomaly_level, "Unknown")

    def train(self, train_loader, epochs=50, lr=0.001):
        """Train the anomaly detection model"""
        optimizer = torch.optim.Adam(self.model.parameters(), lr=lr)
        criterion = torch.nn.MSELoss()
        self.model.train()

        for epoch in range(epochs):
            total_loss = 0.0
            for data in train_loader:
                if isinstance(data, (list, tuple)):
                    data = data[0]

                data = data.to(self.device)

                optimizer.zero_grad()
                reconstructed = self.model(data)
                loss = criterion(reconstructed, data)
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
