# -*- coding: utf-8 -*-
"""
Created on Thu Mar 23 12:05:59 2023

@author: ALuypaert
"""

import pandas as pd
import variables as var
import os

election_data = pd.read_csv(os.path.join(var.party_var_path, "view_election.csv"))
party_data = pd.read_csv(os.path.join(var.party_var_path, "view_party.csv"))

map_label = pd.read_excel(var.codebook, sheet_name= "MAP Label")
map_label.Variables = map_label.Variables.fillna(method="ffill")
countries = list(map_label[map_label.Variables == "country"].Label.unique())
countries.append("United Kingdom")

party_data = party_data[party_data.country_name.isin(countries)]
election_data = election_data[(election_data.country_name.isin(countries)) & (election_data.election_type == "parliament") & (election_data.election_date.str[:4].astype(int) < 2022)]
election_dates = election_data.groupby(by="country_name").max()["election_date"].reset_index()

election_data = election_data.merge(election_dates,how="inner", on=["country_name", "election_date"])


election_data.to_csv(os.path.join(var.output_path, "election_data.csv"), index=False)
#election_data.to_excel(os.path.join(var.output_path, "election_data.xlsx"), index=False)
party_data.to_excel(os.path.join(var.output_path, "party_data.xlsx"), index=False)
