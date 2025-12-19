"""Thermal Anomaly Detection Agent using CrewAI"""

from typing import Dict, Any
import torch
import numpy as np
from src.models import ThermalCNN
from src.utils import setup_logger

logger = setup_logger("ThermalAgent")


class ThermalAnomalyAgent:
    """Agent for detecting thermal anomalies in battery systems"""

    def __init__(self, config=None):
        self.config = config or {}
        self.model = ThermalCNN(
            input_channels=3,
            num_classes=2,
            dropout_rate=self.config.get("dropout_rate", 0.3),
        )
        self.threshold = self.config.get("threshold", 0.7)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)

        logger.info(f"ThermalAnomalyAgent initialized on {self.device}")

    def analyze(self, thermal_image: np.ndarray, temperature: float = None) -> Dict[str, Any]:
        """
        Analyze thermal image for anomalies

        Args:
            thermal_image: Array of flexible shape (will be converted to 3xHxW)
            temperature: Scalar temperature reading

        Returns:
            Dictionary with analysis results
        """
        # Handle flexible input shapes
        if thermal_image.ndim == 2:
            # If 2D, convert to 3-channel
            thermal_image = np.stack([thermal_image, thermal_image, thermal_image], axis=0)
        elif thermal_image.ndim == 3 and thermal_image.shape[0] != 3:
            # If shape is (H, W, C), permute to (C, H, W)
            if thermal_image.shape[2] in [1, 3]:
                thermal_image = np.transpose(thermal_image, (2, 0, 1))
                # If single channel, replicate to 3 channels
                if thermal_image.shape[0] == 1:
                    thermal_image = np.repeat(thermal_image, 3, axis=0)
        elif thermal_image.ndim == 3 and thermal_image.shape[0] == 3:
            pass  # Already (C, H, W)
        else:
            # Flatten and reshape to (3, 32, 32)
            thermal_image = thermal_image.flatten()[:3072].reshape(3, 32, 32)
        
        # Normalize image
        image_normalized = thermal_image / (thermal_image.max() + 1e-6) if thermal_image.max() > 1 else thermal_image
        image_tensor = (
            torch.tensor(image_normalized, dtype=torch.float32)
            .unsqueeze(0)
            .to(self.device)
        )

        # Get predictions
        predictions, probs = self.model.predict(image_tensor)

        is_anomalous = probs[0, 1].item() > self.threshold
        anomaly_score = probs[0, 1].item()

        result = {
            "is_anomalous": is_anomalous,
            "anomaly_score": anomaly_score,
            "confidence": max(probs[0].cpu().numpy()),
            "risk_level": self._calculate_risk_level(anomaly_score),
            "risk_score": anomaly_score,
            "recommendation": self._get_recommendation(anomaly_score),
            "temperature": float(temperature) if temperature else None,
            "anomalies": []
        }
        
        # Add temperature-based anomalies
        if temperature and temperature > 50:
            result['anomalies'].append(f'High temperature: {temperature:.1f}°C')
        if temperature and temperature < 0:
            result['anomalies'].append(f'Low temperature: {temperature:.1f}°C')

        logger.info(
            f"Thermal analysis: anomaly={is_anomalous}, score={anomaly_score:.3f}"
        )
        return result

    def batch_analyze(self, thermal_images: np.ndarray) -> Dict[str, Any]:
        """Analyze batch of thermal images"""
        results = []
        anomaly_scores = []

        for image in thermal_images:
            result = self.analyze(image)
            results.append(result)
            anomaly_scores.append(result["anomaly_score"])

        return {
            "num_images": len(thermal_images),
            "num_anomalies": sum(r["is_anomalous"] for r in results),
            "mean_anomaly_score": np.mean(anomaly_scores),
            "max_anomaly_score": np.max(anomaly_scores),
            "results": results,
        }

    def _calculate_risk_level(self, score: float) -> str:
        """Calculate risk level from anomaly score"""
        if score < 0.4:
            return "LOW"
        elif score < 0.7:
            return "MEDIUM"
        else:
            return "HIGH"

    def _get_recommendation(self, score: float) -> str:
        """Get recommendation based on anomaly score"""
        if score < 0.4:
            return "No action needed. Continue normal monitoring."
        elif score < 0.7:
            return "Increase monitoring frequency. Prepare maintenance plan."
        else:
            return "CRITICAL: Immediate inspection required. Consider emergency shutdown."

    def train(self, train_loader, val_loader, epochs=50, lr=0.001):
        """Train the thermal anomaly model"""
        optimizer = torch.optim.Adam(self.model.parameters(), lr=lr)
        criterion = torch.nn.CrossEntropyLoss()
        self.model.train()

        for epoch in range(epochs):
            total_loss = 0.0
            for images, labels in train_loader:
                images = images.to(self.device)
                labels = labels.to(self.device)

                optimizer.zero_grad()
                outputs = self.model(images)
                loss = criterion(outputs, labels)
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
