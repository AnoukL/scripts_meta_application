# -*- coding: utf-8 -*-
"""
Created on Thu Mar 30 14:26:20 2023

@author: ALuypaert
"""


import os
import pandas as pd
from functions import log_regression
import variables as var
import numpy as np
import matplotlib.pyplot as plt
from math import ceil

regression_goal = "SF_centre-party_nol-r"

map_party_to_country = pd.read_csv(os.path.join(var.output_path, "party_to_country.csv"))

""" import data that has been preprocessed """
log_df = pd.read_csv(var.reg_data, sep=",")

SF_frames = ["CS_3", "EBS_6", "ESp_7", "GBS_2"]


partylr = pd.read_csv(os.path.join(var.output_path, "partylr.csv"), sep=",")

total_frames = SF_frames

total_output = ""
coef_table = pd.DataFrame()
middle = 4

#ref_parties = pd.read_excel(os.path.join(var.party_var_path, "Ref party analysis.xlsx"), sheet_name="Filtered")

for country in log_df.country.unique():

	country_parties = partylr[partylr["country"] == country]

	#make sure other is not selected as referent category
	country_parties_middle_sorted = country_parties.iloc[(country_parties['l-r_party'] - middle).abs().argsort(),:]
	country_parties_filtered = country_parties_middle_sorted[country_parties_middle_sorted.voted_party.str.contains("Other") == False].copy()

	ref_party = f"voted_party_{country_parties_filtered.iloc[0]['voted_party']}"

	country_parties_lr_sorted = country_parties.iloc[country_parties['l-r_party'].argsort(),:]
	country_party_list = country_parties_lr_sorted.voted_party.to_list()

	for frame in total_frames:

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
	country_groups = ["UK",
				   "Netherlands", "Germany", "France",
				   "Finland", "Sweden", "Denmark",
				   "Croatia", "Bulgaria", "Romania", "Slovakia", "Hungary",
				   "Poland", "Lithuania",
				   "Italy", "Spain", "Greece"]
	frame_data["country"] = pd.Categorical(frame_data['country'],
													country_groups)
	frame_data = frame_data.sort_values(by=["country","ref_party","l-r"], ascending=False)
	frame_data["plot_name"] = frame_data["index"].map(index_to_plotname)

	analysis_data = pd.concat([analysis_data,frame_data],ignore_index=True)

	fig1, ax1 = plt.subplots(1, dpi=1200, figsize=(10,6))

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


		if significance < 0.001:
			markersize = 7
		elif significance < 0.01:
			markersize = 6
		elif significance < 0.05:
			markersize = 5
		else:
			markersize = 5

		limit = ceil(max(frame_data[plotted_value].max(), abs(frame_data[plotted_value].min())))
		ax1.set_xlim([-limit, limit])
		ax1.plot((coef),(y),marker= party_marker, color=colours[family], markersize=vote_size)
		plt.title(label=frame)
		#plt.axvline(x = 0, color = 'black', linestyle = '-', linewidth=0.5)
		ax1.set_yticks(range(len(frame_data)),list(frame_data['plot_name']),fontsize=8)

		""" add country

		frame_data = frame_data.assign(position=range(len(frame_data)))
		locations = list(frame_data.groupby("country").max()["position"])
		#locations = [loc/10 for loc in locations]

		ax2 = ax1.twinx()

		ax2.spines["left"].set_position(("axes", -0.10))
		ax2.tick_params('both', length=0, width=0, which='minor')
		ax2.tick_params('both', direction='in', which='major')
		ax2.yaxis.set_ticks_position("left")
		ax2.yaxis.set_label_position("left")

		#locations = [0,0.5,1,2,3,4]
		ax2.set_yticks([sorted(locations)])
		ax2.yaxis.set_major_formatter(ticker.NullFormatter())
		ax2.yaxis.set_minor_locator(ticker.FixedLocator(sorted(locations)))
		ax2.yaxis.set_minor_formatter(ticker.FixedFormatter(countries))
		"""
	plt.savefig(os.path.join(var.output_path,
						  f'confidenceplot_{frame}_{vote_treshold}_{plotted_value}_{regression_goal}.png'),
			 bbox_inches='tight')

analysis_data.to_excel(os.path.join(var.output_path,
									f"modelanalysis_data_nolr_{regression_goal}.xlsx"),
					   index=False)
