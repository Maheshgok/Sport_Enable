"""
Football-Specific Analyzer
Analyzes football/soccer movements
"""

from base_analyzer import BaseSportAnalyzer
from typing import Dict, List, Any
import numpy as np
from scipy.signal import find_peaks


class FootballAnalyzer(BaseSportAnalyzer):
    """Football/Soccer specific motion analysis"""
    
    def analyze_movement(self, landmarks_data: List[Dict], video_type: str,
                        athlete_data: Dict) -> Dict[str, float]:
        """
        Analyze football-specific movements
        
        Args:
            landmarks_data: Pose landmarks per frame
            video_type: Type of movement (free_kick, sprint, dribbling, passing)
            athlete_data: Athlete information
            
        Returns:
            Dictionary of measured metrics
        """
        if video_type == 'free_kick':
            return self.analyze_free_kick(landmarks_data, athlete_data)
        elif video_type == 'sprint':
            return self.analyze_sprint(landmarks_data, athlete_data)
        elif video_type == 'dribbling':
            return self.analyze_dribbling(landmarks_data, athlete_data)
        elif video_type == 'passing':
            return self.analyze_passing(landmarks_data, athlete_data)
        else:
            raise ValueError(f"Unknown video type: {video_type}")
    
    def analyze_free_kick(self, landmarks_data: List[Dict], 
                         athlete_data: Dict) -> Dict[str, float]:
        """Analyze free kick technique"""
        
        # Find kick frame (highest foot velocity)
        kick_frame_idx = self.find_kick_frame(landmarks_data)
        
        if kick_frame_idx is None:
            return {}
        
        # Get key frames
        approach_frames = landmarks_data[max(0, kick_frame_idx-10):kick_frame_idx]
        strike_frame = landmarks_data[kick_frame_idx]
        follow_frames = landmarks_data[kick_frame_idx:min(len(landmarks_data), kick_frame_idx+10)]
        
        metrics = {}
        
        # 1. Approach angle (relative to target)
        if len(approach_frames) > 2:
            approach_angle = self.calculate_approach_angle(approach_frames)
            metrics['approach_angle'] = approach_angle
        
        # 2. Plant foot distance from ball (estimated)
        plant_distance = self.estimate_plant_foot_distance(strike_frame)
        metrics['plant_foot_distance'] = plant_distance
        
        # 3. Knee flexion angle at strike
        knee_angle = self.calculate_angle(
            strike_frame['landmarks']['left_hip'],
            strike_frame['landmarks']['left_knee'],
            strike_frame['landmarks']['left_ankle']
        )
        metrics['knee_flexion_angle'] = knee_angle
        
        # 4. Hip rotation
        hip_rotation = self.calculate_hip_rotation(approach_frames, strike_frame)
        metrics['hip_rotation'] = hip_rotation
        
        # 5. Ankle dorsiflexion
        ankle_angle = self.calculate_ankle_angle(strike_frame)
        metrics['ankle_dorsiflexion'] = ankle_angle
        
        # 6. Follow-through height
        if len(follow_frames) > 0:
            follow_height = self.calculate_follow_through_height(follow_frames)
            metrics['follow_through_height'] = follow_height
        
        return metrics
    
    def analyze_sprint(self, landmarks_data: List[Dict],
                      athlete_data: Dict) -> Dict[str, float]:
        """Analyze sprinting mechanics"""
        
        metrics = {}
        
        # 1. Calculate sprint speed
        speed = self.calculate_sprint_speed(landmarks_data, athlete_data.get('height_cm', 170))
        metrics['sprint_speed'] = speed
        
        # 2. Calculate stride length
        stride_length = self.calculate_stride_length(landmarks_data, athlete_data.get('height_cm', 170))
        metrics['stride_length'] = stride_length
        
        # 3. Calculate cadence (steps per minute)
        cadence = self.calculate_cadence(landmarks_data)
        metrics['cadence'] = cadence
        
        # 4. Knee drive (max knee flexion during swing)
        knee_drive = self.calculate_max_knee_drive(landmarks_data)
        metrics['knee_drive'] = knee_drive
        
        # 5. Arm swing coordination
        arm_swing = self.calculate_arm_swing(landmarks_data)
        metrics['arm_swing'] = arm_swing
        
        return metrics
    
    def analyze_dribbling(self, landmarks_data: List[Dict],
                         athlete_data: Dict) -> Dict[str, float]:
        """Analyze dribbling technique"""
        
        metrics = {}
        
        # 1. Body balance (center of mass stability)
        balance_score = self.calculate_balance_stability(landmarks_data)
        metrics['balance_score'] = balance_score
        
        # 2. Agility (change of direction speed)
        agility_score = self.calculate_agility(landmarks_data)
        metrics['agility_score'] = agility_score
        
        # 3. Hip rotation during turns
        hip_rotation = self.calculate_average_hip_rotation(landmarks_data)
        metrics['hip_rotation'] = hip_rotation
        
        return metrics
    
    def analyze_passing(self, landmarks_data: List[Dict],
                       athlete_data: Dict) -> Dict[str, float]:
        """Analyze passing technique"""
        
        # Similar to free_kick but with different focus
        return self.analyze_free_kick(landmarks_data, athlete_data)
    
    def detect_phases(self, landmarks_data: List[Dict], 
                     video_type: str) -> List[Dict]:
        """
        Detect movement phases in football actions
        
        Returns:
            List of phases with start/end frames
        """
        if video_type == 'free_kick':
            return self.detect_kick_phases(landmarks_data)
        elif video_type == 'sprint':
            return self.detect_sprint_phases(landmarks_data)
        else:
            return []
    
    def detect_kick_phases(self, landmarks_data: List[Dict]) -> List[Dict]:
        """Detect phases in kicking motion"""
        
        # Find kick frame
        kick_frame = self.find_kick_frame(landmarks_data)
        
        if kick_frame is None:
            return []
        
        phases = [
            {
                'name': 'Approach',
                'start_frame': 0,
                'end_frame': max(0, kick_frame - 5),
                'description': 'Player approaching the ball'
            },
            {
                'name': 'Plant',
                'start_frame': max(0, kick_frame - 5),
                'end_frame': kick_frame - 1,
                'description': 'Planting non-kicking foot'
            },
            {
                'name': 'Strike',
                'start_frame': kick_frame - 1,
                'end_frame': kick_frame + 1,
                'description': 'Contact with ball'
            },
            {
                'name': 'Follow Through',
                'start_frame': kick_frame + 1,
                'end_frame': min(len(landmarks_data), kick_frame + 10),
                'description': 'Follow-through motion'
            }
        ]
        
        return phases
    
    def detect_sprint_phases(self, landmarks_data: List[Dict]) -> List[Dict]:
        """Detect stride phases in sprinting"""
        
        # Detect heel strikes (local minima in foot height)
        heel_strikes = self.detect_heel_strikes(landmarks_data)
        
        phases = []
        for i in range(len(heel_strikes) - 1):
            phases.append({
                'name': f'Stride {i+1}',
                'start_frame': heel_strikes[i],
                'end_frame': heel_strikes[i+1],
                'description': 'Complete stride cycle'
            })
        
        return phases
    
    def get_recommendation_for_metric(self, metric_name: str, 
                                     comparison: Dict) -> str:
        """Get sport-specific recommendations"""
        
        recommendations = {
            'knee_flexion_angle': {
                'low': "Increase knee flexion during strike. Work on flexibility exercises.",
                'high': "Excessive knee flexion may reduce power. Focus on optimal contact position."
            },
            'hip_rotation': {
                'low': "Insufficient hip rotation. Practice hip mobility and rotational drills.",
                'high': "Excessive hip rotation may cause imbalance. Focus on core stability."
            },
            'sprint_speed': {
                'low': "Work on sprint mechanics and explosive power training.",
                'high': "Excellent sprint speed! Maintain through proper conditioning."
            },
            'plant_foot_distance': {
                'low': "Plant foot too close to ball. May reduce power and accuracy.",
                'high': "Plant foot too far from ball. Move planting foot closer."
            }
        }
        
        if metric_name in recommendations:
            is_low = comparison['deviation_percent'] < 0
            return recommendations[metric_name]['low' if is_low else 'high']
        else:
            return f"Consult with coach about {metric_name} optimization."
    
    # Helper methods
    
    def find_kick_frame(self, landmarks_data: List[Dict]) -> int:
        """Find frame where kick occurs (max foot velocity)"""
        velocities = []
        
        for i in range(1, len(landmarks_data)):
            prev = landmarks_data[i-1]['landmarks']['right_ankle']
            curr = landmarks_data[i]['landmarks']['right_ankle']
            
            velocity = np.sqrt(
                (curr['x'] - prev['x'])**2 +
                (curr['y'] - prev['y'])**2
            )
            velocities.append(velocity)
        
        if not velocities:
            return None
        
        return np.argmax(velocities) + 1
    
    def calculate_approach_angle(self, approach_frames: List[Dict]) -> float:
        """Calculate approach angle"""
        if len(approach_frames) < 2:
            return 0.0
        
        # Calculate movement direction vector
        first = approach_frames[0]['landmarks']['left_hip']
        last = approach_frames[-1]['landmarks']['left_hip']
        
        angle = np.arctan2(last['y'] - first['y'], last['x'] - first['x'])
        return abs(np.degrees(angle))
    
    def estimate_plant_foot_distance(self, strike_frame: Dict) -> float:
        """Estimate plant foot distance from ball (simplified)"""
        # In real implementation, would need ball detection
        # For now, estimate based on hip-ankle distance
        hip = strike_frame['landmarks']['left_hip']
        ankle = strike_frame['landmarks']['left_ankle']
        
        distance = self.calculate_distance(hip, ankle)
        return distance * 100  # Convert to cm (approximate)
    
    def calculate_hip_rotation(self, approach_frames: List[Dict],
                              strike_frame: Dict) -> float:
        """Calculate hip rotation from approach to strike"""
        if len(approach_frames) < 1:
            return 0.0
        
        # Hip orientation in approach
        approach = approach_frames[-1]['landmarks']
        left_hip_a = approach['left_hip']
        right_hip_a = approach['right_hip']
        
        # Hip orientation at strike
        strike = strike_frame['landmarks']
        left_hip_s = strike['left_hip']
        right_hip_s = strike['right_hip']
        
        # Calculate hip angle change
        angle_approach = np.arctan2(
            right_hip_a['y'] - left_hip_a['y'],
            right_hip_a['x'] - left_hip_a['x']
        )
        
        angle_strike = np.arctan2(
            right_hip_s['y'] - left_hip_s['y'],
            right_hip_s['x'] - left_hip_s['x']
        )
        
        rotation = abs(np.degrees(angle_strike - angle_approach))
        return min(rotation, 180)  # Cap at 180 degrees
    
    def calculate_ankle_angle(self, frame: Dict) -> float:
        """Calculate ankle dorsiflexion angle"""
        return self.calculate_angle(
            frame['landmarks']['left_knee'],
            frame['landmarks']['left_ankle'],
            {'x': frame['landmarks']['left_ankle']['x'],
             'y': frame['landmarks']['left_ankle']['y'] + 0.1,
             'z': frame['landmarks']['left_ankle']['z']}
        )
    
    def calculate_follow_through_height(self, follow_frames: List[Dict]) -> float:
        """Calculate maximum height of follow-through"""
        max_height = 0
        
        for frame in follow_frames:
            height = 1.0 - frame['landmarks']['right_ankle']['y']
            max_height = max(max_height, height)
        
        return max_height * 100  # Convert to relative percentage
    
    def calculate_sprint_speed(self, landmarks_data: List[Dict], 
                              height_cm: float) -> float:
        """Estimate sprint speed"""
        # Simplified calculation based on hip movement
        if len(landmarks_data) < 10:
            return 0.0
        
        fps = 30  # Assume 30 fps
        time_window = len(landmarks_data) / fps
        
        # Calculate hip displacement
        first_hip = landmarks_data[0]['landmarks']['left_hip']
        last_hip = landmarks_data[-1]['landmarks']['left_hip']
        
        displacement = abs(last_hip['x'] - first_hip['x'])
        
        # Scale by height (pixels to meters conversion)
        displacement_meters = displacement * (height_cm / 100)
        
        speed = displacement_meters / time_window
        return speed
    
    def calculate_stride_length(self, landmarks_data: List[Dict],
                               height_cm: float) -> float:
        """Calculate average stride length"""
        heel_strikes = self.detect_heel_strikes(landmarks_data)
        
        if len(heel_strikes) < 2:
            return 0.0
        
        # Calculate distance between heel strikes
        total_distance = 0
        for i in range(len(heel_strikes) - 1):
            frame1 = landmarks_data[heel_strikes[i]]['landmarks']['right_ankle']
            frame2 = landmarks_data[heel_strikes[i+1]]['landmarks']['right_ankle']
            
            distance = abs(frame2['x'] - frame1['x'])
            total_distance += distance
        
        avg_distance = total_distance / (len(heel_strikes) - 1)
        return avg_distance * (height_cm / 100)  # Scale to meters
    
    def calculate_cadence(self, landmarks_data: List[Dict]) -> float:
        """Calculate steps per minute"""
        heel_strikes = self.detect_heel_strikes(landmarks_data)
        
        if len(heel_strikes) < 2:
            return 0.0
        
        fps = 30
        total_time_seconds = len(landmarks_data) / fps
        total_steps = len(heel_strikes)
        
        cadence = (total_steps / total_time_seconds) * 60
        return cadence
    
    def detect_heel_strikes(self, landmarks_data: List[Dict]) -> List[int]:
        """Detect heel strike frames"""
        ankle_heights = [
            frame['landmarks']['right_ankle']['y']
            for frame in landmarks_data
        ]
        
        # Find local minima (heel strikes)
        peaks, _ = find_peaks([-h for h in ankle_heights], distance=10)
        return list(peaks)
    
    def calculate_max_knee_drive(self, landmarks_data: List[Dict]) -> float:
        """Calculate maximum knee drive angle"""
        max_angle = 0
        
        for frame in landmarks_data:
            angle = self.calculate_angle(
                frame['landmarks']['left_hip'],
                frame['landmarks']['left_knee'],
                frame['landmarks']['left_ankle']
            )
            max_angle = max(max_angle, angle)
        
        return max_angle
    
    def calculate_arm_swing(self, landmarks_data: List[Dict]) -> float:
        """Calculate arm swing range (simplified)"""
        elbow_ranges = []
        
        for frame in landmarks_data:
            angle = self.calculate_angle(
                frame['landmarks']['left_shoulder'],
                frame['landmarks']['left_elbow'],
                frame['landmarks']['left_wrist']
            )
            elbow_ranges.append(angle)
        
        return max(elbow_ranges) - min(elbow_ranges)
    
    def calculate_balance_stability(self, landmarks_data: List[Dict]) -> float:
        """Calculate balance/stability score"""
        # Calculate CoM (center of mass) variability
        com_positions = []
        
        for frame in landmarks_data:
            # Approximate CoM as average of hips
            left_hip = frame['landmarks']['left_hip']
            right_hip = frame['landmarks']['right_hip']
            
            com_x = (left_hip['x'] + right_hip['x']) / 2
            com_y = (left_hip['y'] + right_hip['y']) / 2
            
            com_positions.append((com_x, com_y))
        
        # Calculate standard deviation (lower = better stability)
        std_x = np.std([pos[0] for pos in com_positions])
        std_y = np.std([pos[1] for pos in com_positions])
        
        # Convert to score (0-100, higher is better)
        stability_score = max(0, 100 - (std_x + std_y) * 1000)
        return stability_score
    
    def calculate_agility(self, landmarks_data: List[Dict]) -> float:
        """Calculate agility score"""
        # Measure hip direction changes
        direction_changes = 0
        
        for i in range(2, len(landmarks_data)):
            prev_hip = landmarks_data[i-2]['landmarks']['left_hip']
            curr_hip = landmarks_data[i-1]['landmarks']['left_hip']
            next_hip = landmarks_data[i]['landmarks']['left_hip']
            
            # Calculate direction vectors
            dir1_x = curr_hip['x'] - prev_hip['x']
            dir2_x = next_hip['x'] - curr_hip['x']
            
            # Check for direction change
            if dir1_x * dir2_x < 0:
                direction_changes += 1
        
        # Higher number of direction changes = better agility
        return min(100, direction_changes * 10)
    
    def calculate_average_hip_rotation(self, landmarks_data: List[Dict]) -> float:
        """Calculate average hip rotation"""
        rotations = []
        
        for frame in landmarks_data:
            left_hip = frame['landmarks']['left_hip']
            right_hip = frame['landmarks']['right_hip']
            
            angle = np.arctan2(
                right_hip['y'] - left_hip['y'],
                right_hip['x'] - left_hip['x']
            )
            rotations.append(abs(np.degrees(angle)))
        
        return np.mean(rotations) if rotations else 0.0
