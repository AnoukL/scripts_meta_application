# -*- coding: utf-8 -*-
"""
Created on Wed Mar 29 15:12:50 2023

@author: ALuypaert
"""


import os
import pandas as pd
from functions import log_regression
import variables as var
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from math import ceil

regression_goal = "SF_fixed-party_nol-r"

map_party_to_country = pd.read_csv(os.path.join(var.output_path, "party_to_country.csv"))

""" import data that has been preprocessed """
log_df = pd.read_csv(var.reg_data, sep=",")

SF_frames = ["CS_3", "EBS_6", "ESp_7", "GBS_2", "ESu_4"]


partylr = pd.read_csv(os.path.join(var.output_path, "partylr.csv"), sep=",")

total_frames = SF_frames

total_output = ""
coef_table = pd.DataFrame()
middle = 4

ref_parties = pd.read_excel(os.path.join(var.party_var_path, "Ref party analysis.xlsx"), sheet_name="Filtered")

for country in log_df.country.unique():

	country_parties = partylr[partylr["country"] == country]
	country_parties_lr_sorted = country_parties.iloc[country_parties['l-r_party'].argsort(),:]
	country_party_list = country_parties_lr_sorted.voted_party.to_list()

	for frame in total_frames:

		ref_party = ref_parties[(ref_parties.country == var.map_country_to_label[country])
						  & (ref_parties.DV == frame)
						  & (ref_parties.chosen =="yes")]["index"].values[0]
		party_var = [f"voted_party_{party}" for party in country_party_list if f"voted_party_{party}" != ref_party]

		IV_fields = party_var

		print(f"Performing log regression for country {var.map_country_to_label[country]} \
				on {frame} using fields {IV_fields} ")
		output, coef_df = log_regression(log_df[log_df.country == country], IV_fields, frame)

		coef_df["country"] = var.map_country_to_label[country]
		coef_df["model"] = regression_goal

		if len(coef_df) > 1:
			model_constant = coef_df.loc["const"].coef
			coef_df["plot_coef"] = np.where(coef_df.index.astype(str).str.contains("voted"),
									  coef_df.coef + model_constant,
									  coef_df.coef)
		coef_df["ref_party"] = ref_party.replace('voted_party_','')
		coef_table = pd.concat([coef_table, coef_df.reset_index()], ignore_index=True)
		total_output = total_output + f"Results for {country}, {var.map_country_to_label[country]} for solidarity frame {frame} with {ref_party.replace('voted_party_','')} as referent party \n" + output + "\n"

#open text file
with open(os.path.join(var.output_path, f"{regression_goal}_model_output.txt"), "w", encoding="utf-8") as f:
	f.write(total_output)


""" create plots"""

# add party information
party_data = pd.read_excel(os.path.join(var.party_var_path, "partylinks.xlsx"), sheet_name = "Partylist EUI")
coef_table["party_variable"] = np.where(coef_table["index"].str.contains("voted_"), 1,0)
coef_table["index"] = coef_table["index"].str.replace("voted_party_", "")
coef_table = coef_table.merge(party_data[["voted_party_yougov", "Vote share", "Family", "party_name_short", "l-r"]],
							   how="left", right_on="voted_party_yougov",
							   left_on="index")
coef_table.drop(columns="voted_party_yougov",inplace=True)
coef_table.to_excel(os.path.join(var.output_path, f"{regression_goal}_model_coef.xlsx"), index=False)
coef_table["plot_name"] = coef_table['party_name_short'] + " " + coef_table['l-r'].round(2).astype(str)
index_to_plotname = dict(zip(coef_table["index"], coef_table["plot_name"]))

colours = {'Social democracy': "red",
		   "Left": "red",
   	       'Communist/Socialist': "darkred",
		   'Liberal': "gold",
		   'Agrarian': "gold",
		   'Christian democracy': "orange",
	       'Green/Ecologist': "green",
		   'Right-wing': "royalblue",
		   'Conservative': "royalblue"
		   }

vote_treshold = 10
plotted_value = "plot_coef" #or "coef"

# create table for ref parties
fields = ["ref_party", "DV", "country", "[0.025", '0.975]', "coef", "plot_coef"]
ref_party_data = coef_table[(coef_table["index"]=="const")][fields].copy()


analysis_data = pd.DataFrame()

# confidence interval plots per frame
for frame in total_frames:
	frame_data = coef_table[(coef_table.DV == frame)
						 & (coef_table.party_variable==1)
						 & (coef_table["P>|z|"] < 0.05)
						 & (coef_table["Vote share"] > vote_treshold)
						 ]

	countries = frame_data.country.unique()
	# add the referent party data
	frame_ref_parties = ref_party_data[(ref_party_data.DV == frame)
					  & (ref_party_data.country.isin(countries))].copy()
	frame_ref_parties.rename(columns={"ref_party":"index"}, inplace=True)
	frame_ref_parties["ref_party"] = 1
	frame_ref_parties = frame_ref_parties.merge(party_data[["voted_party_yougov",
														 "Family",
														 "Vote share"]],
										 how="left",
										 right_on="voted_party_yougov",
										  left_on="index")
	frame_ref_parties.drop(columns = "voted_party_yougov", inplace=True)
	frame_data = pd.concat([frame_data,frame_ref_parties])

	# set the sorting for the countries
	sorted_countries = frame_data.groupby("country").agg({"plot_coef":["min","max"]}).reset_index()
	sorted_countries.columns = sorted_countries.columns.droplevel(0)
	sorted_countries["difference"] =  sorted_countries["max"] - sorted_countries["min"]
	sorted_countries.sort_values(by="difference", ascending=False, inplace=True)
	sorted_countries.columns = ['country', 'min', 'max', 'difference']

	country_groups = list(sorted_countries.country.unique())
	frame_data["country"] = pd.Categorical(frame_data['country'],
													country_groups)
	frame_data = frame_data.sort_values(by=["country","ref_party","l-r"], ascending=False)
	frame_data["plot_name"] = frame_data["index"].map(index_to_plotname)

	analysis_data = pd.concat([analysis_data,frame_data],ignore_index=True)

	fig1, ax1 = plt.subplots(1, dpi=1200, figsize=(10,6))
	locations_country_y = []

	plt.title(label=frame)

	frame_data['rowno'] = range(len(frame_data))
	pos_calc = frame_data.groupby(by="country").agg({"rowno": ["min", "max"]})
	pos_calc.columns = pos_calc.columns.droplevel()
	frame_data = frame_data.merge(pos_calc.reset_index(), how="left", left_on="country",
							   right_on="country")
	frame_data["country_pos"] =  frame_data["min"] + \
								(frame_data["max"] - frame_data["min"]) / 2


	for i in range(len(frame_data["country"])):
		if frame_data["country"].iloc[i] != frame_data["country"].iloc[i-1]:
			if i != 0:
				plt.axhline(y = i-0.5, color = 'grey', linestyle = "dashed", linewidth=0.1)

	limit = ceil(max(frame_data[plotted_value].max(), abs(frame_data[plotted_value].min())))
	ax1.set_xlim([-limit, limit])

	ax1.set_yticks(range(len(frame_data)),
				 list(frame_data['plot_name']),
				 fontsize=8)

	ax2 = ax1.twinx()
	ax2.set_yticks(frame_data["country_pos"].unique(),
				list(frame_data['country'].unique()),
				fontsize=8)
	ax2.tick_params(axis=u'both', which=u'both',length=0)

	for party, coef, y, family, significance, vote_share in zip(frame_data["index"],
										frame_data[plotted_value],
										range(len(frame_data)),
										frame_data["Family"],
										frame_data["P>|z|"],
										frame_data["Vote share"]):

		if frame_data[frame_data["index"] == party].ref_party.values == 1:
			party_marker = "s"
		else:
			party_marker = "o"

		if vote_share > 30:
			vote_size = 7.5
		elif vote_share > 20:
			vote_size = 6
		elif vote_share > 15:
			vote_size = 4.5
		else:
			vote_size = 3

		ax1.plot((coef),(y),marker= party_marker,
				   color=colours[family],
				   markersize=vote_size)

		ax2.plot((coef),(y),marker= party_marker,
				   color=colours[family],
				   markersize=vote_size)

	plt.savefig(os.path.join(var.output_path,
						  f'confidenceplot_{frame}_{vote_treshold}_{plotted_value}_nolr.png')
			 #, bbox_inches='tight'
			 )

analysis_data.to_excel(os.path.join(var.output_path, "modelanalysis_data_nolr.xlsx"),
					   index=False)
