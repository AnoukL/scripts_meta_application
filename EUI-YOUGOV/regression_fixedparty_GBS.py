# -*- coding: utf-8 -*-
"""
Created on Tue Mar 21 18:59:46 2023

@author: ALuypaert
"""

# -*- coding: utf-8 -*-
"""
Created on Mon Mar 13 15:56:31 2023

@author: ALuypaert
"""

# -*- coding: utf-8 -*-
"""
Created on Wed Mar  8 14:51:25 2023

@author: ALuypaert
"""


import os
import pandas as pd
from functions import lin_regression
import variables as var

regression_goal = "SF_fin_fixed-party_GBS"

map_party_to_country = pd.read_csv(os.path.join(var.output_path, "party_to_country.csv"))

""" import data that has been preprocessed """
lin_df = pd.read_csv(var.reg_data, sep=",")
lin_df = lin_df[~pd.isnull(lin_df["GBS"])]
fields_to_drop = ["chose3", "chose2"]

#socio_dem = ["l-r_indv_2.0", "l-r_indv_3.0", "l-r_indv_4.0"
#			 , "l-r_indv_5.0", "l-r_indv_6.0", "l-r_indv_7.0", "gender_all_female"]


socio_dem = ["gender_all_female"]

target = ["GBS"] #separate because cannot be predicted using log
fixed_IV = socio_dem

SF_frames = ["CS_3", "ESu_4", "EBS_6", "ESp_7"]

partylr = pd.read_csv(os.path.join(var.output_path, "partylr.csv"), sep=",")

total_frames = SF_frames

total_output = ""
coef_table = pd.DataFrame()
middle = 4

ref_parties = pd.read_excel(os.path.join(var.output_path, "Ref party analysis.xlsx"), sheet_name="Filtered")

for country in lin_df.country.unique():

	country_parties = partylr[partylr["country"] == country]
	country_parties_lr_sorted = country_parties.iloc[country_parties['l-r_party'].argsort(),:]
	country_party_list = country_parties_lr_sorted.voted_party.to_list()


	for frame in target:

		ref_party = ref_parties[(ref_parties.country == var.map_country_to_label[country])
						  & (ref_parties.DV == frame)
						  & (ref_parties.chosen =="yes")]["index"].values[0]
		party_var = [f"voted_party_{party}" for party in country_party_list if f"voted_party_{party}" != ref_party]

		flex_IV = [column for column in lin_df.columns if frame not in column
		  and column in total_frames]

		IV_fields = fixed_IV + flex_IV + party_var

		print(f"Performing lineair regression for country {var.map_country_to_label[country]} \
				on {frame} using fields {IV_fields} ")
		output, coef_df = lin_regression(lin_df[lin_df.country == country], IV_fields, frame)

		coef_df["country"] = var.map_country_to_label[country]
		coef_table = pd.concat([coef_table, coef_df.reset_index()], ignore_index=True)
		coef_df["model"] = regression_goal
		total_output = total_output + f"Results for {country}, {var.map_country_to_label[country]} for solidarity frame {frame} with {ref_party.replace('voted_party_','')} as referent party \n" + output + "\n"

#open text file
with open(os.path.join(var.output_path, f"{regression_goal}_model_output.txt"), "w", encoding="utf-8") as f:
	f.write(total_output)

coef_table.to_excel(os.path.join(var.output_path, f"{regression_goal}_model_coef.xlsx"), index=False)
