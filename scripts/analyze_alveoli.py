import cv2
import numpy as np
import os
from glob import glob
import pandas as pd
from scipy.stats import ttest_ind
import statistics as stats
import matplotlib.pyplot as plt
import seaborn as sns
import argparse

def create_tissue_mask(image):
    """Create a mask to isolate tissue in the image."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)
    kernel = np.ones((5, 5), np.uint8)
    opening = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel, iterations=2)
    closing = cv2.morphologyEx(opening, cv2.MORPH_CLOSE, kernel, iterations=2)
    return closing

def subsample_image(image, start_x, start_y, size):
    """Subsample a specific area of the image."""
    return image[start_y:start_y + size, start_x:start_x + size]

def count_alveoli_in_area(image, start_x, start_y, size):
    """Count the alveoli in a subsampled area of the image."""
    subsampled_image = subsample_image(image, start_x, start_y, size)
    tissue_mask = create_tissue_mask(subsampled_image)
    masked_image = cv2.bitwise_and(subsampled_image, subsampled_image, mask=tissue_mask)
    
    hsv_image = cv2.cvtColor(masked_image, cv2.COLOR_BGR2HSV)
    lower_purple = np.array([125, 50, 50])
    upper_purple = np.array([160, 255, 255])
    purple_mask = cv2.inRange(hsv_image, lower_purple, upper_purple)
    
    kernel = np.ones((3, 3), np.uint8)
    purple_mask = cv2.morphologyEx(purple_mask, cv2.MORPH_CLOSE, kernel, iterations=2)
    purple_mask = cv2.morphologyEx(purple_mask, cv2.MORPH_OPEN, kernel, iterations=2)
    
    contours, _ = cv2.findContours(purple_mask, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
    min_size = 50
    alveoli_contours = [cnt for cnt in contours if cv2.contourArea(cnt) > min_size]
    
    return len(alveoli_contours)

def count_alveoli(image_path, subsample_positions, size):
    """Count the total number of alveoli in the specified subsample positions."""
    image = cv2.imread(image_path)
    total_alveoli_count = 0
    
    for pos in subsample_positions:
        start_x, start_y = pos
        total_alveoli_count += count_alveoli_in_area(image, start_x, start_y, size)
    
    return total_alveoli_count

def analyze_alveoli_counts(image_paths, subsample_positions, size):
    """Analyze alveoli counts for a group of images."""
    counts = []
    samples = []
    for image_path in image_paths:
        count = count_alveoli(image_path, subsample_positions, size)
        if count > 0:
            sample_name = os.path.basename(image_path)
            counts.append(count)
            samples.append(sample_name)
    mean_count = np.mean(counts)
    std_error = stats.stdev(counts) / np.sqrt(len(counts))
    return samples, counts, mean_count, std_error

def plot_results(df, group1, group2, colors):
    """Create and save a publication-quality plot with boxplots and individual points."""
    plt.figure(figsize=(10, 6))
    sns.set(style="whitegrid")
    ax = sns.boxplot(x='Condition', y='Alveoli Count', data=df, order=[group1, group2], palette=colors)
    sns.swarmplot(x='Condition', y='Alveoli Count', data=df, order=[group1, group2], color=".25")
    
    ax.set_title('Alveoli Counts by Condition', fontsize=16)
    ax.set_xlabel('Condition', fontsize=14)
    ax.set_ylabel('Alveoli Count', fontsize=14)
    ax.tick_params(labelsize=12)
    
    plt.savefig('alveoli_counts_publication_quality.png', dpi=300, bbox_inches='tight')
    plt.show()

def main():
    parser = argparse.ArgumentParser(description="Analyze alveoli counts in whole mount images.")
    parser.add_argument("--image_dir", type=str, required=True, help="Directory containing the images.")
    parser.add_argument("--group1", type=str, required=True, help="Name of the first comparison group.")
    parser.add_argument("--group2", type=str, required=True, help="Name of the second comparison group.")
    parser.add_argument("--subsample_size", type=int, default=500, help="Size of the subsample (default: 500).")
    parser.add_argument("--subsample_positions", nargs='+', type=int, default=[100, 100, 300, 100, 500, 100], 
                        help="Subsample positions as a list of (x, y) pairs (default: [100, 100, 300, 100, 500, 100]).")
    parser.add_argument("--colors", nargs=2, type=str, default=["#0000FF", "#90EE90"], 
                        help="Colors for the groups in the plot (default: ['#0000FF', '#90EE90']).")
    
    args = parser.parse_args()
    
    subsample_positions = [(args.subsample_positions[i], args.subsample_positions[i + 1]) 
                           for i in range(0, len(args.subsample_positions), 2)]
    
    group1_images = glob(os.path.join(args.image_dir, f'*_{args.group1}_*.tif'))
    group2_images = glob(os.path.join(args.image_dir, f'*_{args.group2}_*.tif'))

    group1_samples, group1_counts, group1_mean, group1_std_error = analyze_alveoli_counts(group1_images, subsample_positions, args.subsample_size)
    group2_samples, group2_counts, group2_mean, group2_std_error = analyze_alveoli_counts(group2_images, subsample_positions, args.subsample_size)

    t_stat, p_value = ttest_ind(group1_counts, group2_counts)

    data = {
        'Sample': group1_samples + group2_samples,
        'Condition': [args.group1] * len(group1_counts) + [args.group2] * len(group2_counts),
        'Alveoli Count': group1_counts + group2_counts
    }
    df = pd.DataFrame(data)
    df.to_csv('alveoli_counts_by_condition.csv', index=False)

    summary_stats = {
        'Condition': [args.group1, args.group2],
        'Mean Count': [group1_mean, group2_mean],
        'Standard Error': [group1_std_error, group2_std_error],
        'p-value': [p_value, p_value]
    }
    summary_df = pd.DataFrame(summary_stats)
    summary_df.to_csv('summary_statistics_alveoli.csv', index=False)

    plot_results(df, args.group1, args.group2, args.colors)

    print(f"{args.group1} - Mean Alveoli Count:", group1_mean, "Standard Error:", group1_std_error)
    print(f"{args.group2} - Mean Alveoli Count:", group2_mean, "Standard Error:", group2_std_error)
    print("T-test p-value:", p_value)
    print("\nAlveoli counts grouped by condition:\n", df)
    print("\nSummary statistics:\n", summary_df)

if __name__ == "__main__":
    main()
