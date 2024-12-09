import statsmodels.api as sm
import numpy as np
import pandas as pd

def split_text_by_tokens(text, max_tokens=20):
    """
    Splits a given text into multiple lines, ensuring each line does not exceed the specified maximum number of tokens.

    This function splits the input `text` into smaller chunks, where each chunk is a line of text containing 
    a maximum of `max_tokens` tokens. Tokens are defined as words separated by whitespace.

    Parameters:
    -----------
    text : str
        The input text to be split into lines.
    max_tokens : int, optional, default=20
        The maximum number of tokens (words) allowed per line.

    Returns:
    --------
    str
        The input text split into multiple lines, with each line containing up to `max_tokens` tokens, 
        joined together with newline characters (`\n`).

    Notes:
    ------
    - Words in the text are not truncated; the function ensures that lines contain complete words.
    - If the input `text` has fewer tokens than `max_tokens`, it will be returned as a single line.

    Example:
    --------
    >>> text = "This is an example sentence to demonstrate how the function works by splitting text into lines."
    >>> split_text_by_tokens(text, max_tokens=10)
    'This is an example sentence to demonstrate\nhow the function works by splitting\ntext into lines.'
    """
	
    words = text.split()
    lines = []
    current_line = []
    
    for word in words:
        current_line.append(word)
        # Check if the current line exceeds the maximum token count
        if len(' '.join(current_line)) >= max_tokens:
            lines.append(' '.join(current_line))
            current_line = []
    
    # Add any remaining words to the final line
    if current_line:
        lines.append(' '.join(current_line))
        
    return '\n'.join(lines)



def scale_marker_sizes(df, scale_column_value, min_size=6, max_size=80, scale_method='sqrt'):
    """
    Scales marker sizes based on the values in a given column of a DataFrame, with optional scaling methods.
    
    Parameters:
    df (pd.DataFrame): The DataFrame containing the data.
    scale_column_value (str): The name of the column to use for scaling marker sizes.
    min_size (int): The minimum size for the markers.
    max_size (int): The maximum size for the markers.
    scale_method (str): The scaling method to use ('linear', 'sqrt', 'log').
    
    Returns:
    pd.Series: A series with scaled marker sizes.
    """
    values = df[scale_column_value]
    if scale_method == 'sqrt':
        values = np.sqrt(values)
    elif scale_method == 'log':
        values = np.log1p(values)  # log(1 + x) to handle zero values safely
    
    sizes = min_size + (values - values.min()) * (max_size - min_size) / (values.max() - values.min())
    return sizes


# Function to calculate the confidence interval for proportions
def calculate_proportion_confint(count, nobs):
    return sm.stats.proportion_confint(count=count, nobs=nobs, method='normal', alpha=0.05)


def cal_stats(data, count_field, groupby_field):
    """
    Calculates statistics for grouped data, including counts, proportions, and confidence intervals.

    This function groups the input data by the specified field, sums up the values in the provided count field
    for each category, calculates proportions, and computes 95% confidence intervals for these proportions.
    The results are returned in a DataFrame for further analysis.

    Parameters:
    -----------
    data : pandas.DataFrame
        The input dataset, which must contain the following columns:
        - `count_field`: Numeric column representing counts to be aggregated.
        - `groupby_field`: The column to group the data by.
    count_field : str
        The column name in `data` representing the counts to be summed for each category.
    groupby_field : str
        The column name to group the data by. Categories within this field will have their statistics calculated.

    Returns:
    --------
    pandas.DataFrame
        A DataFrame containing the following columns for each category in `groupby_field`:
        - `groupby_field`: The category name.
        - `count`: The total value from the count field for the category.
        - `%`: The proportion of the category relative to the total of the count field.
        - `ci_lower`: The lower bound of the 95% confidence interval for the proportion.
        - `ci_upper`: The upper bound of the 95% confidence interval for the proportion.
        - `CI_range`: The range of the confidence interval (`% - ci_lower`).

    Process:
    --------
    1. Group the data by `groupby_field` and calculate the sum of the `count_field` for each category.
    2. Calculate the total sum of the `count_field` to compute proportions.
    3. Compute 95% confidence intervals for the proportions of each category using a helper function
       `calculate_proportion_confint` (assumed to be pre-defined).
    4. Merge the confidence intervals back into the main DataFrame for a consolidated view.
    5. Sort the results by the count of each category in descending order.

    Notes:
    ------
    - The confidence intervals are calculated using the formula:
        `CI = p ± Z * sqrt(p * (1 - p) / N)`
      where `p` is the proportion, `Z` is the Z-score for the confidence level (e.g., 1.96 for 95%),
      and `N` is the total count.
    - The function assumes that a helper function `calculate_proportion_confint` is defined elsewhere to
      compute the confidence intervals.

    Example:
    --------
    >>> data = pd.DataFrame({
    ...     'top25_cat': ['Category1', 'Category2', 'Category1', 'Category3', 'Category2'],
    ...     'tally': [10, 15, 25, 30, 20]
    ... })
    >>> cal_stats(data, count_field="tally", groupby_field="top25_cat")
       top25_cat  count       %  ci_lower  ci_upper  CI_range
    0  Category1     35  0.2917   0.1946   0.4043    0.0971
    1  Category3     30  0.2500   0.1605   0.3575    0.0895
    2  Category2     35  0.2917   0.1946   0.4043    0.0971
    """
    # Group by category and sum the count field
    category_counts = data.groupby(groupby_field, observed=False)[count_field].sum().sort_values(ascending=False)

    # Total count of all tallies
    total_count = category_counts.sum()

    # Create a basic DataFrame with counts and proportions
    basic_df = data.groupby(by=[groupby_field], as_index=False, observed=False)[count_field].sum()
    basic_df['%'] = basic_df[count_field] / total_count

    # Apply the confidence interval calculation to each category
    confidence_intervals = category_counts.apply(lambda count: calculate_proportion_confint(count, total_count))

    # Convert to DataFrame for better readability
    confidence_intervals_df = pd.DataFrame(confidence_intervals.tolist(), index=category_counts.index,
                                           columns=['ci_lower', 'ci_upper'])

    # Merge confidence intervals into the basic DataFrame
    basic_df = basic_df.merge(confidence_intervals_df, how="left", left_on=groupby_field, right_index=True)
    basic_df['CI_range'] = basic_df['%'] - basic_df['ci_lower']

    # Sort the DataFrame by count in descending order
    basic_df.sort_values(by=count_field, ascending=False, inplace=True)

    return basic_df.reset_index(drop=True)
