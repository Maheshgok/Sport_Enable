"""
Base Sport Analyzer
Common functionality for all sport-specific analysis functions
"""

import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from abc import ABC, abstractmethod
from datetime import datetime
import json
from typing import Dict, List, Any, Tuple
from google.cloud import storage


class BaseSportAnalyzer(ABC):
    """Base class for sport-specific motion analysis"""
    
    def __init__(self, sport_config: Dict[str, Any]):
        """
        Initialize analyzer with sport configuration
        
        Args:
            sport_config: Sport configuration from sports_config.py
        """
        self.sport_id = sport_config['sport_id']
        self.sport_name = sport_config['name']
        self.baselines = sport_config['baseline_metrics']
        self.analysis_params = sport_config['analysis_parameters']
        self.video_types = {vt['id']: vt for vt in sport_config['video_types']}
        
        # MediaPipe pose detector
        base_options = python.BaseOptions(
            model_asset_path='pose_landmarker_heavy.task'
        )
        options = vision.PoseLandmarkerOptions(
            base_options=base_options,
            output_segmentation_masks=True,
            num_poses=1
        )
        self.detector = vision.PoseLandmarker.create_from_options(options)
        
        # Storage client for GCS
        self.storage_client = storage.Client()
        
        # Landmark indices
        self.landmarks = {
            'nose': 0, 'left_eye': 2, 'right_eye': 5,
            'left_shoulder': 11, 'right_shoulder': 12,
            'left_elbow': 13, 'right_elbow': 14,
            'left_wrist': 15, 'right_wrist': 16,
            'left_hip': 23, 'right_hip': 24,
            'left_knee': 25, 'right_knee': 26,
            'left_ankle': 27, 'right_ankle': 28
        }
    
    def process_video(self, video_url: str, video_type: str, 
                     athlete_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main processing pipeline
        
        Args:
            video_url: GCS URL to video file
            video_type: Type of video (e.g., 'free_kick', 'jump_shot')
            athlete_data: Athlete information including height, weight, etc.
            
        Returns:
            Complete analysis results dictionary
        """
        print(f"[{self.sport_name}] Processing {video_type} video...")
        
        # 1. Download video from GCS
        video_path = self.download_video(video_url)
        
        # 2. Extract pose landmarks
        print("Extracting pose landmarks...")
        landmarks_data = self.extract_pose_landmarks(video_path)
        
        # 3. Sport-specific analysis
        print("Running sport-specific analysis...")
        analysis_results = self.analyze_movement(landmarks_data, video_type, athlete_data)
        
        # 4. Compare to baselines
        print("Comparing to baselines...")
        comparison = self.compare_to_baseline(analysis_results, athlete_data)
        
        # 5. Detect phases
        print("Detecting movement phases...")
        phases = self.detect_phases(landmarks_data, video_type)
        
        # 6. Generate insights
        print("Generating insights...")
        insights = self.generate_insights(comparison, phases)
        
        # 7. Create report data
        print("Creating report data...")
        report_data = self.create_report_data(
            analysis_results, comparison, phases, insights, athlete_data
        )
        
        return report_data
    
    def download_video(self, video_url: str) -> str:
        """Download video from GCS to local temp file"""
        # Extract bucket and blob from gs:// URL
        if video_url.startswith('gs://'):
            parts = video_url[5:].split('/', 1)
            bucket_name = parts[0]
            blob_name = parts[1]
        else:
            # Handle if it's already a local file
            return video_url
        
        bucket = self.storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_name)
        
        local_path = f'/tmp/{blob_name.split("/")[-1]}'
        blob.download_to_filename(local_path)
        
        return local_path
    
    def extract_pose_landmarks(self, video_path: str) -> List[Dict[str, Any]]:
        """
        Extract pose landmarks from video using MediaPipe
        
        Returns:
            List of landmark data per frame
        """
        cap = cv2.VideoCapture(video_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        
        landmarks_data = []
        frame_idx = 0
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            # Convert to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
            
            # Detect pose
            result = self.detector.detect(mp_image)
            
            if result.pose_landmarks:
                landmarks = result.pose_landmarks[0]
                
                # Extract landmark positions
                frame_data = {
                    'frame': frame_idx,
                    'timestamp': frame_idx / fps,
                    'landmarks': {}
                }
                
                for name, idx in self.landmarks.items():
                    landmark = landmarks[idx]
                    frame_data['landmarks'][name] = {
                        'x': landmark.x,
                        'y': landmark.y,
                        'z': landmark.z,
                        'visibility': landmark.visibility
                    }
                
                landmarks_data.append(frame_data)
            
            frame_idx += 1
        
        cap.release()
        return landmarks_data
    
    @abstractmethod
    def analyze_movement(self, landmarks_data: List[Dict], video_type: str,
                        athlete_data: Dict) -> Dict[str, float]:
        """
        Perform sport-specific movement analysis
        
        Must be implemented by each sport analyzer
        
        Returns:
            Dictionary of measured metrics
        """
        pass
    
    @abstractmethod
    def detect_phases(self, landmarks_data: List[Dict], video_type: str) -> List[Dict]:
        """
        Detect movement phases in the video
        
        Must be implemented by each sport analyzer
        
        Returns:
            List of detected phases with start/end frames
        """
        pass
    
    def compare_to_baseline(self, analysis_results: Dict[str, float],
                           athlete_data: Dict) -> Dict[str, Dict]:
        """
        Compare measured metrics to sport baselines
        
        Args:
            analysis_results: Measured metrics
            athlete_data: Athlete information (may include custom baselines)
            
        Returns:
            Comparison results for each metric
        """
        comparison = {}
        
        for metric_name, measured_value in analysis_results.items():
            if metric_name in self.baselines:
                baseline = self.baselines[metric_name]
                
                # Calculate deviation
                deviation = self.calculate_deviation(
                    measured_value,
                    baseline['min'],
                    baseline['max']
                )
                
                # Determine status
                status = self.get_metric_status(
                    measured_value,
                    baseline['min'],
                    baseline['max'],
                    baseline.get('optimal')
                )
                
                comparison[metric_name] = {
                    'measured': measured_value,
                    'baseline_min': baseline['min'],
                    'baseline_max': baseline['max'],
                    'baseline_optimal': baseline.get('optimal'),
                    'deviation_percent': deviation,
                    'status': status,
                    'unit': baseline['unit'],
                    'description': baseline.get('description', '')
                }
        
        return comparison
    
    def calculate_deviation(self, measured: float, baseline_min: float,
                          baseline_max: float) -> float:
        """
        Calculate percentage deviation from baseline range
        
        Returns:
            Positive if above range, negative if below, 0 if within
        """
        if baseline_min <= measured <= baseline_max:
            return 0.0
        elif measured < baseline_min:
            return -((baseline_min - measured) / baseline_min * 100)
        else:
            return (measured - baseline_max) / baseline_max * 100
    
    def get_metric_status(self, measured: float, baseline_min: float,
                         baseline_max: float, optimal: float = None) -> str:
        """
        Determine metric status: normal, attention, warning, critical
        """
        deviation = abs(self.calculate_deviation(measured, baseline_min, baseline_max))
        
        if deviation == 0:
            return 'normal'
        elif deviation < 10:
            return 'attention'
        elif deviation < 25:
            return 'warning'
        else:
            return 'critical'
    
    def generate_insights(self, comparison: Dict, phases: List[Dict]) -> List[Dict]:
        """
        Generate insights based on analysis and comparison
        
        Returns:
            List of insights with priority and recommendations
        """
        insights = []
        
        # Check for metrics outside baseline
        for metric_name, comp in comparison.items():
            if comp['status'] in ['warning', 'critical']:
                insights.append({
                    'type': 'baseline_deviation',
                    'metric': metric_name,
                    'severity': comp['status'],
                    'message': f"{metric_name} is {abs(comp['deviation_percent']):.1f}% "
                              f"{'above' if comp['deviation_percent'] > 0 else 'below'} baseline",
                    'recommendation': self.get_recommendation_for_metric(metric_name, comp)
                })
        
        # Check for asymmetries
        asymmetry_insights = self.detect_asymmetries(comparison)
        insights.extend(asymmetry_insights)
        
        # Phase-specific insights
        phase_insights = self.analyze_phases(phases)
        insights.extend(phase_insights)
        
        return insights
    
    def detect_asymmetries(self, comparison: Dict) -> List[Dict]:
        """Detect left/right asymmetries in movement"""
        # To be implemented based on sport-specific needs
        return []
    
    def analyze_phases(self, phases: List[Dict]) -> List[Dict]:
        """Analyze detected movement phases"""
        # To be implemented based on sport-specific needs
        return []
    
    @abstractmethod
    def get_recommendation_for_metric(self, metric_name: str, comparison: Dict) -> str:
        """
        Get sport-specific recommendation for a metric deviation
        
        Must be implemented by each sport analyzer
        """
        pass
    
    def create_report_data(self, analysis_results: Dict, comparison: Dict,
                          phases: List[Dict], insights: List[Dict],
                          athlete_data: Dict) -> Dict[str, Any]:
        """
        Create structured report data
        
        Returns:
            Complete report data dictionary
        """
        # Calculate overall status
        statuses = [comp['status'] for comp in comparison.values()]
        if 'critical' in statuses:
            overall_status = 'critical'
        elif 'warning' in statuses:
            overall_status = 'warning'
        elif 'attention' in statuses:
            overall_status = 'attention'
        else:
            overall_status = 'excellent'
        
        report_data = {
            'sport': self.sport_name,
            'sport_id': self.sport_id,
            'analysis_timestamp': datetime.now().isoformat(),
            'athlete': {
                'name': f"{athlete_data.get('first_name', '')} {athlete_data.get('last_name', '')}",
                'height_cm': athlete_data.get('height_cm'),
                'weight_kg': athlete_data.get('weight_kg'),
                'position': athlete_data.get('position')
            },
            'overall_status': overall_status,
            'measured_metrics': analysis_results,
            'baseline_comparison': comparison,
            'detected_phases': phases,
            'insights': insights,
            'recommendations': self.generate_recommendations(insights),
            'metadata': {
                'analyzer_version': '1.0',
                'confidence_threshold': 0.5
            }
        }
        
        return report_data
    
    def generate_recommendations(self, insights: List[Dict]) -> List[str]:
        """Generate actionable recommendations from insights"""
        recommendations = []
        
        # Sort insights by severity
        critical_insights = [i for i in insights if i.get('severity') == 'critical']
        warning_insights = [i for i in insights if i.get('severity') == 'warning']
        
        # Add critical recommendations first
        for insight in critical_insights:
            if 'recommendation' in insight:
                recommendations.append(f"⚠️ PRIORITY: {insight['recommendation']}")
        
        # Add warning recommendations
        for insight in warning_insights:
            if 'recommendation' in insight:
                recommendations.append(f"⚡ {insight['recommendation']}")
        
        return recommendations
    
    def calculate_angle(self, point1: Dict, point2: Dict, point3: Dict) -> float:
        """Calculate angle between three points"""
        vector1 = np.array([point1['x'] - point2['x'], point1['y'] - point2['y']])
        vector2 = np.array([point3['x'] - point2['x'], point3['y'] - point2['y']])
        
        cosine_angle = np.dot(vector1, vector2) / (
            np.linalg.norm(vector1) * np.linalg.norm(vector2)
        )
        angle = np.arccos(np.clip(cosine_angle, -1.0, 1.0))
        
        return np.degrees(angle)
    
    def calculate_distance(self, point1: Dict, point2: Dict) -> float:
        """Calculate Euclidean distance between two points"""
        return np.sqrt(
            (point1['x'] - point2['x'])**2 +
            (point1['y'] - point2['y'])**2 +
            (point1['z'] - point2['z'])**2
        )
