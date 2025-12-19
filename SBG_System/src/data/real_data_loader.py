"""Real Battery Data Integration for SBG System"""

import numpy as np
import pandas as pd
import zipfile
import os
from pathlib import Path
import warnings

warnings.filterwarnings('ignore')


class CALCEDataLoader:
    """Loader for CALCE battery dataset from ZIP file"""
    
    def __init__(self, zip_path):
        """
        Initialize CALCE data loader
        
        Args:
            zip_path: Path to calce-dataset.zip
        """
        self.zip_path = zip_path
        self.data_cache = {}
        
    def list_available_files(self):
        """List all CSV files available in the ZIP"""
        with zipfile.ZipFile(self.zip_path, 'r') as zf:
            return [f for f in zf.namelist() if f.endswith('.csv')]
    
    def load_csv(self, filename):
        """Load a specific CSV file from ZIP"""
        if filename in self.data_cache:
            return self.data_cache[filename]
        
        with zipfile.ZipFile(self.zip_path, 'r') as zf:
            with zf.open(filename) as f:
                df = pd.read_csv(f)
                self.data_cache[filename] = df
                return df
    
    def load_all_test_data(self, limit=None):
        """Load all test battery cycles"""
        files = self.list_available_files()
        test_files = [f for f in files if '/Test/' in f]
        
        data_list = []
        for i, filepath in enumerate(test_files):
            if limit and i >= limit:
                break
            print(f"Loading {filepath}...")
            df = self.load_csv(filepath)
            df['battery_id'] = filepath.split('/')[-1].replace('.csv', '')
            data_list.append(df)
        
        if data_list:
            return pd.concat(data_list, ignore_index=True)
        return pd.DataFrame()
    
    def load_all_train_data(self, limit=None):
        """Load all training battery cycles"""
        files = self.list_available_files()
        train_files = [f for f in files if '/Train/' in f]
        
        data_list = []
        for i, filepath in enumerate(train_files):
            if limit and i >= limit:
                break
            print(f"Loading {filepath}...")
            df = self.load_csv(filepath)
            df['battery_id'] = filepath.split('/')[-1].replace('.csv', '')
            data_list.append(df)
        
        if data_list:
            return pd.concat(data_list, ignore_index=True)
        return pd.DataFrame()


class BatteryDataPreprocessor:
    """Preprocess raw battery data for SBG agents"""
    
    @staticmethod
    def extract_thermal_features(df):
        """
        Extract thermal features from battery data
        
        Returns:
            - thermal_map: 2D array simulating thermal image
            - temperature: scalar temperature reading
        """
        # Use actual temperature if available, else use electrical proxies
        if 'T' in df.columns:
            temperature = df['T'].mean()
        else:
            temperature = 25.0  # Default room temperature
        
        # Create pseudo-thermal map from voltage variations
        v_data = df['V'].values if 'V' in df.columns else np.random.randn(64)
        
        # Create 8x8 thermal map
        if len(v_data) >= 64:
            thermal_map = v_data[:64].reshape(8, 8)
        else:
            thermal_map = np.pad(
                v_data.reshape(-1, 1),
                ((0, 64 - len(v_data)), (0, 7)),
                mode='edge'
            )[:64].reshape(8, 8)
        
        # Normalize to 0-100 range (representing temperature)
        thermal_map = 20 + (thermal_map - thermal_map.min()) / (thermal_map.max() - thermal_map.min() + 1e-6) * 60
        
        return thermal_map.astype(np.float32), float(temperature)
    
    @staticmethod
    def extract_acoustic_features(df, window_size=512):
        """
        Extract acoustic-like features from battery signals
        
        Returns:
            - spectrogram: 2D frequency-time representation
            - fault_indicators: Dict of fault metrics
        """
        # Use current (I) and voltage rate (dV_dt) as acoustic proxies
        if 'I' in df.columns:
            signal = df['I'].values
        elif 'V' in df.columns:
            signal = df['V'].values
        else:
            signal = np.random.randn(1000)
        
        # Pad or truncate to window size
        if len(signal) < window_size:
            signal = np.pad(signal, (0, window_size - len(signal)), mode='edge')
        else:
            signal = signal[:window_size]
        
        # Create pseudo-spectrogram using rolling window FFT
        hop_length = window_size // 8
        specs = []
        
        for i in range(0, len(signal) - window_size, hop_length):
            window = signal[i:i + window_size]
            fft = np.abs(np.fft.fft(window))[:256]
            specs.append(fft)
        
        spectrogram = np.array(specs).T if specs else np.random.randn(256, 8)
        
        # Calculate fault indicators
        fault_indicators = {
            'impedance_rise': df['Internal_Resistance_Ohm_'].mean() if 'Internal_Resistance_Ohm_' in df.columns else 0.1,
            'voltage_noise': df['dV_dt_V_s_'].std() if 'dV_dt_V_s_' in df.columns else 0.01,
            'current_spikes': (np.abs(np.diff(signal)) > np.std(signal) * 2).sum() / len(signal)
        }
        
        return spectrogram.astype(np.float32), fault_indicators
    
    @staticmethod
    def extract_rul_features(df, capacity_fade_threshold=0.8):
        """
        Extract RUL prediction features
        
        Returns:
            - state_features: Dict of state variables
            - capacity_fade: Normalized capacity degradation
        """
        # Extract key state variables
        state_features = {
            'voltage': df['V'].mean() if 'V' in df.columns else 3.7,
            'current': df['I'].mean() if 'I' in df.columns else 0.0,
            'soc': df['SOC'].mean() if 'SOC' in df.columns else 0.5,
            'temperature': df['T'].mean() if 'T' in df.columns else 25.0,
            'charge_capacity': df['ChargeCapacityAh'].max() if 'ChargeCapacityAh' in df.columns else 2.0,
            'discharge_capacity': df['Discharge_CapacityAh'].max() if 'Discharge_CapacityAh' in df.columns else 2.0,
            'impedance': df['Internal_Resistance_Ohm_'].mean() if 'Internal_Resistance_Ohm_' in df.columns else 0.1,
            'cycle_count': df['Cycle_Index'].max() if 'Cycle_Index' in df.columns else 1
        }
        
        # Calculate capacity fade ratio
        initial_capacity = 2.0  # Assumed nominal capacity
        current_capacity = state_features['discharge_capacity']
        capacity_fade = current_capacity / (initial_capacity + 1e-6)
        
        return state_features, capacity_fade
    
    @staticmethod
    def extract_anomaly_features(df):
        """
        Extract anomaly detection features
        
        Returns:
            - feature_vector: Flattened array of anomaly-related features
        """
        features = []
        
        # Voltage anomalies
        if 'V' in df.columns:
            v = df['V'].values
            features.extend([
                np.mean(v),
                np.std(v),
                np.max(v),
                np.min(v),
                np.percentile(v, 95) - np.percentile(v, 5)
            ])
        
        # Current anomalies
        if 'I' in df.columns:
            i = df['I'].values
            features.extend([
                np.mean(i),
                np.std(i),
                np.max(i),
                np.min(i),
                (np.abs(np.diff(i)) > np.std(i) * 3).sum() / len(i)
            ])
        
        # Temperature anomalies
        if 'T' in df.columns:
            t = df['T'].values
            features.extend([
                np.mean(t),
                np.std(t),
                np.max(t),
                np.min(t)
            ])
        
        # Impedance anomalies
        if 'Internal_Resistance_Ohm_' in df.columns:
            r = df['Internal_Resistance_Ohm_'].values
            features.extend([
                np.mean(r),
                np.std(r)
            ])
        
        # Pad to standard size (20 features)
        while len(features) < 20:
            features.append(0.0)
        
        return np.array(features[:20]).astype(np.float32)


class BatteryDataPipeline:
    """End-to-end pipeline for real battery data"""
    
    def __init__(self, data_path):
        """
        Initialize pipeline
        
        Args:
            data_path: Path to data directory containing calce-dataset.zip
        """
        self.data_path = data_path
        zip_path = os.path.join(data_path, 'calce-dataset.zip')
        self.loader = CALCEDataLoader(zip_path)
        self.preprocessor = BatteryDataPreprocessor()
    
    def prepare_data_for_agents(self, limit_files=3):
        """
        Load and prepare real battery data for SBG agents
        
        Returns:
            dict: Data dictionary with keys:
                - 'thermal': List of thermal maps and temps
                - 'acoustic': List of spectrograms and faults
                - 'rul': List of state features and capacity fades
                - 'anomaly': List of anomaly feature vectors
                - 'battery_ids': List of battery IDs
        """
        print("\n" + "="*60)
        print("Loading Real CALCE Battery Data")
        print("="*60)
        
        # Load test data
        df_test = self.loader.load_all_test_data(limit=limit_files)
        
        if df_test.empty:
            print("Warning: No test data loaded!")
            return self._empty_data_dict()
        
        print(f"\nLoaded {len(df_test)} test records from {df_test['battery_id'].nunique()} batteries")
        
        # Prepare data for each agent
        data = {
            'thermal': [],
            'acoustic': [],
            'rul': [],
            'anomaly': [],
            'battery_ids': []
        }
        
        # Process each battery
        for battery_id in df_test['battery_id'].unique():
            df_battery = df_test[df_test['battery_id'] == battery_id]
            
            print(f"\nProcessing {battery_id} ({len(df_battery)} records)")
            
            # Thermal
            thermal_map, temperature = self.preprocessor.extract_thermal_features(df_battery)
            data['thermal'].append({
                'image': thermal_map,
                'temperature': temperature,
                'battery_id': battery_id
            })
            
            # Acoustic
            spectrogram, fault_indicators = self.preprocessor.extract_acoustic_features(df_battery)
            data['acoustic'].append({
                'spectrogram': spectrogram,
                'fault_indicators': fault_indicators,
                'battery_id': battery_id
            })
            
            # RUL
            state_features, capacity_fade = self.preprocessor.extract_rul_features(df_battery)
            data['rul'].append({
                'state': state_features,
                'capacity_fade': capacity_fade,
                'battery_id': battery_id
            })
            
            # Anomaly
            anomaly_features = self.preprocessor.extract_anomaly_features(df_battery)
            data['anomaly'].append({
                'features': anomaly_features,
                'battery_id': battery_id
            })
            
            data['battery_ids'].append(battery_id)
        
        print("\n" + "="*60)
        print("Data Preparation Complete")
        print("="*60)
        
        return data
    
    @staticmethod
    def _empty_data_dict():
        """Return empty data dictionary structure"""
        return {
            'thermal': [],
            'acoustic': [],
            'rul': [],
            'anomaly': [],
            'battery_ids': []
        }


if __name__ == "__main__":
    # Example usage
    data_path = r"c:\Users\21652\Documents\GitHub\challengePES\data"
    pipeline = BatteryDataPipeline(data_path)
    
    # Prepare data
    data = pipeline.prepare_data_for_agents(limit_files=3)
    
    print(f"\nLoaded data for {len(data['battery_ids'])} batteries:")
    print(f"  Thermal samples: {len(data['thermal'])}")
    print(f"  Acoustic samples: {len(data['acoustic'])}")
    print(f"  RUL samples: {len(data['rul'])}")
    print(f"  Anomaly samples: {len(data['anomaly'])}")
