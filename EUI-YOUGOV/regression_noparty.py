# -*- coding: utf-8 -*-
"""
Created on Tue Mar 14 16:55:36 2023

@author: ALuypaert
"""


import os
import pandas as pd
from functions import log_regression
import variables as var

regression_goal = "SF_fin_noparty"

""" import data that has been preprocessed """
log_df = pd.read_csv(var.reg_data, sep=",")
log_df = log_df[(log_df.chose3 == 1) & (~pd.isnull(log_df["l-r_indv"])) & (~pd.isnull(log_df["GBS"]))]

log_df = log_df[log_df.country == 210]

fields_to_drop = ["chose3", "chose2"]

socio_dem = ['age_grp_all_25-34','age_grp_all_35-44', 'age_grp_all_45-54', # 18-24 = referent group
				   'age_grp_all_55+','gender_all_female', "l-r_indv"]

others = ["GBS"] #separate because cannot be predicted using log
fixed_IV = socio_dem + others

SF_frames = ["CS_3", "ESu_4", "EBS_6", "ESp_7",
		  "CS_fin_3", "ESu_fin_4", "EBS_fin_6", "ESp_fin_7"]

total_frames = SF_frames

total_output = ""
coef_table = pd.DataFrame()

for country in log_df.country.unique():

	for frame in total_frames:

		if country == 1:
			if "EU_type" in frame: #UK does not have data for this question
				continue
			flex_IV = [column for column in log_df.columns if column not in frame
			  and column in total_frames and "EU_type" not in column
			  and "GBS" not in column]
		else:
			flex_IV = [column for column in log_df.columns if frame not in column
			  and column in total_frames]  #UK does not have data for this question

		#combine_IV = [column for column in log_df.columns if "(" in column and frame not in column]

		IV_fields = fixed_IV + flex_IV

		print(f"Performing log regression for country {var.map_country_to_label[country]} \
				on {frame} using fields {IV_fields} ")
		output, coef_df = log_regression(log_df[log_df.country == country], IV_fields, frame)

		coef_df["country"] = var.map_country_to_label[country]
		coef_table = pd.concat([coef_table, coef_df.reset_index()], ignore_index=True)
		total_output = total_output + f"Results for {country}, {var.map_country_to_label[country]} \
		for solidarity frame {frame} \n" + output + "\n"

#open text file
with open(os.path.join(var.output_path, f"{regression_goal}_model_output.txt"), "w") as f:
	f.write(total_output)

coef_table.to_excel(os.path.join(var.output_path, f"{regression_goal}_model_coef.xlsx"), index=False)
