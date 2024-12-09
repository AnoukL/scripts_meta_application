# -*- coding: utf-8 -*-
"""
Created on Fri Mar 10 13:50:41 2023

@author: ALuypaert
"""
import os
import pandas as pd
import variables as var

"""
Calculate correlations between each frame's incentive and the financial q
correlations between frames amongst each other
correlations between financial amongst each other

total, within each country, within each country-party
"""

data = pd.read_excel(os.path.join(var.output_path, "data_excel_analysis.xlsx"))
data = data[(data["filter"] == "none") & (data.level == "individual")]
columns_to_del = [column for column in data.columns if "(" in column or "share" in column]
columns_to_del = columns_to_del + ["l-r_party", "respondent_id", "count",
					   "age_grp_all", "gender_all", "l-r_indv", "chose3", "chose2",
					   "no_fin_choices", "exp1_all_3_5", "exp1_all_2_5", "filter", "level"]
data.drop(columns=columns_to_del, inplace=True)
data.sort_index(axis=1, inplace=True)
#data = pd.get_dummies(data, columns = ["EU_type"])

correlations = data.corr().reset_index()
correlations["level"] = "overall"

for country in data.country.unique():
	filtered_data = data[data.country == country]

	country_corr = filtered_data.corr().reset_index()
	country_corr["level"] = "country"
	country_corr["country"] = country

	print(country_corr)
	correlations = pd.concat([correlations, country_corr], ignore_index=True)

	for party in filtered_data.voted_party.unique():

		filtered_data_party = filtered_data[filtered_data.voted_party == party]

		party_corr = filtered_data_party.corr().reset_index()
		party_corr["level"] = "country-party"
		party_corr["country"] = country
		party_corr["party"] = party

		print(party_corr)
		correlations = pd.concat([correlations, party_corr])


correlations.to_excel(os.path.join(var.output_path, "correlations.xlsx"), index=False)
