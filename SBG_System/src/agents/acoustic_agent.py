"""Acoustic Fault Detection Agent using CrewAI"""

from typing import Dict, Any
import torch
import numpy as np
from src.models import AcousticClassifier
from src.utils import setup_logger

logger = setup_logger("AcousticAgent")


class AcousticFaultAgent:
    """Agent for detecting acoustic faults in battery systems"""

    def __init__(self, config=None):
        self.config = config or {}
        self.model = AcousticClassifier(
            input_shape=(13, 173),
            num_classes=2,
            dropout_rate=self.config.get("dropout_rate", 0.3),
        )
        self.threshold = self.config.get("threshold", 0.65)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)

        logger.info(f"AcousticFaultAgent initialized on {self.device}")

    def analyze(self, mfcc_features: np.ndarray, fault_indicators: Dict = None) -> Dict[str, Any]:
        """
        Analyze acoustic features for faults

        Args:
            mfcc_features: MFCC features array (flexible shape)
            fault_indicators: Dict with impedance_rise, voltage_noise, current_spikes

        Returns:
            Dictionary with analysis results
        """
        # Reshape input to match model expectations (13, 173)
        if mfcc_features.shape != (13, 173):
            # Resize using simple padding/truncation strategy
            h, w = mfcc_features.shape[:2] if mfcc_features.ndim >= 2 else (1, len(mfcc_features.flatten()))
            
            # Flatten and reshape
            data = mfcc_features.flatten()
            target_size = 13 * 173
            
            if len(data) < target_size:
                # Pad with last value
                data = np.pad(data, (0, target_size - len(data)), mode='edge')
            else:
                # Truncate
                data = data[:target_size]
            
            mfcc_features = data.reshape(13, 173)
        
        # Convert to tensor - shape should be (batch=1, channels=1, height=13, width=173) -> (1, 13, 173) for Conv1d
        # Conv1d expects (batch, channels, length), so we treat it as (1, 13, 173)
        features_tensor = (
            torch.tensor(mfcc_features, dtype=torch.float32)
            .unsqueeze(0)  # Add batch dimension: (1, 13, 173)
            .to(self.device)
        )

        # Get predictions
        predictions, probs = self.model.predict(features_tensor)

        is_faulty = probs[0, 1].item() > self.threshold
        fault_score = probs[0, 1].item()

        result = {
            "is_faulty": is_faulty,
            "fault_score": fault_score,
            "confidence": max(probs[0].cpu().numpy()),
            "fault_type": self._identify_fault_type(fault_score),
            "severity": self._calculate_severity(fault_score),
            "action": self._get_action(fault_score),
            "risk_level": self._get_risk_level(fault_score),
            "anomalies": []
        }
        
        # Add fault indicators if available
        if fault_indicators:
            result['anomalies'] = self._check_fault_indicators(fault_indicators)

        logger.info(f"Acoustic analysis: faulty={is_faulty}, score={fault_score:.3f}")
        return result
    
    def _check_fault_indicators(self, indicators: Dict) -> list:
        """Check specific fault indicators"""
        anomalies = []
        if indicators.get('impedance_rise', 0) > 0.15:
            anomalies.append('High impedance rise')
        if indicators.get('voltage_noise', 0) > 0.05:
            anomalies.append('Excessive voltage noise')
        if indicators.get('current_spikes', 0) > 0.1:
            anomalies.append('Current spikes detected')
        return anomalies
    
    def _get_risk_level(self, score: float) -> str:
        """Get risk level"""
        if score < 0.35:
            return "LOW"
        elif score < 0.60:
            return "MEDIUM"
        elif score < 0.80:
            return "HIGH"
        else:
            return "CRITICAL"

    def batch_analyze(self, mfcc_batch: np.ndarray) -> Dict[str, Any]:
        """Analyze batch of acoustic features"""
        results = []
        fault_scores = []

        for mfcc in mfcc_batch:
            result = self.analyze(mfcc)
            results.append(result)
            fault_scores.append(result["fault_score"])

        return {
            "num_samples": len(mfcc_batch),
            "num_faults": sum(r["is_faulty"] for r in results),
            "mean_fault_score": np.mean(fault_scores),
            "max_fault_score": np.max(fault_scores),
            "results": results,
        }

    def _identify_fault_type(self, score: float) -> str:
        """Identify type of fault"""
        if score < 0.35:
            return "NONE"
        elif score < 0.60:
            return "MINOR_DEGRADATION"
        elif score < 0.80:
            return "SIGNIFICANT_DEGRADATION"
        else:
            return "CRITICAL_MICROCRACKS"

    def _calculate_severity(self, score: float) -> str:
        """Calculate fault severity"""
        if score < 0.35:
            return "NONE"
        elif score < 0.60:
            return "MINOR"
        elif score < 0.80:
            return "MODERATE"
        else:
            return "SEVERE"

    def _get_action(self, score: float) -> str:
        """Get recommended action"""
        if score < 0.35:
            return "Continue monitoring"
        elif score < 0.60:
            return "Increase monitoring frequency"
        elif score < 0.80:
            return "Schedule preventive maintenance"
        else:
            return "URGENT: Immediate maintenance required"

    def train(self, train_loader, val_loader, epochs=50, lr=0.001):
        """Train the acoustic fault model"""
        optimizer = torch.optim.Adam(self.model.parameters(), lr=lr)
        criterion = torch.nn.CrossEntropyLoss()
        self.model.train()

        for epoch in range(epochs):
            total_loss = 0.0
            for features, labels in train_loader:
                features = features.to(self.device)
                labels = labels.to(self.device)

                optimizer.zero_grad()
                outputs = self.model(features)
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
