# -*- coding: utf-8 -*-
"""
Created on Wed Mar  8 14:57:45 2023

@author: ALuypaert
"""

import os
import pandas as pd

path = ***** #removed for anonimity reasons
datafile = os.path.join(path, "2022_EUI_YouGov", "2022_EUI_YouGov_dataset.csv")
codebook = os.path.join(path, "2022_EUI_YouGov", "2022_EUI_YouGov_codebook.xlsx")
output_path =  os.path.join(path, "output")
reg_data = os.path.join(output_path, "cleaned_data.csv")
country_var_path =  os.path.join(path, "Countrydata")
party_var_path =  os.path.join(path, "party data")
country_data = os.path.join(country_var_path, "Country_variables.xlsx")


dep_var = ["CS_3", "ESu_4", "EBS_6", "ESp_7"]
idv = ["l-r_indv", "country", 'gender_dummy_male','gender_dummy_female',
	   "age_dummy_18-24", 'age_dummy_25-34', 'age_dummy_35-44', 'age_dummy_45-54', 'age_dummy_55+'
	   , "CS_3", "ESu_4", "EBS_6", "ESp_7"]


map_label = pd.read_excel(codebook, sheet_name= "MAP Label")
map_label.Variables = map_label.Variables.fillna(method="ffill")
map_country_to_label = dict(zip(map_label[map_label.Variables == "country"]['Value'],
								map_label[map_label.Variables == "country"]['Label']))
