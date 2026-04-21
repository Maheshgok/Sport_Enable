# Cloud Run Service for Assessment Analysis
# This service analyzes videos according to predefined assessment prompts or custom protocols

import os
import json
import cv2
import numpy as np
from flask import Flask, request, jsonify
from google.cloud import storage, firestore
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import tempfile
import shutil
from datetime import datetime
import requests

app = Flask(__name__)

# Initialize clients
storage_client = storage.Client()
db = firestore.Client()

# MediaPipe setup
base_options = python.BaseOptions(model_asset_path='pose_landmarker_heavy.task')
options = vision.PoseLandmarkerOptions(
    base_options=base_options,
    output_segmentation_masks=True,
    num_poses=1
)
detector = vision.PoseLandmarker.create_from_options(options)

def download_video_from_gcs(gcs_url):
    """Download video from GCS to temp file"""
    bucket_name = gcs_url.split('/')[2]
    blob_path = '/'.join(gcs_url.split('/')[3:])

    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_path)

    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
    blob.download_to_filename(temp_file.name)
    return temp_file.name

def analyze_video_with_config(video_path, analysis_config):
    """Analyze video according to analysis configuration"""
    cap = cv2.VideoCapture(video_path)
    results = []

    joints_to_track = analysis_config.get('joints_to_track', [])
    angles_to_measure = analysis_config.get('angles_to_measure', [])
    metrics_to_calculate = analysis_config.get('metrics_to_calculate', [])

    frame_count = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Convert to RGB for MediaPipe
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

        # Detect pose
        detection_result = detector.detect(mp_image)

        if detection_result.pose_landmarks:
            landmarks = detection_result.pose_landmarks[0]

            frame_data = {
                'frame': frame_count,
                'timestamp': cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0,
                'landmarks': {}
            }

            # Extract specified joints
            landmark_indices = {
                'nose': 0, 'left_eye': 2, 'right_eye': 5, 'left_ear': 7, 'right_ear': 8,
                'left_shoulder': 11, 'right_shoulder': 12, 'left_elbow': 13, 'right_elbow': 14,
                'left_wrist': 15, 'right_wrist': 16, 'left_hip': 23, 'right_hip': 24,
                'left_knee': 25, 'right_knee': 26, 'left_ankle': 27, 'right_ankle': 28,
                'left_heel': 29, 'right_heel': 30, 'left_foot_index': 31, 'right_foot_index': 32
            }

            for joint_name in joints_to_track:
                if joint_name in landmark_indices:
                    idx = landmark_indices[joint_name]
                    landmark = landmarks[idx]
                    frame_data['landmarks'][joint_name] = {
                        'x': landmark.x,
                        'y': landmark.y,
                        'z': landmark.z,
                        'visibility': landmark.visibility
                    }

            # Calculate specified angles
            frame_data['angles'] = {}
            for angle_name in angles_to_measure:
                angle_value = calculate_angle(angle_name, landmarks, landmark_indices)
                if angle_value is not None:
                    frame_data['angles'][angle_name] = angle_value

            results.append(frame_data)

        frame_count += 1
        if frame_count > 300:  # Limit to 10 seconds at 30fps
            break

    cap.release()
    return results

def calculate_angle(angle_name, landmarks, landmark_indices):
    """Calculate specific joint angles"""
    try:
        if angle_name == 'knee_flexion':
            # Left knee angle
            hip = np.array([landmarks[landmark_indices['left_hip']].x, landmarks[landmark_indices['left_hip']].y])
            knee = np.array([landmarks[landmark_indices['left_knee']].x, landmarks[landmark_indices['left_knee']].y])
            ankle = np.array([landmarks[landmark_indices['left_ankle']].x, landmarks[landmark_indices['left_ankle']].y])

            v1 = hip - knee
            v2 = ankle - knee
            cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
            angle = np.arccos(np.clip(cos_angle, -1, 1))
            return np.degrees(angle)

        elif angle_name == 'hip_angle':
            # Left hip angle
            shoulder = np.array([landmarks[landmark_indices['left_shoulder']].x, landmarks[landmark_indices['left_shoulder']].y])
            hip = np.array([landmarks[landmark_indices['left_hip']].x, landmarks[landmark_indices['left_hip']].y])
            knee = np.array([landmarks[landmark_indices['left_knee']].x, landmarks[landmark_indices['left_knee']].y])

            v1 = shoulder - hip
            v2 = knee - hip
            cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
            angle = np.arccos(np.clip(cos_angle, -1, 1))
            return np.degrees(angle)

        elif angle_name == 'shoulder_elevation':
            # Left shoulder elevation
            shoulder = np.array([landmarks[landmark_indices['left_shoulder']].x, landmarks[landmark_indices['left_shoulder']].y])
            elbow = np.array([landmarks[landmark_indices['left_elbow']].x, landmarks[landmark_indices['left_elbow']].y])

            # Reference vector (straight down)
            ref_vector = np.array([0, 1])
            arm_vector = elbow - shoulder

            cos_angle = np.dot(ref_vector, arm_vector) / (np.linalg.norm(ref_vector) * np.linalg.norm(arm_vector))
            angle = np.arccos(np.clip(cos_angle, -1, 1))
            return np.degrees(angle)

    except:
        return None

    return None

def generate_report(analysis_results, analysis_config):
    """Generate report based on analysis configuration"""
    report = {
        'summary': {},
        'metrics': {},
        'flagged_issues': [],
        'recommendations': []
    }

    # Calculate summary metrics
    if analysis_results:
        all_angles = {}
        for frame in analysis_results:
            for angle_name, angle_value in frame.get('angles', {}).items():
                if angle_name not in all_angles:
                    all_angles[angle_name] = []
                all_angles[angle_name].append(angle_value)

        for angle_name, values in all_angles.items():
            if values:
                report['metrics'][f'{angle_name}_avg'] = np.mean(values)
                report['metrics'][f'{angle_name}_min'] = np.min(values)
                report['metrics'][f'{angle_name}_max'] = np.max(values)

    # Check against baseline metrics
    baseline_metrics = analysis_config.get('baseline_metrics', {})
    risk_factors = analysis_config.get('risk_factors', {})

    for metric_name, value in report['metrics'].items():
        if metric_name in baseline_metrics:
            baseline = baseline_metrics[metric_name]
            if isinstance(baseline, dict):
                min_val = baseline.get('min')
                max_val = baseline.get('max')
                if min_val is not None and value < min_val:
                    report['flagged_issues'].append(f'{metric_name} below normal range: {value:.1f} < {min_val}')
                if max_val is not None and value > max_val:
                    report['flagged_issues'].append(f'{metric_name} above normal range: {value:.1f} > {max_val}')

    return report

@app.route('/analyze', methods=['POST'])
def analyze_assessment():
    """Main analysis endpoint for both prompts and custom protocols"""
    try:
        data = request.get_json()

        execution_type = data.get('execution_type', 'prompt')  # 'prompt' or 'custom_protocol'
        execution_id = data.get('execution_id')
        analysis_config = data.get('analysis_config', {})
        video_urls = data.get('video_urls', {})

        if not execution_id or not analysis_config:
            return jsonify({'error': 'execution_id and analysis_config required'}), 400

        # Determine collection based on execution type
        if execution_type == 'prompt':
            collection_name = 'prompt_executions'
        else:
            collection_name = 'custom_protocol_executions'

        # Update execution status
        execution_ref = db.collection(collection_name).document(execution_id)
        execution_ref.update({
            'status': 'processing',
            'processing_started_at': datetime.now()
        })

        analysis_results = {}

        # Process each video
        for view_name, gcs_url in video_urls.items():
            if gcs_url:
                video_path = download_video_from_gcs(gcs_url)
                try:
                    results = analyze_video_with_config(video_path, analysis_config)
                    analysis_results[view_name] = results
                finally:
                    os.unlink(video_path)

        # Generate report
        report = generate_report(analysis_results, analysis_config)

        # Update execution with results
        execution_ref.update({
            'status': 'completed',
            'processing_completed_at': datetime.now(),
            'analysis_results': analysis_results,
            'report_data': report,
            'flagged_issues': report['flagged_issues']
        })

        return jsonify({
            'success': True,
            'execution_id': execution_id,
            'execution_type': execution_type,
            'analysis_results': analysis_results,
            'report': report
        }), 200

    except Exception as e:
        # Update execution with error
        if 'execution_id' in locals() and 'collection_name' in locals():
            execution_ref = db.collection(collection_name).document(execution_id)
            execution_ref.update({
                'status': 'failed',
                'error_message': str(e)
            })

        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'service': 'protocol-analysis'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))