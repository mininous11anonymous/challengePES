"""Configuration management for Smart Battery Guardian"""

import os
import yaml
from pathlib import Path


class Config:
    """Central configuration for SBG system"""

    def __init__(self, config_file=None):
        self.config_path = Path(__file__).parent.parent.parent / "config" / "config.yaml"
        if config_file:
            self.config_path = Path(config_file)

        self.config = self._load_config()

    def _load_config(self):
        """Load configuration from YAML file"""
        if self.config_path.exists():
            with open(self.config_path, "r") as f:
                return yaml.safe_load(f) or {}
        return self._default_config()

    @staticmethod
    def _default_config():
        """Default configuration"""
        return {
            "system": {
                "name": "Smart Battery Guardian",
                "version": "1.0.0",
                "device": "cuda" if os.environ.get("CUDA_AVAILABLE") else "cpu",
            },
            "thermal": {
                "model_type": "cnn",
                "input_shape": (64, 64, 3),
                "num_classes": 2,
                "threshold": 0.7,
            },
            "acoustic": {
                "model_type": "spectrogram_classifier",
                "sample_rate": 44100,
                "n_mfcc": 13,
                "threshold": 0.65,
            },
            "rul": {
                "model_type": "lstm",
                "sequence_length": 50,
                "num_features": 5,
                "hidden_units": 64,
            },
            "anomaly": {
                "model_type": "autoencoder",
                "contamination": 0.1,
                "threshold": 0.75,
            },
            "control": {
                "model_type": "dqn",
                "learning_rate": 0.001,
                "gamma": 0.99,
            },
            "data": {
                "batch_size": 32,
                "validation_split": 0.2,
                "test_split": 0.1,
            },
            "training": {
                "epochs": 50,
                "learning_rate": 0.001,
                "early_stopping_patience": 5,
            },
        }

    def get(self, key, default=None):
        """Get configuration value"""
        keys = key.split(".")
        value = self.config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
        return value if value is not None else default

    def set(self, key, value):
        """Set configuration value"""
        keys = key.split(".")
        config = self.config
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value

    def save(self, filepath=None):
        """Save configuration to file"""
        filepath = filepath or self.config_path
        with open(filepath, "w") as f:
            yaml.dump(self.config, f, default_flow_style=False)
