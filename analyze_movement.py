"""
Example script for analyzing the output data from Video Annotation Tool
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import glob

def analyze_movement_data(frame_data_csv):
    """
    Analyze movement data from the video annotation tool
    """
    # Load data
    df = pd.read_csv(frame_data_csv)
    
    print("=" * 70)
    print(f"MOVEMENT ANALYSIS: {os.path.basename(frame_data_csv)}")
    print("=" * 70)
    print(f"\nTotal frames: {len(df)}")
    print(f"Duration: {df['timestamp_sec'].max():.2f} seconds")
    print(f"Average FPS: {len(df) / df['timestamp_sec'].max():.1f}")
    
    # Analyze key joint movements
    print("\n" + "=" * 70)
    print("KEY JOINT ANGLES")
    print("=" * 70)
    
    angle_cols = [col for col in df.columns if 'angle' in col]
    for col in angle_cols:
        print(f"\n{col.replace('_', ' ').title()}:")
        print(f"  Range: {df[col].min():.1f}° to {df[col].max():.1f}°")
        print(f"  Mean: {df[col].mean():.1f}°")
        print(f"  Movement: {df[col].max() - df[col].min():.1f}°")
        
        # Find frames with max/min
        max_frame = df.loc[df[col].idxmax(), 'frame']
        min_frame = df.loc[df[col].idxmin(), 'frame']
        print(f"  Max at frame: {max_frame} ({df.loc[df[col].idxmax(), 'timestamp_sec']:.2f}s)")
        print(f"  Min at frame: {min_frame} ({df.loc[df[col].idxmin(), 'timestamp_sec']:.2f}s)")
    
    # Knee-hip relationship analysis
    print("\n" + "=" * 70)
    print("KNEE-HIP RELATIONSHIP")
    print("=" * 70)
    
    for side in ['left', 'right']:
        col = f'{side}_knee_hip_distance'
        if col in df.columns:
            print(f"\n{side.title()} Side:")
            
            # Positive = knee below hip, Negative = knee above hip
            above_hip_frames = df[df[col] < 0]
            below_hip_frames = df[df[col] > 0]
            
            print(f"  Max knee lift (above hip): {abs(df[col].min()):.4f} units")
            print(f"  Max knee drop (below hip): {df[col].max():.4f} units")
            print(f"  Frames with knee above hip: {len(above_hip_frames)} ({100*len(above_hip_frames)/len(df):.1f}%)")
            print(f"  Frames with knee below hip: {len(below_hip_frames)} ({100*len(below_hip_frames)/len(df):.1f}%)")
    
    # Calculate joint velocities
    print("\n" + "=" * 70)
    print("JOINT MOVEMENT VELOCITY")
    print("=" * 70)
    
    joints = ['left_knee', 'right_knee', 'left_hip', 'right_hip', 
              'left_shoulder', 'right_shoulder', 'left_ankle', 'right_ankle',
              'left_elbow', 'right_elbow', 'left_wrist', 'right_wrist']
    
    velocities = []
    for joint in joints:
        if f'{joint}_x' in df.columns:
            dx = df[f'{joint}_x'].diff()
            dy = df[f'{joint}_y'].diff()
            dz = df[f'{joint}_z'].diff()
            velocity = np.sqrt(dx**2 + dy**2 + dz**2)
            
            velocities.append({
                'joint': joint,
                'max_velocity': velocity.max(),
                'mean_velocity': velocity.mean(),
                'total_movement': velocity.sum()
            })
    
    velocity_df = pd.DataFrame(velocities).sort_values('total_movement', ascending=False)
    
    print("\nMost Active Joints (by total movement):")
    for idx, row in velocity_df.head(5).iterrows():
        print(f"  {row['joint'].replace('_', ' ').title()}: {row['total_movement']:.4f}")
    
    # Body symmetry analysis
    print("\n" + "=" * 70)
    print("BODY SYMMETRY ANALYSIS")
    print("=" * 70)
    
    symmetry_pairs = [
        ('left_knee_angle', 'right_knee_angle'),
        ('left_elbow_angle', 'right_elbow_angle'),
        ('left_knee_hip_distance', 'right_knee_hip_distance')
    ]
    
    for left_col, right_col in symmetry_pairs:
        if left_col in df.columns and right_col in df.columns:
            diff = abs(df[left_col] - df[right_col])
            print(f"\n{left_col.replace('_', ' ').title()} vs {right_col.replace('_', ' ').title()}:")
            print(f"  Mean difference: {diff.mean():.2f}")
            print(f"  Max difference: {diff.max():.2f}")
            print(f"  Symmetry score: {100 - (diff.mean() / max(df[left_col].mean(), df[right_col].mean()) * 100):.1f}%")
    
    return df

def plot_joint_movement(df, joint_name, output_path='movement_plot.png'):
    """
    Plot joint movement over time
    """
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    fig.suptitle(f'{joint_name.replace("_", " ").title()} Movement Analysis', fontsize=16)
    
    # X coordinate
    axes[0, 0].plot(df['timestamp_sec'], df[f'{joint_name}_x'], 'b-', linewidth=2)
    axes[0, 0].set_title('Horizontal Position (X)')
    axes[0, 0].set_xlabel('Time (seconds)')
    axes[0, 0].set_ylabel('Position (normalized)')
    axes[0, 0].grid(True, alpha=0.3)
    
    # Y coordinate
    axes[0, 1].plot(df['timestamp_sec'], df[f'{joint_name}_y'], 'r-', linewidth=2)
    axes[0, 1].set_title('Vertical Position (Y)')
    axes[0, 1].set_xlabel('Time (seconds)')
    axes[0, 1].set_ylabel('Position (normalized)')
    axes[0, 1].grid(True, alpha=0.3)
    axes[0, 1].invert_yaxis()  # Invert Y axis (0 = top, 1 = bottom)
    
    # Z coordinate (depth)
    axes[1, 0].plot(df['timestamp_sec'], df[f'{joint_name}_z'], 'g-', linewidth=2)
    axes[1, 0].set_title('Depth Position (Z)')
    axes[1, 0].set_xlabel('Time (seconds)')
    axes[1, 0].set_ylabel('Depth (normalized)')
    axes[1, 0].grid(True, alpha=0.3)
    
    # Velocity
    dx = df[f'{joint_name}_x'].diff()
    dy = df[f'{joint_name}_y'].diff()
    dz = df[f'{joint_name}_z'].diff()
    velocity = np.sqrt(dx**2 + dy**2 + dz**2)
    
    axes[1, 1].plot(df['timestamp_sec'], velocity, 'm-', linewidth=2)
    axes[1, 1].set_title('Movement Velocity')
    axes[1, 1].set_xlabel('Time (seconds)')
    axes[1, 1].set_ylabel('Velocity (units/frame)')
    axes[1, 1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"\n✓ Plot saved: {output_path}")
    plt.close()

def plot_joint_angles(df, output_path='joint_angles.png'):
    """
    Plot all joint angles over time
    """
    angle_cols = [col for col in df.columns if 'angle' in col]
    
    if not angle_cols:
        print("No angle data found in dataset")
        return
    
    fig, axes = plt.subplots(len(angle_cols), 1, figsize=(12, 3*len(angle_cols)))
    if len(angle_cols) == 1:
        axes = [axes]
    
    fig.suptitle('Joint Angles Over Time', fontsize=16)
    
    colors = ['b', 'r', 'g', 'm']
    for idx, col in enumerate(angle_cols):
        axes[idx].plot(df['timestamp_sec'], df[col], 
                      color=colors[idx % len(colors)], linewidth=2)
        axes[idx].set_title(col.replace('_', ' ').title())
        axes[idx].set_xlabel('Time (seconds)')
        axes[idx].set_ylabel('Angle (degrees)')
        axes[idx].grid(True, alpha=0.3)
        axes[idx].axhline(y=90, color='gray', linestyle='--', alpha=0.5, label='90°')
        axes[idx].axhline(y=180, color='gray', linestyle='--', alpha=0.5, label='180°')
        axes[idx].legend()
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✓ Angles plot saved: {output_path}")
    plt.close()

def compare_left_right(df, output_path='left_right_comparison.png'):
    """
    Compare left vs right side movements
    """
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    fig.suptitle('Left vs Right Side Comparison', fontsize=16)
    
    # Knee angles
    if 'left_knee_angle' in df.columns and 'right_knee_angle' in df.columns:
        axes[0, 0].plot(df['timestamp_sec'], df['left_knee_angle'], 'b-', label='Left', linewidth=2)
        axes[0, 0].plot(df['timestamp_sec'], df['right_knee_angle'], 'r-', label='Right', linewidth=2)
        axes[0, 0].set_title('Knee Angles')
        axes[0, 0].set_ylabel('Angle (degrees)')
        axes[0, 0].set_xlabel('Time (seconds)')
        axes[0, 0].legend()
        axes[0, 0].grid(True, alpha=0.3)
    
    # Elbow angles
    if 'left_elbow_angle' in df.columns and 'right_elbow_angle' in df.columns:
        axes[0, 1].plot(df['timestamp_sec'], df['left_elbow_angle'], 'b-', label='Left', linewidth=2)
        axes[0, 1].plot(df['timestamp_sec'], df['right_elbow_angle'], 'r-', label='Right', linewidth=2)
        axes[0, 1].set_title('Elbow Angles')
        axes[0, 1].set_ylabel('Angle (degrees)')
        axes[0, 1].set_xlabel('Time (seconds)')
        axes[0, 1].legend()
        axes[0, 1].grid(True, alpha=0.3)
    
    # Wrist height
    if 'left_wrist_y' in df.columns and 'right_wrist_y' in df.columns:
        axes[1, 0].plot(df['timestamp_sec'], df['left_wrist_y'], 'b-', label='Left', linewidth=2)
        axes[1, 0].plot(df['timestamp_sec'], df['right_wrist_y'], 'r-', label='Right', linewidth=2)
        axes[1, 0].set_title('Wrist Height')
        axes[1, 0].set_ylabel('Vertical Position')
        axes[1, 0].set_xlabel('Time (seconds)')
        axes[1, 0].invert_yaxis()
        axes[1, 0].legend()
        axes[1, 0].grid(True, alpha=0.3)
    
    # Ankle height
    if 'left_ankle_y' in df.columns and 'right_ankle_y' in df.columns:
        axes[1, 1].plot(df['timestamp_sec'], df['left_ankle_y'], 'b-', label='Left', linewidth=2)
        axes[1, 1].plot(df['timestamp_sec'], df['right_ankle_y'], 'r-', label='Right', linewidth=2)
        axes[1, 1].set_title('Ankle Height')
        axes[1, 1].set_ylabel('Vertical Position')
        axes[1, 1].set_xlabel('Time (seconds)')
        axes[1, 1].invert_yaxis()
        axes[1, 1].legend()
        axes[1, 1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✓ Comparison plot saved: {output_path}")
    plt.close()

def main():
    """
    Main analysis function
    """
    import sys
    
    if len(sys.argv) < 2:
        # Try to find most recent CSV in output folder
        csv_files = glob.glob('output/frame_data_*.csv')
        if not csv_files:
            print("Usage: python analyze_movement.py <frame_data_csv>")
            print("Example: python analyze_movement.py output/frame_data_20260326_123456.csv")
            return
        csv_file = max(csv_files, key=os.path.getctime)
        print(f"Using most recent file: {csv_file}")
    else:
        csv_file = sys.argv[1]
    
    if not os.path.exists(csv_file):
        print(f"Error: File not found: {csv_file}")
        return
    
    # Analyze data
    df = analyze_movement_data(csv_file)
    
    # Create output folder for plots
    output_folder = os.path.dirname(csv_file)
    timestamp = os.path.basename(csv_file).replace('frame_data_', '').replace('.csv', '')
    
    # Generate plots
    print("\n" + "=" * 70)
    print("GENERATING VISUALIZATIONS")
    print("=" * 70)
    
    # Plot key joints
    for joint in ['left_knee', 'right_knee', 'left_wrist', 'right_wrist']:
        if f'{joint}_x' in df.columns:
            plot_path = os.path.join(output_folder, f'{joint}_movement_{timestamp}.png')
            plot_joint_movement(df, joint, plot_path)
    
    # Plot angles
    angles_path = os.path.join(output_folder, f'joint_angles_{timestamp}.png')
    plot_joint_angles(df, angles_path)
    
    # Plot left-right comparison
    comparison_path = os.path.join(output_folder, f'left_right_comparison_{timestamp}.png')
    compare_left_right(df, comparison_path)
    
    print("\n" + "=" * 70)
    print("ANALYSIS COMPLETE!")
    print("=" * 70)

if __name__ == "__main__":
    main()
