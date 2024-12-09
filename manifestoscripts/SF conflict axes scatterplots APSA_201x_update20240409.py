# -*- coding: utf-8 -*-
"""
Created on Fri Apr 28 13:34:41 2023

@author: ALuypaert
"""

# -*- coding: utf-8 -*-
"""
Created on Fri Apr 28 13:04:36 2023

@author: ALuypaert
"""
import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

path = r"C:\Users\aluypaert\OneDrive - Universiteit Antwerpen\APSA"
filepath = os.path.join(path, "ISP_APSApaper.csv")

data = pd.read_csv(filepath)

columnstokeep = [c for c in data.columns if "ISP" in c or "overall_std" in c]
columnstokeep.append("country")
columnstokeep.append("party")
columnstokeep.append("year")

data = data[columnstokeep]
data = data[data.year > 2000]

new_names = dict(zip(columnstokeep, [c.replace("|ISP","") for c in columnstokeep]))

data = data.rename(columns=new_names)

abbreviations = {"sp.a": "sp.a"
				 , "SP": "SP"
	, "Groen": "Groen"
	, "Open VLD": "O-VLD"
	, "VLD": "VLD"
	, "CD&V": "CD&V"
	, "CVP": "CVP"
	, "N-VA": "N-VA"
	, "Volksunie": "VU"
	, "Vlaams Belang": "VB"
	, "Vlaams Blok": "VB"
	,"Democratic Party": "DEM"
	,"Republican Party": "REP"
	}

markers_map = {"sp.a": "*"
	,"SP": "*"
	,"Groen": "o"
	,"Agalev": "o"
	,"Open VLD": ">"
	,"VLD": ">"
	,"CD&V": "D"
	,"CVP": "D"
	,"N-VA": "h"
	,"Volksunie": "h"
	,"Vlaams Belang": "v"
	,"Vlaams Blok": "v"
	,"Democratic Party": "s"
	,"Republican Party": "p"
	}

party_colours = {"sp.a": "red"
	, "SP": "red"
	,"Groen": "green"
	, "Agalev": "green"
	,"Open VLD": "gold"
	, "VLD": "gold"
	,"CVP": "orange"
	,"CD&V": "orange"
	,"N-VA": "royalblue"
	,"Volksunie": "royalblue"
	,"Vlaams Belang": "royalblue"
	,"Vlaams Blok": "royalblue"
	,"Democratic Party": "royalblue"
	,"Republican Party": "red"
	}

countries = ["Belgium", "USA"]

data = data[data.country.isin(countries)]

custom = [Line2D([], [], marker=markers_map["sp.a"], markersize=3, color=party_colours["sp.a"], linestyle='None'),
		     Line2D([], [], marker=markers_map["Groen"], markersize=3, color=party_colours["Groen"], linestyle='None'),
			 Line2D([], [], marker=markers_map["Open VLD"], markersize=3, color=party_colours["Open VLD"], linestyle='None'),
			 Line2D([], [], marker=markers_map["CD&V"], markersize=3, color=party_colours["CD&V"], linestyle='None'),
			 Line2D([], [], marker=markers_map["N-VA"], markersize=3, color=party_colours["N-VA"], linestyle='None'),
			 Line2D([], [], marker=markers_map["Vlaams Belang"], markersize=3, color=party_colours["Vlaams Belang"], linestyle='None'),
			 Line2D([], [], marker=markers_map["Democratic Party"], markersize=3, color=party_colours["Democratic Party"], linestyle='None'),
			 Line2D([], [], marker=markers_map["Republican Party"], markersize=3, color=party_colours["Republican Party"], linestyle='None'),]


f = plt.figure(figsize=(18, 18),dpi=1200)
f, axes = plt.subplots(nrows = 4, ncols = 4, sharex=True, sharey = True)
plt.subplots_adjust(hspace=0.12, wspace=0.12)

f.legend(custom, ["sp.a", "Groen", "Open VLD", "CD&V", "N-VA", "Vlaams Belang",
				  "Democratic Party", "Republican Party"],
			 loc='lower left', fontsize=4, frameon=False)

ticks = np.linspace(-2.5,2.5,6)

Xframes = ["GBS", "CS", "EBS", "ES"]
Yframes = ["ES", "EBS", "CS", "GBS"]

col = 0

opposing_parties = {"USA": ["Democratic Party", "Republican Party"],
					"Belgium": ["Groen", "N-VA"]}

opposing_partiesBE = {"Belgium": ["Groen", "N-VA"]}
opposing_partiesUS = {"USA": ["Democratic Party", "Republican Party"]}

BEdata = data[data.country.isin(["Belgium"])]

#first map Belgium data
for Xframe in Xframes:
	row = 3

	for Yframe in Yframes:

		ax = axes[row][col]
		ax.tick_params(axis="both", labelsize=4)
		ax.set_xticks(ticks)
		ax.set_yticks(ticks)
		ax.grid(axis="both", linewidth=0.15)
		ax.set_aspect('equal', adjustable='box')

		if row == 3:
			ax.set_xlabel(Xframe, fontsize=6)

		if col == 0:
			ax.set_ylabel(Yframe, fontsize=6)

		if Xframe == Yframe:
			break

		standard_devationX = BEdata[f"{Xframe}_overall_std"].iloc[0]
		standard_devationY = BEdata[f"{Yframe}_overall_std"].iloc[0]
		for country in opposing_partiesBE:
			party1 = opposing_partiesBE[country][0]
			party2 = opposing_partiesBE[country][1]
			x1 = BEdata[Xframe][BEdata.party == party1].values[0]
			x2 = BEdata[Xframe][BEdata.party == party2].values[0]
			y1 = BEdata[Yframe][BEdata.party == party1].values[0]
			y2 = BEdata[Yframe][BEdata.party == party2].values[0]

			linestyle = "-"

			x_center = min(x1,x2) + (max(x1,x2) - min(x1,x2))/2
			y_center = min(y1,y2) + (max(y1,y2) - min(y1,y2))/2


			if abs(y1-y2) >= 5 * standard_devationY:
				linewidth = 0.4
			else:
				linewidth = 0.2
			ax.plot([x_center, x_center], [y1,y2], "black",
					   linestyle=linestyle, linewidth=linewidth)

			if abs(x1-x2) >= 5 * standard_devationX:
				linewidth = 0.4
			else:
				linewidth = 0.2
			ax.plot([x1, x2], [y_center,y_center], "black",
					   linestyle=linestyle, linewidth=linewidth)

		# draw scatter plots
		for party, country, x, y, year in zip(BEdata["party"],
											BEdata["country"],
											BEdata[Xframe],
											BEdata[Yframe],
											BEdata["year"]):

			c = party_colours[party]
			m = markers_map[party]

			if year < 2000:
				filled = "none"
			else:
				filled = c

			if Yframe != Xframe:
				ax.scatter(x,y, color=filled, s=3, marker=m, edgecolors=c, linewidths=0.4)

		row -= 1

	col +=1

USdata = data[data.country.isin(["USA"])]

Xframes = ["CS", "EBS", "ES"]
Yframes = ["GBS", "CS", "EBS", "ES"]

col = 1

for Xframe in Xframes:
	row = 0

	for Yframe in Yframes:
		ax = axes[row][col]
		ax.grid(axis="both", linewidth=0.15)
		ax.set_xticks(ticks)
		ax.set_yticks(ticks)
		ax.grid(axis="both", linewidth=0.15)
		ax.set_aspect('equal', adjustable='box')

		if Xframe == Yframe:
			break

        #draw crosses
		standard_devationX = USdata[f"{Xframe}_overall_std"].iloc[0]
		standard_devationY = USdata[f"{Yframe}_overall_std"].iloc[0]
		for country in opposing_partiesUS:
			party1 = opposing_partiesUS[country][0]
			party2 = opposing_partiesUS[country][1]
			x1 = USdata[Xframe][USdata.party == party1].values[0]
			x2 = USdata[Xframe][USdata.party == party2].values[0]
			y1 = USdata[Yframe][USdata.party == party1].values[0]
			y2 = USdata[Yframe][USdata.party == party2].values[0]


			linestyle = "-"

			x_center = min(x1,x2) + (max(x1,x2) - min(x1,x2))/2
			y_center = min(y1,y2) + (max(y1,y2) - min(y1,y2))/2


			if abs(y1-y2) >= 5 * standard_devationY:
				linewidth = 0.4
			else:
				linewidth = 0.2
			ax.plot([x_center, x_center], [y1,y2], "black",
					   linestyle=linestyle, linewidth=linewidth)

			if abs(x1-x2) >= 5 * standard_devationX:
				linewidth = 0.4
			else:
				linewidth = 0.2
			ax.plot([x1, x2], [y_center,y_center], "black",
					   linestyle=linestyle, linewidth=linewidth)
            
        #draw points
		for party, country, x, y, year in zip(USdata["party"],
											USdata["country"],
											USdata[Xframe],
											USdata[Yframe],
											USdata["year"]):

			c = party_colours[party]
			m = markers_map[party]

			if year < 2000:
				filled = "none"
			else:
				filled = c

			if Yframe != Xframe:
				ax.scatter(x,y, color=filled, s=3, marker=m, edgecolors=c, linewidths=0.4)

		row += 1
	col +=1


plt.savefig(os.path.join(path,'conflict_axis_customscatter_201x.jpg'),dpi=1200)
plt.show()
