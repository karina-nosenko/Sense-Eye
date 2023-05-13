import cv2
import json
import os
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
from collections import defaultdict

defined_strings = {0: 'orange', 1: 'pink'}

def create_personalized_frames():
     # Path to the directory containing the trace files and images
    trace_dir = "../materials/traces"

    # Iterate over all the game directories
    for game_dir in os.listdir(trace_dir):
        game_path = os.path.join(trace_dir, game_dir)

        # Ignore non-directory items in the traces folder
        if not os.path.isdir(game_path):
            continue

        # Read the trace file for this game
        trace_file_path = os.path.join(game_path, "traces.json")
        if not os.path.exists(trace_file_path):
            continue
   
        # Open the JSON file and load its contents into a Python object
        with open(trace_file_path, 'r') as f:
            data = json.load(f)
        df = pd.DataFrame.from_dict(data, orient='columns')
        df = df.dropna(subset=['gameId'])

        # Fiter the df to include only players
        filtered_data = [obj for obj in data if obj.get('class') == 'person' and 'properties' in obj and all(key in obj['properties'] for key in ['holdsBall', 'x', 'y', 'sightDirection', 'center_y', 'id', 'team'])]
        filtered_df = pd.DataFrame(filtered_data)

        # Create a copy of the original DataFrame
        players_df = df.copy()

        if 'properties' in players_df and 'id' in players_df['properties']:
            players_df['properties']['id'] = players_df['properties']['id'].astype(str).apply(lambda x: defined_strings.get(int(x), x))

        # Create the frames with insights
        create_ball_holders_percentages(game_path, df)
        create_correlations(game_path, filtered_df)

def create_ball_holders_percentages(game_path, df):
    default_color = 'gray'  # Default color for IDs not found in defined_strings
    next_numeric_id = 2  # Start assigning numeric IDs from 3 onwards

    # Step 1: Group objects by gameId
    game_groups = defaultdict(list)
    for _, row in df.iterrows():
        game_groups[row['gameId']].append(row)

    # Step 2: Calculate holdsBall percentage for each id in each gameId group
    for game_id, group in game_groups.items():
        id_counts = defaultdict(int)
        total_objects = len(group)

        # Step 3: Count occurrences of holdsBall being true for each id
        for row in group:
            properties = row['properties']
            if 'holdsBall' in properties and properties['holdsBall'] and 'id' in properties:
                id_value = properties['id']
                if not isinstance(id_value, int):
                    if id_value not in defined_strings:
                        defined_strings[id_value] = next_numeric_id
                        next_numeric_id += 1
                    id_value = defined_strings[id_value]
                id_counts[id_value] += 1

        hash_map = {}  # Hash map to store ID-percentage associations
        max_percentage = 0
        max_color = None
        for id_value, count in id_counts.items():
            percentage = int(count / total_objects * 100)
            hash_map[id_value] = percentage
            if percentage > max_percentage:
                max_percentage = percentage
                max_color = defined_strings.get(id_value, default_color)

        # Prepare data for plotting
        ids = list(hash_map.keys())
        percentages = list(hash_map.values())

        # Convert numeric IDs to labels
        labels = [defined_strings.get(id_value, str(id_value)) for id_value in ids]

        # Plotting the chart
        plt.figure(figsize=(8, 6))
        plt.bar(labels, percentages, color=[defined_strings.get(id_value, default_color) for id_value in ids])
        plt.xlabel('Cap Color')
        plt.ylabel('Percentage')
        plt.title(f"Percentages of Ball Holders")

        # Display the percentage on top of each bar
        for i, percentage in enumerate(percentages):
            plt.text(i, percentage + 1, f"{percentage}%", ha='center', va='bottom')
        
        # Set the x-axis ticks to display only whole numbers
        plt.xticks(range(min(ids), max(ids) + 1))

        # Adjust the y-axis limit to accommodate the highest bar
        plt.ylim(top=max_percentage + 10)  # Increase the limit by 10 units 

        # Add text at the bottom of the chart
        text = f"The player with the highest percentage of holding the ball is: {max_color}"
        plt.text(0.5, -0.15, text, transform=plt.gca().transAxes, ha='center')

        # Adjust the layout to ensure the text fits within the figure
        plt.tight_layout()

        plt.savefig(game_path + '/ball_holders.png')

def create_correlations(game_path, filtered_df):
    # Create a DataFrame from the filtered data
    df = pd.DataFrame(filtered_df)

    # Select the relevant numeric fields for correlation analysis
    numeric_fields = ['x', 'y', 'sightDirection', 'id', 'team']
    subset_df = df['properties'].apply(lambda x: pd.Series({field: x[field] for field in numeric_fields}))

    # Calculate the correlation matrix
    corr_matrix = subset_df.corr()

    # Rename the 'id' label to 'color' in the correlation matrix
    corr_matrix = corr_matrix.rename(columns={'id': 'color'})
    corr_matrix = corr_matrix.rename(index={'id': 'color'})

    # Create a mask for the upper triangular portion
    mask = np.triu(np.ones_like(corr_matrix, dtype=bool))

    # Plot the correlation heatmap with triangular mask
    plt.figure(figsize=(10, 8))
    sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', mask=mask)
    plt.title('Correlation Heatmap')

    plt.savefig(game_path + '/correlations.png')