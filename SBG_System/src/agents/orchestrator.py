"""Battery Monitoring Orchestrator using CrewAI patterns"""

from typing import Dict, Any, List
import numpy as np
from datetime import datetime
from src.agents import (
    ThermalAnomalyAgent,
    AcousticFaultAgent,
    RULPredictionAgent,
    AnomalyDetectionAgent,
)
from src.models import RLChargeController
from src.utils import setup_logger

logger = setup_logger("Orchestrator")


class BatteryMonitoringOrchestrator:
    """
    Main orchestrator for Smart Battery Guardian system.
    Coordinates all AI agents and generates comprehensive battery health assessment.
    """

    def __init__(self, config=None):
        self.config = config or {}

        # Initialize all agents
        logger.info("Initializing all monitoring agents...")
        self.thermal_agent = ThermalAnomalyAgent(
            self.config.get("thermal", {})
        )
        self.acoustic_agent = AcousticFaultAgent(
            self.config.get("acoustic", {})
        )
        self.rul_agent = RULPredictionAgent(self.config.get("rul", {}))
        self.anomaly_agent = AnomalyDetectionAgent(
            self.config.get("anomaly", {})
        )
        self.rl_controller = RLChargeController(
            state_size=8,
            action_size=5,
            **self.config.get("control", {}),
        )

        # Monitoring state
        self.last_assessment = None
        self.assessment_history = []
        self.risk_scores = {"thermal": 0.0, "acoustic": 0.0, "rul": 0.0, "anomaly": 0.0}

        logger.info("Orchestrator initialized successfully")

    def comprehensive_assessment(
        self,
        thermal_image: np.ndarray,
        acoustic_features: np.ndarray,
        rul_sequence: np.ndarray,
        sensor_data: np.ndarray,
    ) -> Dict[str, Any]:
        """
        Perform comprehensive battery health assessment using all agents

        Args:
            thermal_image: Thermal infrared image
            acoustic_features: MFCC features from acoustic sensors
            rul_sequence: Historical cycle data sequence
            sensor_data: Current sensor readings

        Returns:
            Comprehensive assessment report
        """
        timestamp = datetime.now()

        logger.info("Starting comprehensive battery assessment...")

        # Parallel agent analysis
        thermal_result = self.thermal_agent.analyze(thermal_image)
        acoustic_result = self.acoustic_agent.analyze(acoustic_features)
        rul_result = self.rul_agent.predict(rul_sequence)
        anomaly_result = self.anomaly_agent.detect(sensor_data)

        # Update risk scores
        self.risk_scores["thermal"] = thermal_result["anomaly_score"]
        self.risk_scores["acoustic"] = acoustic_result["fault_score"]
        self.risk_scores["rul"] = 1.0 - (
            rul_result["predicted_rul"] / 500.0
        )  # Invert for risk
        self.risk_scores["anomaly"] = anomaly_result["anomaly_score"]

        # Calculate overall risk
        overall_risk = self._calculate_overall_risk()

        # Generate control recommendations
        control_state = self._build_state_vector(
            thermal_result, acoustic_result, rul_result, anomaly_result
        )
        action = self.rl_controller.get_action(control_state, training=False)
        charge_rate = self.rl_controller.action_to_charge_rate(action)

        # Comprehensive assessment report
        assessment = {
            "timestamp": timestamp,
            "overall_health": self._calculate_overall_health(),
            "overall_risk_score": overall_risk,
            "risk_scores": self.risk_scores.copy(),
            "thermal_analysis": thermal_result,
            "acoustic_analysis": acoustic_result,
            "rul_prediction": rul_result,
            "anomaly_detection": anomaly_result,
            "control_recommendation": {
                "charge_rate": charge_rate,
                "action": action,
                "rationale": self._get_control_rationale(
                    charge_rate, overall_risk
                ),
            },
            "alerts": self._generate_alerts(
                thermal_result, acoustic_result, rul_result, anomaly_result, overall_risk
            ),
            "summary": self._generate_summary(overall_risk),
        }

        # Store in history
        self.last_assessment = assessment
        self.assessment_history.append(assessment)

        logger.info(f"Assessment complete. Overall risk: {overall_risk:.3f}")

        return assessment

    def _calculate_overall_risk(self) -> float:
        """Calculate weighted overall risk score"""
        weights = {
            "thermal": 0.3,
            "acoustic": 0.25,
            "rul": 0.25,
            "anomaly": 0.2,
        }

        overall_risk = sum(
            self.risk_scores[key] * weights[key] for key in weights
        )

        return min(1.0, overall_risk)

    def _calculate_overall_health(self) -> str:
        """Calculate overall health status"""
        risk = self._calculate_overall_risk()

        if risk < 0.3:
            return "EXCELLENT"
        elif risk < 0.5:
            return "GOOD"
        elif risk < 0.7:
            return "FAIR"
        elif risk < 0.85:
            return "POOR"
        else:
            return "CRITICAL"

    def _build_state_vector(self, thermal_res, acoustic_res, rul_res, anomaly_res):
        """Build state vector for RL controller"""
        state = np.array([
            thermal_res["anomaly_score"],
            acoustic_res["fault_score"],
            rul_res["predicted_rul"] / 500.0,  # Normalize
            anomaly_res["anomaly_score"],
            anomaly_res["z_score"],
            rul_res["predicted_rul"] / 100.0,  # Alternative RUL metric
            thermal_res["confidence"],
            acoustic_res["confidence"],
        ])
        return state

    def _get_control_rationale(self, charge_rate: float, overall_risk: float) -> str:
        """Explain the control decision"""
        if overall_risk > 0.8:
            return (
                "CRITICAL: Reducing charge rate to prevent thermal runaway "
                "and stress."
            )
        elif overall_risk > 0.6:
            return "HIGH RISK: Moderately reducing charge rate for safety."
        elif overall_risk > 0.4:
            return "MEDIUM RISK: Slight charge rate adjustment."
        else:
            return "Low risk detected. Optimal charge rate applied."

    def _generate_alerts(
        self, thermal_res, acoustic_res, rul_res, anomaly_res, overall_risk
    ) -> List[Dict[str, str]]:
        """Generate alerts based on analysis"""
        alerts = []

        if thermal_res["is_anomalous"]:
            alerts.append({
                "level": "CRITICAL" if thermal_res["anomaly_score"] > 0.85 else "WARNING",
                "source": "Thermal",
                "message": f"Thermal anomaly detected: {thermal_res['recommendation']}",
            })

        if acoustic_res["is_faulty"]:
            alerts.append({
                "level": "CRITICAL" if acoustic_res["fault_score"] > 0.85 else "WARNING",
                "source": "Acoustic",
                "message": f"Acoustic fault detected: {acoustic_res['action']}",
            })

        if rul_res["predicted_rul"] < 50:
            alerts.append({
                "level": "CRITICAL",
                "source": "RUL",
                "message": f"Low RUL detected: {rul_res['maintenance_recommendation']}",
            })

        if anomaly_res["anomaly_level"] in ["MODERATE", "SEVERE"]:
            alerts.append({
                "level": "WARNING",
                "source": "Anomaly Detection",
                "message": f"Anomaly level {anomaly_res['anomaly_level']}: {anomaly_res['action']}",
            })

        if overall_risk > 0.8:
            alerts.append({
                "level": "CRITICAL",
                "source": "System",
                "message": "CRITICAL RISK: Immediate intervention required!",
            })

        return alerts

    def _generate_summary(self, overall_risk: float) -> str:
        """Generate human-readable summary"""
        risk_level = self._risk_to_level(overall_risk)

        summary = f"Battery Health Assessment - Risk Level: {risk_level}\n"
        summary += f"Overall Risk Score: {overall_risk:.1%}\n"

        if self.last_assessment:
            num_alerts = len(self.last_assessment.get("alerts", []))
            summary += f"Active Alerts: {num_alerts}\n"

        return summary

    @staticmethod
    def _risk_to_level(risk: float) -> str:
        """Convert risk score to level"""
        if risk < 0.3:
            return "LOW"
        elif risk < 0.5:
            return "MODERATE"
        elif risk < 0.7:
            return "HIGH"
        else:
            return "CRITICAL"

    def get_assessment_history(self, num_last=10) -> List[Dict[str, Any]]:
        """Get recent assessment history"""
        return self.assessment_history[-num_last:]

    def save_checkpoint(self, filepath: str):
        """Save all agent models"""
        import os

        os.makedirs(filepath, exist_ok=True)

        self.thermal_agent.save(os.path.join(filepath, "thermal_agent.pt"))
        self.acoustic_agent.save(os.path.join(filepath, "acoustic_agent.pt"))
        self.rul_agent.save(os.path.join(filepath, "rul_agent.pt"))
        self.anomaly_agent.save(os.path.join(filepath, "anomaly_agent.pt"))
        self.rl_controller.save(os.path.join(filepath, "rl_controller.pt"))

        logger.info(f"Checkpoint saved to {filepath}")

    def load_checkpoint(self, filepath: str):
        """Load all agent models"""
        import os

        self.thermal_agent.load(os.path.join(filepath, "thermal_agent.pt"))
        self.acoustic_agent.load(os.path.join(filepath, "acoustic_agent.pt"))
        self.rul_agent.load(os.path.join(filepath, "rul_agent.pt"))
        self.anomaly_agent.load(os.path.join(filepath, "anomaly_agent.pt"))
        self.rl_controller.load(os.path.join(filepath, "rl_controller.pt"))

        logger.info(f"Checkpoint loaded from {filepath}")
