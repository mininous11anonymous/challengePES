"""Synthetic Data Generator for Battery Systems"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta


class SyntheticBatteryDataGenerator:
    """Generate synthetic battery monitoring data for testing"""

    def __init__(self, seed=42):
        np.random.seed(seed)
        self.start_time = datetime.now()

    def generate_normal_thermal_data(self, num_samples=100, height=64, width=64):
        """Generate normal thermal infrared images"""
        images = []
        for _ in range(num_samples):
            # Create realistic thermal gradient
            x = np.linspace(-1, 1, width)
            y = np.linspace(-1, 1, height)
            X, Y = np.meshgrid(x, y)

            # Gaussian thermal distribution
            thermal_base = 40 + 10 * np.exp(-(X**2 + Y**2) / 0.5)
            thermal_base += np.random.normal(0, 1, thermal_base.shape)

            # Stack as RGB channels
            image = np.stack(
                [thermal_base, thermal_base * 0.9, thermal_base * 0.8], axis=2
            )
            images.append(image)

        return np.array(images)

    def generate_anomalous_thermal_data(self, num_samples=100, height=64, width=64):
        """Generate thermal images with anomalies"""
        images = []
        for _ in range(num_samples):
            # Base thermal
            x = np.linspace(-1, 1, width)
            y = np.linspace(-1, 1, height)
            X, Y = np.meshgrid(x, y)
            thermal_base = 40 + 10 * np.exp(-(X**2 + Y**2) / 0.5)

            # Add anomalous hotspot
            hotspot_x = np.random.uniform(-0.5, 0.5)
            hotspot_y = np.random.uniform(-0.5, 0.5)
            hotspot = (
                60
                * np.exp(
                    -(
                        (X - hotspot_x) ** 2 + (Y - hotspot_y) ** 2
                    ) / 0.1
                )
            )
            thermal_base += hotspot

            # Stack as RGB
            image = np.stack(
                [thermal_base, thermal_base * 0.8, thermal_base * 0.6], axis=2
            )
            images.append(image)

        return np.array(images)

    def generate_acoustic_features(self, num_samples=100, n_mfcc=13):
        """Generate MFCC features for acoustic data"""
        features = []
        for i in range(num_samples):
            # Normal acoustic features (low variance)
            mfcc = np.random.normal(20, 5, (n_mfcc, 173))
            features.append(mfcc)

        return np.array(features)

    def generate_faulty_acoustic_features(self, num_samples=100, n_mfcc=13):
        """Generate MFCC features with anomalies"""
        features = []
        for i in range(num_samples):
            # Faulty features (higher variance, different mean)
            mfcc = np.random.normal(35, 15, (n_mfcc, 173))
            features.append(mfcc)

        return np.array(features)

    def generate_battery_cycle_data(
        self, num_cycles=500, num_features=5, degradation_rate=0.001
    ):
        """Generate battery degradation cycle data"""
        data = []
        timestamps = []
        current_time = self.start_time

        for cycle in range(num_cycles):
            # Simulate degradation over cycles
            capacity = 100 * np.exp(-degradation_rate * cycle)
            voltage = 3.7 - 0.001 * cycle + np.random.normal(0, 0.02)
            temperature = 25 + np.random.normal(0, 2)
            current = np.random.uniform(0.5, 2.0)
            resistance = 0.01 + 0.0001 * cycle

            data.append([capacity, voltage, temperature, current, resistance])
            timestamps.append(current_time)
            current_time += timedelta(hours=1)

        df = pd.DataFrame(
            data, columns=["capacity", "voltage", "temperature", "current", "resistance"]
        )
        df["timestamp"] = timestamps
        df["cycle"] = range(num_cycles)

        return df

    def generate_soc_data(self, num_samples=1000):
        """Generate State of Charge data"""
        data = []
        timestamps = []
        current_time = self.start_time

        for i in range(num_samples):
            # Sinusoidal SOC pattern with noise
            soc = 50 + 40 * np.sin(i / 100) + np.random.normal(0, 2)
            soc = np.clip(soc, 0, 100)

            temp = 25 + np.random.normal(0, 1)
            voltage = 3.6 + 0.01 * (soc / 100) + np.random.normal(0, 0.01)
            current = np.random.uniform(-5, 5)

            data.append([soc, temp, voltage, current])
            timestamps.append(current_time)
            current_time += timedelta(minutes=5)

        df = pd.DataFrame(data, columns=["soc", "temperature", "voltage", "current"])
        df["timestamp"] = timestamps

        return df

    def generate_rul_sequence_data(self, num_sequences=100, sequence_length=50):
        """Generate sequences for RUL prediction"""
        X = []
        y = []

        for _ in range(num_sequences):
            # Create degradation sequence
            degradation_rate = np.random.uniform(0.5, 2.0)
            sequence = []

            for t in range(sequence_length):
                capacity = 100 - t * degradation_rate + np.random.normal(0, 1)
                voltage = 3.7 - 0.001 * t + np.random.normal(0, 0.02)
                temperature = 25 + np.random.normal(0, 2)
                current = np.random.uniform(0.5, 2.0)
                resistance = 0.01 + 0.0001 * t

                sequence.append(
                    [capacity, voltage, temperature, current, resistance]
                )

            X.append(sequence)

            # RUL = remaining cycles until capacity drops to 80%
            rul = max(0, (100 - 80) / degradation_rate - sequence_length)
            y.append(rul)

        return np.array(X), np.array(y)

    def generate_multimodal_battery_data(self, duration_hours=24):
        """Generate comprehensive multimodal battery monitoring data"""
        data = {
            "thermal_images": self.generate_normal_thermal_data(num_samples=100),
            "acoustic_features": self.generate_acoustic_features(num_samples=100),
            "cycle_data": self.generate_battery_cycle_data(num_cycles=200),
            "soc_data": self.generate_soc_data(num_samples=500),
            "rul_sequences": self.generate_rul_sequence_data(num_sequences=50),
        }

        return data
