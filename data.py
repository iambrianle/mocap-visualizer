import pandas as pd
import math
import matplotlib.pyplot as plt
from mat4py import loadmat
import os

# load the .mat file
path = 'motioncapture_with_time.mat'
mat4py_data = loadmat(path)

# identify all sheet names
sheet_names = [key for key in mat4py_data.keys()]

# define markers
markers = {
    'right_hip': ["'XRxAsis  '", "'YRxAsis  '", "'ZRxAsis  '"],
    'right_knee': ["'XRxLatCon'", "'YRxLatCon'", "'ZRxLatCon'"],
    'right_ankle': ["'XRxLatMal'", "'YRxLatMal'", "'ZRxLatMal'"],
    'left_hip': ["'XLxAsis  '", "'YLxAsis  '", "'ZLxAsis  '"],
    'left_knee': ["'XLxLatCon'", "'YLxLatCon'", "'ZLxLatCon'"],
    'left_ankle': ["'XLxLatMal'", "'YLxLatMal'", "'ZLxLatMal'"],
    'right_foot': ["'XRxToe1  '", "'YRxToe1  '", "'ZRxToe1  '"],
    'left_foot': ["'XLxToe1  '", "'YLxToe1  '", "'ZLxToe1  '"],
    'head': ["'XRxCheec '", "'YRxCheec '", "'ZRxCheec '"],
    'neck': ["'XC7      '", "'YC7      '", "'ZC7      '"],
    'torso': ["'Xmaxkif  '", "'Ymaxkif  '", "'Zmaxkif  '"],
}

# Create an output directory for the plots
output_dir = 'plots'
os.makedirs(output_dir, exist_ok=True)

# Define calculating functions
def calculate_distance(p1, p2):
    x_diff = p2[0] - p1[0]
    y_diff = p2[1] - p1[1]
    z_diff = p2[2] - p1[2]
    return math.sqrt(x_diff ** 2 + y_diff ** 2 + z_diff ** 2)

def calculate_angle(a, b, c, epsilon=1e-8):
    if b < epsilon or c < epsilon:
        return 0.0
    cos_theta = (b**2 + c**2 - a**2) / (2 * b * c)
    cos_theta = max(min(cos_theta, 1.0), -1.0)
    theta_radians = math.acos(cos_theta)
    return math.degrees(theta_radians)

def calculate_angle_between_points(p1, p2, p3):
    a = calculate_distance(p1, p2)
    b = calculate_distance(p2, p3)
    c = calculate_distance(p1, p3)
    return calculate_angle(a, b, c)

def calculate_walking_speed(start, end, final_time):
    distance = calculate_distance(start, end)
    speed = distance / final_time if final_time != 0 else 0
    return speed

def KneeAngleRight(hip, knee, ankle):
    return calculate_angle_between_points(hip, knee, ankle)

def KneeAngleLeft(hip, knee, ankle):
    return calculate_angle_between_points(hip, knee, ankle)

def AnkleAngleRight(knee, ankle, foot):
    return calculate_angle_between_points(knee, ankle, foot)

def AnkleAngleLeft(knee, ankle, foot):
    return calculate_angle_between_points(knee, ankle, foot)

def HeadNeckAngle(head, neck, torso):
    return calculate_angle_between_points(head, neck, torso)

# processing function
for sheet_name in sheet_names:
    print(f"Processing {sheet_name}...")

    sheet_data = mat4py_data[sheet_name]
    marker_names = sheet_data['marker_names']
    marker_data = sheet_data['marker_data']
    time_data = sheet_data['time']

    # create dataframe for the current sheet
    df = pd.DataFrame(marker_data)
    df.columns = [name.strip() for name in marker_names]
    time_series = pd.Series(time_data, name='Time')
    print(df)

    # Extract marker positions
    extracted_data = {key: df[columns].astype(float).to_numpy() for key, columns in markers.items()}
    print(extracted_data)


    # Movement data (assuming 'torso' represents overall movement)
    movement = extracted_data['torso']

    # Calculate walking speed
    start = tuple(float(x) for x in movement[0])
    end = tuple(float(x) for x in movement[-1])
    final_time = float(time_series.iloc[-1])
    walking_speed = calculate_walking_speed(start, end, final_time)
    print(f"Walking speed for {sheet_name}: {walking_speed:.2f} meters per second")

    # Calculate angles over time
    knee_angles_right = [
        KneeAngleRight(rh, rk, ra) for rh, rk, ra in zip(
            extracted_data['right_hip'],
            extracted_data['right_knee'],
            extracted_data['right_ankle']
        )
    ]
    knee_angles_left = [
        KneeAngleLeft(lh, lk, la) for lh, lk, la in zip(
            extracted_data['left_hip'],
            extracted_data['left_knee'],
            extracted_data['left_ankle']
        )
    ]
    ankle_angles_right = [
        AnkleAngleRight(rk, ra, rf) for rk, ra, rf in zip(
            extracted_data['right_knee'],
            extracted_data['right_ankle'],
            extracted_data['right_foot']
        )
    ]
    ankle_angles_left = [
        AnkleAngleLeft(lk, la, lf) for lk, la, lf in zip(
            extracted_data['left_knee'],
            extracted_data['left_ankle'],
            extracted_data['left_foot']
        )
    ]
    head_neck_angles = [
        HeadNeckAngle(h, n, t) for h, n, t in zip(
            extracted_data['head'],
            extracted_data['neck'],
            extracted_data['torso']
        )
    ]

    # Plotting
    plt.figure(figsize=(14, 10))
    plt.plot(time_series, knee_angles_right, label='Right Knee Angle', marker='o', color='orange', markersize=4)
    plt.plot(time_series, knee_angles_left, label='Left Knee Angle', marker='o', color='blue', markersize=4)
    plt.plot(time_series, ankle_angles_right, label='Right Ankle Angle', marker='o', color='green', markersize=4)
    plt.plot(time_series, ankle_angles_left, label='Left Ankle Angle', marker='o', color='red', markersize=4)
    plt.plot(time_series, head_neck_angles, label='Head/Neck Angle', marker='o', color='purple', markersize=4)

    # Add walking speed as a text annotation on the plot
    plt.text(0.95, 0.95, f'Walking Speed: {walking_speed:.2f} m/s',
             horizontalalignment='right',
             verticalalignment='top',
             transform=plt.gca().transAxes,
             fontsize=12,
             bbox=dict(facecolor='white', alpha=0.5))

    plt.title(f'Angle Profiles Over Time for {sheet_name}')
    plt.xlabel('Time (seconds)')
    plt.ylabel('Angle (degrees)')
    plt.legend()
    plt.grid(True)

    # Save the plot
    output_path = os.path.join(output_dir, f"{sheet_name}_output.png")
    plt.savefig(output_path)
    print(f"Plot saved to {output_path}\n")

    # plt.show()
    # plt.close()

print("Processing complete for all sheets.")