"""Flask API for Smart Battery Guardian System"""

import os
import json
import numpy as np
import threading
import time
from datetime import datetime
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import sys

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.agents.orchestrator import BatteryMonitoringOrchestrator
from src.data.real_data_loader import BatteryDataPipeline
from src.utils.report_generator import create_battery_report

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Global variables
orchestrator = None
data_pipeline = None
latest_assessment = None
assessment_history = []
monitoring_active = False
monitoring_thread = None
system_metrics = {
    'data_points_ingested': 0,
    'analyses_completed': 0,
    'start_time': None,
    'last_update': None,
    'uptime_seconds': 0,
    'current_batteries': [],
    'data_rate': 0  # data points per second
}

def init_sbg():
    """Initialize SBG system"""
    global orchestrator, data_pipeline
    
    print("Initializing SBG System...")
    
    try:
        # Initialize orchestrator
        orchestrator = BatteryMonitoringOrchestrator()
        
        # Initialize data pipeline - path to challengePES/data
        # Current dir is SBG_System, need to go up one level to challengePES
        data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
        data_pipeline = BatteryDataPipeline(data_dir)
        
        print("✓ SBG System initialized successfully")
        return True
    except Exception as e:
        print(f"✗ Error initializing SBG: {e}")
        return False


@app.route('/', methods=['GET'])
def dashboard():
    """Serve the dashboard HTML"""
    dashboard_path = os.path.join(os.path.dirname(__file__), 'dashboard.html')
    if os.path.exists(dashboard_path):
        return send_file(dashboard_path)
    return jsonify({'status': 'error', 'message': 'Dashboard not found'}), 404


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'orchestrator_ready': orchestrator is not None,
        'data_pipeline_ready': data_pipeline is not None
    })


@app.route('/api/load-real-data', methods=['POST'])
def load_real_data():
    """Load and prepare real battery data"""
    try:
        limit = request.json.get('limit', 5) if request.json else 5
        
        print(f"\nLoading real battery data (limit={limit})...")
        data = data_pipeline.prepare_data_for_agents(limit_files=limit)
        
        return jsonify({
            'status': 'success',
            'message': f'Loaded data for {len(data["battery_ids"])} batteries',
            'batteries': data['battery_ids'],
            'counts': {
                'thermal': len(data['thermal']),
                'acoustic': len(data['acoustic']),
                'rul': len(data['rul']),
                'anomaly': len(data['anomaly'])
            },
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/analyze/battery', methods=['POST'])
def analyze_battery():
    """Run comprehensive battery assessment"""
    global latest_assessment
    
    try:
        if orchestrator is None:
            raise ValueError("Orchestrator not initialized")
        
        # Load data if needed
        if not data_pipeline:
            return jsonify({'status': 'error', 'message': 'Data pipeline not ready'}), 500
        
        # Get battery data
        request_data = request.json or {}
        limit = request_data.get('limit', 3)
        
        print(f"\nRunning comprehensive battery analysis...")
        data = data_pipeline.prepare_data_for_agents(limit_files=limit)
        
        assessments = []
        
        # Analyze each battery
        for i, battery_id in enumerate(data['battery_ids']):
            print(f"\nAnalyzing {battery_id}...")
            
            assessment = {
                'battery_id': battery_id,
                'timestamp': datetime.now().isoformat(),
                'agents': {}
            }
            
            # Thermal agent
            if i < len(data['thermal']):
                thermal_data = data['thermal'][i]
                thermal_risk = orchestrator.thermal_agent.analyze(
                    thermal_data['image'],
                    thermal_data['temperature']
                )
                assessment['agents']['thermal'] = {
                    'risk_level': str(thermal_risk.get('risk_level', 'UNKNOWN')),
                    'risk_score': float(thermal_risk.get('risk_score', 0)),
                    'temperature': thermal_data['temperature'],
                    'anomalies': thermal_risk.get('anomalies', [])
                }
            
            # Acoustic agent
            if i < len(data['acoustic']):
                acoustic_data = data['acoustic'][i]
                acoustic_risk = orchestrator.acoustic_agent.analyze(
                    acoustic_data['spectrogram'],
                    acoustic_data['fault_indicators']
                )
                assessment['agents']['acoustic'] = {
                    'risk_level': str(acoustic_risk.get('risk_level', 'UNKNOWN')),
                    'risk_score': float(acoustic_risk.get('risk_score', 0)),
                    'fault_indicators': acoustic_data['fault_indicators'],
                    'anomalies': acoustic_risk.get('anomalies', [])
                }
            
            # RUL agent
            if i < len(data['rul']):
                rul_data = data['rul'][i]
                rul_risk = orchestrator.rul_agent.analyze(
                    rul_data['state'],
                    rul_data['capacity_fade']
                )
                assessment['agents']['rul'] = {
                    'risk_level': str(rul_risk.get('risk_level', 'UNKNOWN')),
                    'risk_score': float(rul_risk.get('risk_score', 0)),
                    'capacity_fade': rul_data['capacity_fade'],
                    'predicted_rul_cycles': int(rul_risk.get('rul_cycles', 0))
                }
            
            # Anomaly agent
            if i < len(data['anomaly']):
                anomaly_data = data['anomaly'][i]
                anomaly_risk = orchestrator.anomaly_agent.analyze(
                    anomaly_data['features']
                )
                assessment['agents']['anomaly'] = {
                    'risk_level': str(anomaly_risk.get('risk_level', 'UNKNOWN')),
                    'risk_score': float(anomaly_risk.get('risk_score', 0)),
                    'anomalies_detected': anomaly_risk.get('anomalies_detected', 0),
                    'reconstruction_error': float(anomaly_risk.get('reconstruction_error', 0))
                }
            
            # Overall assessment
            risk_scores = [
                assessment['agents'][agent].get('risk_score', 0)
                for agent in ['thermal', 'acoustic', 'rul', 'anomaly']
                if agent in assessment['agents']
            ]
            
            overall_risk = np.mean(risk_scores) if risk_scores else 0.5
            
            if overall_risk >= 0.7:
                overall_level = 'CRITICAL'
            elif overall_risk >= 0.5:
                overall_level = 'WARNING'
            elif overall_risk >= 0.3:
                overall_level = 'CAUTION'
            else:
                overall_level = 'HEALTHY'
            
            assessment['overall'] = {
                'risk_level': overall_level,
                'risk_score': float(overall_risk),
                'recommendation': _get_recommendation(overall_level, assessment['agents'])
            }
            
            assessments.append(assessment)
            assessment_history.append(assessment)
        
        latest_assessment = assessments[0] if assessments else None
        
        return jsonify({
            'status': 'success',
            'assessments': assessments,
            'total_batteries': len(assessments),
            'summary': {
                'avg_risk_score': float(np.mean([a['overall']['risk_score'] for a in assessments])),
                'critical_count': sum(1 for a in assessments if a['overall']['risk_level'] == 'CRITICAL'),
                'warning_count': sum(1 for a in assessments if a['overall']['risk_level'] == 'WARNING'),
                'healthy_count': sum(1 for a in assessments if a['overall']['risk_level'] == 'HEALTHY')
            }
        })
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/assessment/latest', methods=['GET'])
def get_latest_assessment():
    """Get the latest assessment"""
    if latest_assessment:
        return jsonify({
            'status': 'success',
            'assessment': latest_assessment
        })
    else:
        return jsonify({
            'status': 'not_found',
            'message': 'No assessment available yet'
        }), 404


@app.route('/api/assessment/history', methods=['GET'])
def get_assessment_history():
    """Get assessment history"""
    limit = request.args.get('limit', 10, type=int)
    return jsonify({
        'status': 'success',
        'count': len(assessment_history),
        'history': assessment_history[-limit:],
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/models/info', methods=['GET'])
def get_models_info():
    """Get information about loaded models"""
    if orchestrator is None:
        return jsonify({'status': 'error', 'message': 'Orchestrator not initialized'}), 500
    
    return jsonify({
        'status': 'success',
        'models': {
            'thermal_cnn': {
                'type': 'CNN',
                'input_shape': (1, 8, 8),
                'description': 'Thermal anomaly detection'
            },
            'acoustic_classifier': {
                'type': 'Conv1D',
                'input_shape': (256, 8),
                'description': 'Acoustic fault detection'
            },
            'rul_lstm': {
                'type': 'LSTM with Attention',
                'input_shape': (100, 8),
                'description': 'RUL prediction'
            },
            'anomaly_autoencoder': {
                'type': 'Autoencoder',
                'input_shape': (20,),
                'description': 'Anomaly detection'
            }
        },
        'agents': {
            'thermal_agent': 'Analyzes thermal patterns',
            'acoustic_agent': 'Detects acoustic anomalies',
            'rul_agent': 'Predicts remaining useful life',
            'anomaly_agent': 'Multi-modal anomaly detection'
        }
    })


def _get_recommendation(risk_level, agents_data):
    """Generate recommendation based on risk level and agent findings"""
    recommendations = {
        'CRITICAL': 'IMMEDIATE ACTION REQUIRED: Battery requires urgent inspection and possible replacement. Do not use in critical applications.',
        'WARNING': 'TAKE ACTION: Battery should be scheduled for maintenance within the next week. Monitor closely.',
        'CAUTION': 'MONITOR: Battery is showing some signs of degradation. Plan for maintenance within 30 days.',
        'HEALTHY': 'NO ACTION NEEDED: Battery is operating normally. Continue regular monitoring.'
    }
    
    rec = recommendations.get(risk_level, 'Unknown status')
    
    # Add specific agent findings
    if 'thermal' in agents_data and agents_data['thermal']['risk_score'] > 0.7:
        rec += " [Thermal issues detected]"
    if 'acoustic' in agents_data and agents_data['acoustic']['risk_score'] > 0.7:
        rec += " [Acoustic faults detected]"
    if 'rul' in agents_data and agents_data['rul']['risk_score'] > 0.7:
        rec += " [RUL degradation]"
    if 'anomaly' in agents_data and agents_data['anomaly']['risk_score'] > 0.7:
        rec += " [Abnormal behavior detected]"
    
    return rec


@app.route('/api/generate-report', methods=['POST'])
def generate_report():
    """Generate a PDF report for battery assessments"""
    try:
        data = request.get_json()
        
        # Get assessments from request or use latest
        assessments = data.get('assessments', [])
        if not assessments and latest_assessment:
            assessments = [latest_assessment]
        
        if not assessments:
            return jsonify({'error': 'No assessments available'}), 400
        
        # Calculate summary statistics
        summary = {
            'total_batteries': len(assessments),
            'avg_risk_score': np.mean([a.get('overall', {}).get('risk_score', 0) for a in assessments]),
            'healthy_count': len([a for a in assessments if a.get('overall', {}).get('risk_level') == 'HEALTHY']),
            'warning_count': len([a for a in assessments if a.get('overall', {}).get('risk_level') in ['CAUTION', 'WARNING']]),
            'critical_count': len([a for a in assessments if a.get('overall', {}).get('risk_level') == 'CRITICAL']),
        }
        
        # Generate PDF
        pdf_buffer = create_battery_report(assessments, summary)
        
        # Return PDF file
        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f"battery_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        )
    
    except Exception as e:
        print(f"Error generating report: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/monitoring/status', methods=['GET'])
def get_monitoring_status():
    """Get real-time monitoring status"""
    global system_metrics
    
    if system_metrics['start_time']:
        system_metrics['uptime_seconds'] = (datetime.now() - system_metrics['start_time']).total_seconds()
    
    return jsonify({
        'status': 'success',
        'monitoring_active': monitoring_active,
        'metrics': system_metrics,
        'timestamp': datetime.now().isoformat(),
        'last_assessment': latest_assessment['timestamp'] if latest_assessment else None
    })


@app.route('/api/monitoring/start', methods=['POST'])
def start_real_time_monitoring():
    """Start real-time data ingestion and monitoring"""
    global monitoring_active, system_metrics, monitoring_thread
    
    try:
        if monitoring_active:
            return jsonify({
                'status': 'already_active',
                'message': 'Monitoring already running',
                'metrics': system_metrics
            })
        
        # Reset metrics
        system_metrics = {
            'data_points_ingested': 0,
            'analyses_completed': 0,
            'start_time': datetime.now(),
            'last_update': datetime.now(),
            'uptime_seconds': 0,
            'current_batteries': [],
            'data_rate': 0
        }
        
        monitoring_active = True
        
        # Start background monitoring thread
        monitoring_thread = threading.Thread(target=_continuous_monitoring, daemon=True)
        monitoring_thread.start()
        
        return jsonify({
            'status': 'started',
            'message': 'Real-time monitoring started',
            'start_time': system_metrics['start_time'].isoformat()
        })
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/monitoring/stop', methods=['POST'])
def stop_real_time_monitoring():
    """Stop real-time monitoring"""
    global monitoring_active
    
    monitoring_active = False
    
    return jsonify({
        'status': 'stopped',
        'message': 'Real-time monitoring stopped',
        'final_metrics': system_metrics
    })


def _continuous_monitoring():
    """Background thread for continuous data monitoring"""
    global monitoring_active, system_metrics, latest_assessment, assessment_history
    
    data_batch = []
    batch_size = 2
    data_ingestion_count = 0
    
    while monitoring_active:
        try:
            if not data_pipeline:
                time.sleep(1)
                continue
            
            # Simulate real-time data ingestion
            data = data_pipeline.prepare_data_for_agents(limit_files=1)
            
            if data and data['battery_ids']:
                battery_id = data['battery_ids'][0]
                
                # Simulate ingesting data points from each agent
                thermal_points = len(data.get('thermal', []))
                acoustic_points = len(data.get('acoustic', []))
                rul_points = len(data.get('rul', []))
                anomaly_points = len(data.get('anomaly', []))
                
                data_points = thermal_points + acoustic_points + rul_points + anomaly_points
                data_ingestion_count += data_points
                system_metrics['data_points_ingested'] += data_points
                
                # Update current batteries
                if battery_id not in system_metrics['current_batteries']:
                    system_metrics['current_batteries'].append(battery_id)
                
                # Calculate data rate (points per second)
                if system_metrics['start_time']:
                    elapsed = (datetime.now() - system_metrics['start_time']).total_seconds()
                    if elapsed > 0:
                        system_metrics['data_rate'] = round(system_metrics['data_points_ingested'] / elapsed, 2)
                
                data_batch.append(battery_id)
                
                # When batch is ready, run analysis
                if len(data_batch) >= batch_size:
                    # Analyze batch
                    assessments = []
                    for i, bat_id in enumerate(data_batch):
                        assessment = {
                            'battery_id': bat_id,
                            'timestamp': datetime.now().isoformat(),
                            'agents': {},
                            'ingestion_batch': data_ingestion_count
                        }
                        
                        # Run quick analysis on ingested data
                        try:
                            if orchestrator and i < len(data['thermal']):
                                thermal_data = data['thermal'][i] if i < len(data['thermal']) else None
                                if thermal_data:
                                    thermal_risk = orchestrator.thermal_agent.analyze(
                                        thermal_data['image'],
                                        thermal_data['temperature']
                                    )
                                    assessment['agents']['thermal'] = {
                                        'risk_score': float(thermal_risk.get('risk_score', 0)),
                                        'temperature': thermal_data['temperature']
                                    }
                        except:
                            pass
                        
                        assessments.append(assessment)
                    
                    latest_assessment = assessments[0] if assessments else None
                    assessment_history.extend(assessments)
                    system_metrics['analyses_completed'] += len(assessments)
                    system_metrics['last_update'] = datetime.now().isoformat()
                    
                    data_batch = []
                
                # Simulate real-time data arrival
                time.sleep(0.5)
        
        except Exception as e:
            print(f"Error in continuous monitoring: {e}")
            time.sleep(1)


if __name__ == '__main__':
    # Initialize SBG
    if init_sbg():
        print("\n" + "="*70)
        print("🔋 SMART BATTERY GUARDIAN - API SERVER STARTING")
        print("="*70)
        print("\n🌐 Access the Dashboard at: http://localhost:5000")
        print("\n📊 API Endpoints:")
        print("  ├─ GET    /api/health                 (Health check)")
        print("  ├─ POST   /api/load-real-data         (Load battery data)")
        print("  ├─ POST   /api/analyze/battery        (Run analysis)")
        print("  ├─ GET    /api/assessment/latest      (Get latest assessment)")
        print("  ├─ GET    /api/assessment/history     (Get assessment history)")
        print("  ├─ GET    /api/models/info            (Model information)")
        print("  ├─ POST   /api/generate-report        (PDF report generation)")
        print("  ├─ POST   /api/monitoring/start       (Start real-time monitoring)")
        print("  ├─ POST   /api/monitoring/stop        (Stop real-time monitoring)")
        print("  └─ GET    /api/monitoring/status      (Get monitoring metrics)")
        print("\n🔴 REAL-TIME FEATURES:")
        print("  ✓ Live data ingestion monitoring")
        print("  ✓ Real-time metrics tracking")
        print("  ✓ Continuous battery analysis")
        print("  ✓ System uptime tracking")
        print("\n" + "="*70)
        print("✓ System ready. Click 'Start Real-Time Monitor' on dashboard!")
        print("="*70 + "\n")
        
        # Run Flask app
        app.run(debug=True, host='0.0.0.0', port=5000)
    else:
        print("Failed to initialize SBG system!")
        sys.exit(1)
