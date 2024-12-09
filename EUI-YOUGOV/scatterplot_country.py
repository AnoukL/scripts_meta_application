# -*- coding: utf-8 -*-
"""
Created on Tue Apr 25 10:36:04 2023

@author: ALuypaert
"""


import os
import pandas as pd
import variables as var
import matplotlib.pyplot as plt
import numpy as np

""" import data that has been preprocessed """
data = pd.read_excel(os.path.join(var.output_path, "data_for_maps.xlsx"))

columns_to_keep = [c for c in data.columns if "EU" not in c]
data = data[columns_to_keep]
data.columns = [c.replace("_share","") for c in data.columns]

frames = ['ESu_1', 'CS_2', 'CS_3', 'ESu_4', 'EBS_6', 'ESp_7', 'GBS_2']
fin_frames = ['ESu_fin_1', 'CS_fin_2', 'CS_fin_3', 'ESu_fin_4', 'EBS_fin_6',
			  'ESp_fin_7', 'GBS_fin_2']

ticks = np.linspace(0,1,5)

f = plt.figure(dpi=4400)
f, axes = plt.subplots(nrows = len(frames), ncols = len(frames), sharex=True, sharey = True)
f.set_size_inches(35,35)

col = 0

fontsize = 20

for Xframe in frames:
	row = len(frames) -1

	for Yframe in list(reversed(frames)):

		ax = axes[row][col]
		ax.tick_params(axis="both", labelsize=fontsize)
		ax.set_xticks(ticks, fontsize=fontsize)
		ax.set_yticks(ticks, fontsize=fontsize)
		ax.grid(axis="both", linewidth=0.15)

		if row == len(frames) -1:
			ax.set_xlabel(Xframe, fontsize=fontsize)

		if col == 0:
			ax.set_ylabel(Yframe, fontsize=fontsize)

		if Xframe == Yframe:
			break


		# draw scatter plots
		for country, x, y, in zip(data["ISO"],
									data[Xframe],
									data[Yframe]):

			if Yframe != Xframe:
				ax.scatter(x,y, color="black", s=fontsize, marker="o")
				ax.text(x,y,country)

		row -= 1

	col +=1

plt.savefig(os.path.join(var.output_path, 'scatterplot.png'))
