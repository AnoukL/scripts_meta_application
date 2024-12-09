def add_top_field(data, top_value, category_column, rankingtype='pos'):
    """
    Adds a new field to a dataset, grouping categories based on their ranking in terms of frequency.
    
    This function identifies the top `top_value` categories from the `word_category_grouped` column
    based on their frequency in the dataset. It then creates a mapping that assigns these top categories
    to themselves and all other categories to a group labeled "other". Additionally, it provides the 
    top categories as a dictionary for external use.
    
    Parameters:
    -----------
    data : pandas.DataFrame
        Input dataframe that contains the column `word_category_grouped` and `sentence`.
    top_value : int
        The number of top categories to identify based on their frequency.
    rankingtype : str, optional, default='pos'
        A label to describe the ranking type so that multiple rankings for the same top can be made (e.g., 'pos').
        This value is appended to the key in the output dictionary.

    Returns:
    --------
    top_ranking : dict
        A dictionary with a single key following the format `top{top_value}_cat_{rankingtype}`,
        mapping to a list of the top `top_value` categories.
    new_column : pandas.Series
        A new column for the dataframe where top categories retain their original names and 
        all other categories are grouped as "other".
    
    Example:
    --------
    >>> data = pd.DataFrame({
    ...     'word_category_grouped': ['A', 'A', 'B', 'B', 'B', 'C', 'C', 'D'],
    ...     'sentence': ['s1', 's2', 's3', 's4', 's5', 's6', 's7', 's8']
    ... })
    >>> top_ranking, new_column = add_top_field(data, top_value=2)
    >>> top_ranking
    {'top2_cat_pos': ['B', 'A']}
    >>> new_column
    0        A
    1        A
    2        B
    3        B
    4        B
    5    other
    6    other
    7    other
    Name: word_category_grouped, dtype: object
    """
    data_temp = data.copy()
        
    # Calculate the total frequency of each category
    total_ranking_frames = data_temp.groupby(by=[category_column], as_index=False, observed=False).agg({"sentence": "count"}).sort_values("sentence", ascending=False)
    total_ranking_frames.rename(columns={"sentence": "count"}, inplace=True)
    total_ranking_frames['%'] = 100 * total_ranking_frames['count'] / total_ranking_frames['count'].sum()

    # Get the top categories and all unique categories
    top_values = list(total_ranking_frames.head(top_value)[category_column])
    total = list(total_ranking_frames[category_column])

    # Create a dictionary mapping the top categories
    top_ranking = {f"top{top_value}_cat_{rankingtype}": top_values}

    top_dict = {}
    for cat in total:
        if cat in top_values:
            top_dict[cat] = cat
        else:
            top_dict[cat] = "other"
    
    # Map the new field to the original data
    return top_ranking, data_temp[category_column].map(top_dict).fillna("other")
