import pandas as pd
import numpy as np
import os

from itertools import product

import matplotlib.pyplot as plt
import plotly
import plotly.graph_objects as go
import matplotlib.ticker as mticker
from matplotlib.ticker import PercentFormatter, MultipleLocator
from adjustText import adjust_text

from statsmodels.graphics.mosaicplot import mosaic as sm_mosaic
from scipy.stats import norm

import prince

import sys
sys.path.append(r'C:\Users\aluypaert\OneDrive - Universiteit Antwerpen\PHDscripts\common_modules')
from helper_functions import split_text_by_tokens, scale_marker_sizes, cal_stats


def format_plot(ax, 
                title, 
                ylabel='Proportion', 
                ylim=1, 
                yaxisPERC = True,
                yaxis_loc=0.1, 
                invisible_spines=['right', 'top', 'left', 'bottom'], 
                legend_loc='upper left',
               legend_size=14):
   
    ax.set_ylabel(ylabel)
    ax.set_ylim(0,ylim)
    if yaxisPERC:
        ax.yaxis.set_major_formatter(PercentFormatter(1))
    ax.yaxis.set_major_locator(MultipleLocator(yaxis_loc))  # Set ticks at every x

    ax.legend(loc=legend_loc, frameon=False, fontsize=legend_size)
    ax.set_title(title, loc='left', fontsize=14)
    ax.grid(axis='y',linestyle=':', linewidth=0.3)
    ax.spines[invisible_spines].set_visible(False)


# Function to calculate bar positions
def calculate_bar_positions(index, group_width, num_parties):
    bar_width = (group_width * (num_parties - 1)) / num_parties
    group_starts = index - group_width / 2.0
    return bar_width, group_starts

# Function to format x-axis labels
def format_x_labels(ax, labels, max_tokens_per_line, fontsize=8):
    if max_tokens_per_line != None:
        formatted_labels = [split_text_by_tokens(label, max_tokens=max_tokens_per_line) for label in labels]
        ax.set_xticklabels(formatted_labels, fontsize=fontsize, rotation=0)
    else:
        ax.set_xticklabels(labels, fontsize=fontsize, rotation=0)

def set_up_x_labels(ax, labels, max_tokens_per_line, x_pos, fontsize=8):
    ax.set_xticks(x_pos)
    ax.set_xlim(x_pos[0]-0.5, x_pos[-1]+0.5)
    format_x_labels(ax, labels, max_tokens_per_line, fontsize)
    
    
def plot_groups_by_party(data1, data2, party1, party2, party_colors, title, savepath, labels, y_lim=0.5, labelsize=10):
    df1 = list(data1['%'])
    df2 = list(data2['%'])
    df1_CI = list(data1['CI_range'])
    df2_CI = list(data2['CI_range'])
    
    x_pos = np.arange(len(labels))  # the x locations for the labels
    bar_width = 0.35  # the width of the bars
    
    fig, ax = plt.subplots(figsize=(20,10),dpi=450)
    rects1 = ax.bar(x_pos - bar_width/2, df1, bar_width, yerr=df1_CI,
                    label=party1,capsize=2, color=party_colors[party1], alpha=0.7)
    rects2 = ax.bar(x_pos + bar_width/2, df2, bar_width, yerr=df2_CI,
                    label=party2, capsize=2, color=party_colors[party2], alpha=0.7)

    format_plot(ax = ax, 
                title = title, 
                ylabel='Proportion', 
                ylim=y_lim, 
                yaxisPERC = True,
                yaxis_loc=0.1, 
                invisible_spines=['right', 'top', 'left', 'bottom'], 
                legend_loc='upper left',
               legend_size=14)
                        
    set_up_x_labels(ax=ax, labels=labels, max_tokens_per_line=4, x_pos=x_pos, fontsize=labelsize)
    
    plt.tight_layout() 
    plt.savefig(os.path.join(savepath, f'{title}.png'), format="png")
    plt.show()    
    


def create_mosaic_plot(data, title, field_to_show, sf_colors, save_path, max_tokens_per_line=3):
    """
    Creates a mosaic plot to visualize the proportion of frames by group, with customized colors 
    and formatted x-axis labels.

    This function generates a mosaic plot where the proportion of a specific field (e.g., 
    solidarity frames) is visualized across different categories. Colors are assigned to each 
    frame using a predefined color mapping. X-axis labels are split into multiple lines to 
    improve readability when they exceed a certain token length.

    Parameters:
    -----------
    data : pandas.DataFrame
        The input dataset, which must contain columns corresponding to the `field_to_show` 
        and `sf` (solidarity frames).
    title : str
        The title of the plot, which is also used in the filename for saving the plot.
    max_tokens_per_line : int, optional, default=3
        The maximum number of tokens (words) allowed per line in the x-axis labels. Labels 
        exceeding this limit are split into multiple lines.
    field_to_show : str
        The column in `data` representing the categorical variable to be grouped by.
    sf_colors : dict
        A dictionary mapping each solidarity frame (`sf`) to a specific color.
    save_path : str
        The directory path where the output mosaic plot image will be saved.

    Returns:
    --------
    None
        The function displays the mosaic plot and saves it as a JPEG image in the specified directory.

    Notes:
    ------
    - X-axis labels are split into lines using the `split_text_by_tokens` helper function to ensure
      readability when labels are long.
    - The plot's aesthetics are adjusted for better visibility, including hiding unnecessary spines.

    Example:
    --------
    >>> data = pd.DataFrame({
    ...     'sf': ['Frame1', 'Frame1', 'Frame2', 'Frame3', 'Frame2'],
    ...     'group': ['CatA', 'CatB', 'CatC', 'CatA', 'CatD'],
    ...     'count': [10, 20, 30, 40, 50]
    ... })
    >>> create_mosaic_plot(data, title='Example Mosaic Plot', max_tokens_per_line=2)

    This will generate a mosaic plot, display it, and save it to the specified directory.
    """
    # Create a mosaic plot with colors for different SF values
    fig, ax = plt.subplots(figsize=(13, 6), dpi=400)
    
    sm_mosaic(
        data, 
        index=[field_to_show, 'sf'], 
        title=f'Proportion of frame by group - {title}',
        ax=ax,
        properties=lambda key: {'color': sf_colors[key[1]]},  # Assign colors based on SF
        labelizer=lambda k: ''  # Hide default labels
    )
    
    # Format x-tick labels to have line breaks after a specified number of tokens
    labels = [item.get_text() for item in ax.get_xticklabels()]
    formatted_labels = [split_text_by_tokens(label, max_tokens=max_tokens_per_line) for label in labels]
    ax.set_xticklabels(formatted_labels, fontsize=6, rotation=0)

    # Set font size for x-axis label and hide unnecessary spines
    ax.set_xlabel(ax.get_xlabel(), fontsize=4)
    ax.spines[['top', 'right']].set_visible(False)

    # Adjust subplot layout and save the plot
    plt.tight_layout()
    plt.savefig(os.path.join(save_path, f'{field_to_show}_{title}_mosaic.png'), format="png")
    plt.show()



def create_sankey(data, title, save_path, source_column, target_column, source_order, target_order, source_colors=None, target_colors=None, remove_other=True):
    """
    Creates a Sankey diagram visualizing the relationships between two categorical variables (e.g., solidarity frames and grouped categories).
    The diagram uses custom colors to differentiate source and target nodes, applying colors for targets if provided.

    Parameters:
    -----------
    data : pandas.DataFrame
        Input dataset containing at least two columns: source_column (source nodes) and target_column (target nodes).
    title : str
        The title of the visualization, which is also used in the filename of the saved image.
    save_path : str
        The directory path where the output Sankey diagram image will be saved.
    source_order : list
        A predefined list of unique source nodes to ensure consistent ordering and matching.
    target_order : list
        A predefined list of unique target nodes for consistent ordering and matching.
    source_colors : dict, optional
        A dictionary mapping source node labels to their respective colors. Default is grey ('#d3d3d3') if a source label is not found.
    target_colors : dict, optional
        A dictionary mapping target node labels to their respective colors. Default is grey ('#808080') if a target label is not found.

    Returns:
    --------
    None
        The function generates and displays a Sankey diagram and saves it as a JPEG image in the specified directory.
    """
    # Group data by source and target categories, then count occurrences
    
    sankey_counts = data.groupby([source_column, target_column], observed=False).size().reset_index(name='count')
    
    
    # Ensure custom order for sources and targets
    sankey_counts[source_column] = pd.Categorical(sankey_counts[source_column], categories=source_order, ordered=True)
    sankey_counts[target_column] = pd.Categorical(sankey_counts[target_column], categories=target_order, ordered=True)

    # Sort the grouped data for consistency in the diagram
    sankey_counts = sankey_counts.sort_values(by=[source_column, target_column])
    
    if remove_other:
        sankey_counts = sankey_counts[(sankey_counts[source_column] != 'other') & (sankey_counts[target_column] != 'other')]

    # Extract sources, targets, and values for the diagram
    sources = sankey_counts[source_column].tolist()
    targets = sankey_counts[target_column].tolist()
    values = sankey_counts['count'].tolist()

    # Map unique labels (sources and targets) to numeric indices for the Sankey diagram
    unique_labels = list(source_order) + [label for label in target_order if label not in source_order]
    label_map = {label: i for i, label in enumerate(unique_labels)}

    # Convert source and target labels to their corresponding numeric indices
    source_indices = [label_map[source] for source in sources]
    target_indices = [label_map[target] for target in targets]

    # Assign colors to links
    if source_colors is not None:
        link_colors = [source_colors.get(source, '#d3d3d3') for source in sources]
    elif target_colors is not None:
        link_colors = [target_colors.get(target, '#808080') for target in targets]
    else:
        link_colors = ['#d3d3d3'] * len(sources)  # Default grey

    # Assign colors to nodes
    node_colors = []
    for label in unique_labels:
        if label in source_order and source_colors:  # Source node
            node_colors.append(source_colors.get(label, '#d3d3d3'))
        elif label in target_order and target_colors:  # Target node
            node_colors.append(target_colors.get(label, '#808080'))
        else:  # Default grey
            node_colors.append('#808080')

    # Create the Sankey diagram
    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,
            thickness=10,
            line=dict(color="rgba(0,0,0,0)", width=0),  # No border around nodes
            label=unique_labels,
            color=node_colors  # Node colors based on source/target type
        ),
        link=dict(
            source=source_indices,
            target=target_indices,
            value=values,
            color=link_colors  # Link colors based on source or target nodes
        )
    )])

    # Update layout with title and dimensions
    fig.update_layout(
        title_text=title,
        font_size=8,
        height=600,
        width=500  # Adjust diagram width and height
    )

    # Save the diagram as an image and display it
    fig.write_image(os.path.join(save_path, f'{title}_sankey.png'),format="png", scale=1)
    fig.show()





def create_correspondence_plot(data, title, field1, field2, save_path):
    """
    Creates a Correspondence Analysis (CA) plot to visualize the relationships between two categorical variables.

    Correspondence Analysis reduces the dimensionality of a contingency table and projects 
    both rows and columns into a lower-dimensional space, helping to identify associations 
    between categories of the two variables.

    Parameters:
    -----------
    data : pandas.DataFrame
        Input dataset containing the two categorical fields to analyze.
    title : str
        Title of the plot, also used in the filename for saving the plot.
    field1 : str
        Name of the first categorical column, used for rows in the contingency table.
    field2 : str
        Name of the second categorical column, used for columns in the contingency table.
    save_path : str
        Directory path for saving the output plot.

    Returns:
    --------
    None
        The function generates and displays a scatter plot visualizing the correspondence analysis 
        results, and saves the plot as a JPEG image.

    Process:
    --------
    1. Create a contingency table using the two specified fields.
    2. Perform Correspondence Analysis using the `prince` library.
    3. Extract row and column coordinates for the first two components.
    4. Scale marker sizes for the column categories based on their sum in the contingency table.
    5. Plot the row and column points, adding labels and adjusting text placement for readability.
    6. Annotate the axes with the percentage of variance explained by the first two components.
    7. Customize the plot aesthetics, including grid lines, axis labels, and tick label sizes.

    Notes:
    ------
    - Row points represent categories of `field1` (e.g., solidarity frames) and are shown as crosses.
    - Column points represent categories of `field2` (e.g., groups) and are shown as circles, with 
      marker sizes scaled by the column sums.
    - The `adjust_text` library is used to fine-tune text label placement to avoid overlaps.

    Example:
    --------
    >>> data = pd.DataFrame({
    ...     'sf': ['Frame1', 'Frame1', 'Frame2', 'Frame3', 'Frame2'],
    ...     'group': ['CatA', 'CatB', 'CatC', 'CatA', 'CatD'],
    ...     'count': [10, 20, 30, 40, 50]
    ... })
    >>> create_correspondence_plot(data, title='Example Correspondence Plot', field1='sf', field2='group')

    This will generate a correspondence plot, display it, and save it to the specified directory.
    """
    # Create a contingency table
    contingency_table = pd.crosstab(data[field1], data[field2])
    
    # Perform Correspondence Analysis
    ca = prince.CA(n_components=2)
    ca = ca.fit(contingency_table)
    
    # Extract row and column coordinates
    row_coords = ca.row_coordinates(contingency_table)
    col_coords = ca.column_coordinates(contingency_table)

    # Calculate marker sizes for column coordinates based on column sums
    col_sums = contingency_table.sum(axis=0).reset_index()
    col_sizes = scale_marker_sizes(col_sums, 0)

    # Plot the results
    fig, ax = plt.subplots(figsize=(6, 6), dpi=200)
    plt.scatter(row_coords.iloc[:, 0], row_coords.iloc[:, 1], c='#E69F00', marker="x", s=12, label='solidarity frame')
    plt.scatter(col_coords.iloc[:, 0], col_coords.iloc[:, 1], c='#56B4E9', marker="o", s=col_sizes, label='group')
    
    # Add labels for row and column coordinates
    TEXTS = []
    for i, txt in enumerate(contingency_table.index):
        x = row_coords.iloc[i, 0]
        y = row_coords.iloc[i, 1]
        TEXTS.append(ax.text(x, y, txt, color='#E69F00', fontsize=6, weight='bold'))

    for i, txt in enumerate(contingency_table.columns):
        x = col_coords.iloc[i, 0] + 0.02
        y = col_coords.iloc[i, 1] + 0.01
        TEXTS.append(ax.text(x, y, txt, color='#56B4E9', fontsize=6))

    adjust_text(TEXTS)

    # Customize the plot
    plt.title(f'Correspondence analysis {title}', fontsize=8)
    ax.set_xlabel(f"Component 0: {ca.eigenvalues_summary.iloc[0]['% of variance']} of variance", fontsize=6)
    ax.set_ylabel(f"Component 1: {ca.eigenvalues_summary.iloc[1]['% of variance']} of variance", fontsize=6)
    plt.axhline(y=0, color='grey', linewidth=0.5)
    plt.axvline(x=0, color='grey', linewidth=0.5)
    ax.spines[['top', 'right']].set_visible(False)
    ax.tick_params(axis='x', labelsize=4)
    ax.tick_params(axis='y', labelsize=4)
    plt.grid(True, alpha=0.2)

    # Save and display the plot
    plt.savefig(os.path.join(save_path, f'{title}_correspondence.png'), format="png")
    plt.show()



def create_parallel_plot(data, title, frames, field_to_show, save_path):
    """
    Creates a parallel coordinates plot to visualize the proportional representation of 
    solidarity frames (SF) across different groups.

    This plot represents multiple categories (`frames`) using a normalized scale (proportions), 
    with each category visualized as a separate line across group categories. The y-axis displays 
    proportions (0 to 1), and groups are represented along the x-axis.

    Parameters:
    -----------
    data : pandas.DataFrame
        Input dataset containing columns for `sf` (solidarity frames) and a categorical variable 
        represented by `field_to_show`.
    title : str
        The title of the plot, also used in the filename for saving the plot.
    frames : list
        List of solidarity frames (`sf`) to include in the plot. Only rows with these frames are used.

    field_to_show : str
        The column in `data` representing the categorical variable (e.g., groups).
    save_path : str
        Directory path for saving the output plot.

    Returns:
    --------
    None
        The function generates and displays a parallel coordinates plot and saves it as a JPEG image.

    Process:
    --------
    1. Filter the dataset to include only rows with `sf` values in the `frames` list.
    2. Group the filtered data by `field_to_show` and `sf`, calculate counts, and pivot the table.
    3. Normalize the pivoted table by row sums to obtain proportions for each frame.
    4. Create a parallel coordinates plot where:
       - X-axis represents group categories (`field_to_show`).
       - Y-axis represents proportions of each frame in each group.
    5. Customize the plot with a color map, legend, grid lines, and aesthetic adjustments.

    Notes:
    ------
    - The y-axis is formatted to display percentages (0% to 100%).
    - Frames with no data in a group are assigned a proportion of 0.

    Example:
    --------
    >>> data = pd.DataFrame({
    ...     'sf': ['Frame1', 'Frame1', 'Frame2', 'Frame3', 'Frame2'],
    ...     'group': ['CatA', 'CatB', 'CatC', 'CatA', 'CatD'],
    ...     'count': [10, 20, 30, 40, 50]
    ... })
    >>> create_parallel_plot(data, title='Example Parallel Plot', frames=['Frame1', 'Frame2', 'Frame3'])

    This will generate a parallel coordinates plot, display it, and save it to the specified directory.
    """
    # Filter data to include only the specified frames
    df = data[data.sf.isin(frames)].copy()

    # Group and pivot the data
    counts = df.groupby([field_to_show, 'sf']).size().reset_index(name='count')
    pivot_df = counts.pivot(index=field_to_show, columns='sf', values='count').fillna(0)

    # Normalize the pivoted data to get proportions
    pivot_df_percentage = pivot_df.div(pivot_df.sum(axis=1), axis=0).reset_index()
    pivot_df_percentage = pivot_df_percentage[[field_to_show] + frames]

    # Create the parallel coordinates plot
    plt.figure(figsize=(10, 5))
    ax = pd.plotting.parallel_coordinates(pivot_df_percentage, field_to_show, colormap='tab10', axvlines=False)
    
    # Add title and customize plot
    plt.title(f'SF proportions by group for {title}')
    plt.xticks(rotation=0)
    plt.grid(axis="y", alpha=0.25)
    plt.grid(axis="x", alpha=0.25)
    ax.set_ylim(0, 1)
    ax.yaxis.set_major_formatter(mticker.PercentFormatter(1))  # Format y-axis as percentages
    plt.legend(fontsize=7, frameon=False)
    ax.spines[['top', 'left', 'bottom', 'right']].set_visible(False)  # Hide spines

    # Save the plot and display it
    plt.savefig(os.path.join(save_path, f'{title}_parallel.png'), format="png")
    plt.show()



def plot_frames_by_party(data_filtered, title, frames, bar_colors, save_path):
    """
    Plots the proportion of negative solidarity frames by party with confidence intervals.

    This function calculates and visualizes the proportions of negative solidarity frames for 
    different political parties, including 95% confidence intervals for these proportions. 
    The bars in the plot represent proportions for each frame, grouped by party.

    Parameters:
    -----------
    data_filtered : pandas.DataFrame
        The input dataset, filtered to include only relevant data. It must contain the following columns:
        - `party_name`: The political party name.
        - `sf`: The solidarity frame associated with each observation.
    title : str
        A string representing the year or additional context to include in the plot title.

    Global Variables:
    -----------------
    global_negative_sources : list
        A predefined list of negative solidarity frame categories to order the x-axis.
    group_path : str
        Directory path for saving the output plot.

    Returns:
    --------
    None
        The function generates and displays a grouped bar chart with error bars and saves the 
        plot as a JPEG image.

    Process:
    --------
    1. Calculate the counts for each combination of `party_name` and `sf` using a complete set 
       of combinations to handle missing categories.
    2. Compute the total number of frames per party and calculate the proportion of frames that 
       belong to each `sf` category.
    3. Calculate 95% confidence intervals for the proportions using the binomial standard error.
    4. Separate the data into subsets for specific parties (e.g., Democratic and Republican).
    5. Create a grouped bar chart, with error bars indicating the confidence intervals.
    6. Customize the plot aesthetics, including grid lines, labels, and axis formatting.

    Notes:
    ------
    - Confidence intervals are calculated using the formula:
        `CI = proportion ± Z * sqrt(proportion * (1 - proportion) / total_count)`
      where `Z` corresponds to the critical value for a 95% confidence level.
    - Bars are color-coded by party (e.g., blue for Democratic Party, crimson for Republican Party).

    Example:
    --------
    >>> data = pd.DataFrame({
    ...     'party_name': ['Democratic Party', 'Democratic Party', 'Republican Party', 'Republican Party'],
    ...     'sf': ['Frame1', 'Frame2', 'Frame1', 'Frame2'],
    ...     'count': [30, 20, 25, 35]
    ... })
    >>> plot_frames_by_party(data, title_year='2024')

    This will generate a grouped bar chart displaying the proportions of negative frames 
    with confidence intervals for each party and save the plot as an image.
    """
    # Get unique parties and frames
    unique_parties = data_filtered['party_name'].unique()
    unique_frames = data_filtered['sf'].unique()

    # Generate all combinations of party_name and sf
    all_combinations = pd.DataFrame(
        list(product(unique_parties, unique_frames)), columns=['party_name', 'sf']
    )
   
    # Step 1: Group by party_name and sf, and calculate the counts
    grouped_party_sf = (
        data_filtered.groupby(['party_name', 'sf']).size().reset_index(name='count')
    )

    # Reindex to ensure all combinations of party_name and sf are present
    grouped_party_sf = all_combinations.merge(
        grouped_party_sf, on=['party_name', 'sf'], how='left'
    ).fillna({'count': 0})

    # Step 2: Calculate the total number of frames per party
    total_counts = data_filtered.groupby('party_name').size().reset_index(name='total_count')

    # Merge total_counts into the grouped DataFrame
    grouped_party_sf = grouped_party_sf.merge(total_counts, on='party_name')

    # Calculate proportions
    grouped_party_sf['proportion'] = grouped_party_sf['count'] / grouped_party_sf['total_count']

    # Step 3: Calculate the confidence intervals
    confidence_level = 0.95
    z = norm.ppf(1 - (1 - confidence_level) / 2)
    grouped_party_sf['se'] = np.sqrt(grouped_party_sf['proportion'] * (1 - grouped_party_sf['proportion']) / grouped_party_sf['total_count'])
    grouped_party_sf['ci_lower'] = grouped_party_sf['proportion'] - z * grouped_party_sf['se']
    grouped_party_sf['ci_upper'] = grouped_party_sf['proportion'] + z * grouped_party_sf['se']

    # Separate the data by party
    grouped_party_sf['sf'] = pd.Categorical(grouped_party_sf['sf'], 
                                            categories=frames, 
                                            ordered=True)
                                            
    # Define positions for the bars
    x_pos = np.arange(len(frames))  # the label locations
    width = 0.35  # the width of the bars

    # Create the plot
    fig, ax = plt.subplots(figsize=(10, 6))
    
    
    for i, party in enumerate(sorted(grouped_party_sf['party_name'].unique())):
        party_data = grouped_party_sf[grouped_party_sf['party_name'] == party].sort_values(by=['sf'])
        
        # Plot data bars with error bars
        ax.bar(x_pos + (i - len(grouped_party_sf.party_name.unique()) / 2) * width, party_data['proportion'], width, label=party,
               yerr=[party_data['proportion'] - party_data['ci_lower'], 
                     party_data['ci_upper'] - party_data['proportion']], capsize=5, color=bar_colors[party], alpha=0.7)
                 
    # Add some text for labels, title and custom x-axis tick labels, etc.
    format_plot(ax=ax, 
                title= title, 
                ylabel='Proportion', 
                ylim=1, 
                yaxisPERC = True,
                yaxis_loc=0.1, 
                invisible_spines=['right', 'top', 'left', 'bottom'], 
                legend_loc='upper left',
               legend_size=14)
               
    set_up_x_labels(ax=ax, labels=frames, max_tokens_per_line=None, x_pos=x_pos, fontsize=10)
    
    
    # Display the plot
    plt.tight_layout()
    plt.savefig(os.path.join(save_path, f'{title}.png'), format="png")
    plt.show()
