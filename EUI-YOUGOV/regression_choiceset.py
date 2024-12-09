# -*- coding: utf-8 -*-
"""
Created on Tue Mar 14 10:44:27 2023

@author: ALuypaert
"""

# -*- coding: utf-8 -*-
"""
Created on Wed Mar  8 14:51:25 2023

@author: ALuypaert
"""


import os
import pandas as pd
from functions import log_regression
import variables as var

""" does not give stats output
from sklearn.linear_model import LogisticRegression
model = LogisticRegression(max_iter=1000, penalty='none')
output = model.fit(x_train,y_train)
print(list(zip(fields, output.coef_.tolist()[0])), output.intercept_)
"""

regression_goal = "SF_fin_choiceset"

""" import data that has been preprocessed """
log_df = pd.read_csv(var.reg_data, sep=",")
log_df = log_df[(log_df.chose3 == 1) & (~pd.isnull(log_df["l-r_indv"])) & (~pd.isnull(log_df["GBS"]))]

log_df = log_df[log_df.country == 210]

fields_to_drop = ["chose3", "chose2"]

socio_dem = ['age_grp_all_25-34','age_grp_all_35-44', 'age_grp_all_45-54', # 18-24 = referent group
				   'age_grp_all_55+','gender_all_female', "l-r_indv"]

party_var = ["l-r_party"]

others = ["GBS"] #separate because cannot be predicted using log
fixed_IV = socio_dem + party_var + others

SF_frames = ["CS_3", "ESu_4", "EBS_6", "ESp_7",
		  "CS_fin_3", "ESu_fin_4", "EBS_fin_6", "ESp_fin_7"]

total_frames = SF_frames

total_output = ""
coef_table = pd.DataFrame()

for country in log_df.country.unique():

	for frame in total_frames:

		if country == 1:
			flex_IV = [column for column in log_df.columns if column not in frame
			  and column in total_frames and "GBS" not in column]
		else:
			flex_IV = [column for column in log_df.columns if frame not in column
			  and column in total_frames]  #UK does not have data for this question

		# combine all the choicesets in which the frame is not present
		choicesets_IV_combo = [column for column in log_df.columns if "(" in column
						 and frame not in column]
	#	log_df["combined_choice"] = log_df[choicesets_IV_combo].agg('sum', axis=1)

		# get a list of the choicesets in which the frame is present
		choicesets_IV = [column for column in log_df.columns if "(" in column
				   and frame in column
				   and column.count("_") == 2]

		IV_fields = fixed_IV + flex_IV + choicesets_IV #+ ["combined_choice"]

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
