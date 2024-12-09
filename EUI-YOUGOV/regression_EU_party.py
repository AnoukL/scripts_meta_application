# -*- coding: utf-8 -*-
"""
Created on Wed Mar 15 17:08:44 2023

@author: ALuypaert
"""



import os
import pandas as pd
from functions import log_regression
import variables as var

regression_goal = "EU_party"


""" import data that has been preprocessed """
log_df = pd.read_csv(var.reg_data, sep=",")
log_df = log_df[~pd.isnull(log_df["GBS"])]

fields_to_drop = ["chose3", "chose2"]

socio_dem = ["l-r_indv_2.0", "l-r_indv_3.0", "l-r_indv_4.0"
			 , "l-r_indv_5.0", "l-r_indv_6.0", "l-r_indv_7.0", "gender_all_female"]

others = ["GBS"] #separate because cannot be predicted using log
fixed_IV = socio_dem + others

SF_frames = ["CS_3", "ESu_4", "EBS_6", "ESp_7"]

partylr = pd.read_csv(os.path.join(var.output_path, "partylr.csv"), sep=",")

EU_frames = ['EU_type_global', 'EU_type_market', 'EU_type_protective', 'EU_type_social'] #None = referent group
total_frames = EU_frames + SF_frames

total_output = ""
coef_table = pd.DataFrame()
middle = 4

for country in log_df.country.unique():

	country_parties = partylr[partylr["country"] == country]

	#make sure other is not selected as referent category
	country_parties_middle_sorted = country_parties.iloc[(country_parties['l-r_party'] - middle).abs().argsort(),:]
	country_parties_filtered = country_parties_middle_sorted[country_parties_middle_sorted.voted_party.str.contains("Other") == False].copy()

	ref_party = f"voted_party_{country_parties_filtered.iloc[0]['voted_party']}"

	country_parties_lr_sorted = country_parties.iloc[country_parties['l-r_party'].argsort(),:]

	country_party_list = country_parties_lr_sorted.voted_party.to_list()
	party_var = [f"voted_party_{party}" for party in country_party_list if f"voted_party_{party}" != ref_party]

	for frame in EU_frames:

		if country == 1:
				continue
		else:
			flex_IV = [column for column in log_df.columns if frame not in column
			  and column in total_frames]

		#combine_IV = [column for column in log_df.columns if "(" in column and frame not in column]

		IV_fields = fixed_IV + flex_IV + party_var

		print(f"Performing log regression for country {var.map_country_to_label[country]} \
				on {frame} using fields {IV_fields} ")
		output, coef_df = log_regression(log_df[log_df.country == country], IV_fields, frame)

		coef_df["country"] = var.map_country_to_label[country]
		coef_table = pd.concat([coef_table, coef_df.reset_index()], ignore_index=True)
		total_output = total_output + f"Results for {country}, {var.map_country_to_label[country]} \
		for solidarity frame {frame} with {ref_party.replace('voted_party_','')} as referent party \n" + output + "\n"

#open text file
with open(os.path.join(var.output_path, f"{regression_goal}_model_output.txt"), "w", encoding="utf-8") as f:
	f.write(total_output)

coef_table.to_excel(os.path.join(var.output_path, f"{regression_goal}_model_coef.xlsx"), index=False)