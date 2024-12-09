# -*- coding: utf-8 -*-
"""
Created on Thu Jan 19 09:54:48 2023

@author: Anouk
"""


import pandas as pd
from os.path import join
import matplotlib.pyplot as plt
from heatmap_functions import corrplot

basepath = "C:/Users/aluypaert/OneDrive - Universiteit Antwerpen/"
SF_path = join(basepath, "Solidarity frame analysis")

""" correlations are calculated using the numbers from the excel files!!!! (due to how SF % are calculated)

# mappings
codetodescription = {
    1: "GBS",
    3: "CS",
    5: "EBS",
    7: "ES",
    2: "N-GBS",
    4: "N-CS",
    6: "N-EBS",
    8: "N-ES"
}

sv_sf_mappings = {
      1: 1
    , 2: 3
    , 3: 5
    , 4: 7
    }

country_files = {"Flanders": join(SF_path, "Flanders", "analyzed_manifestos_Flanders.xlsx")
                 , "Sweden": join(SF_path, "SV","analyzed_manifestos_sv_eu_analysis.xlsm")
                 , "USA": join(SF_path, "US", "Tagged manifestos_final_update20220921 negative.xlsx")
                 }


correlations_base = pd.DataFrame()
columns_to_keep = ["party_name", "year", "SF"]

all_countries = pd.DataFrame()


#load data and calculate the share for each SF per country, per party
for country in country_files:
    country_data = pd.read_excel(country_files[country], sheet_name="Sentences")

    print(f"Loaded data for {country}")
    print(len(country_data))
    print(country_data.columns)
    print(country_data.SF.unique())

    if country == "Sweden":
        country_data["SF"] = country_data.SF.map(sv_sf_mappings)

    country_data = country_data[country_data.SF.isin([1, 3, 5, 7])]

    print(country_data.SF.unique())
    print(len(country_data))

    country_data = country_data[columns_to_keep]


    print(country_data)

    shares = country_data.groupby(['party_name', "year"])["SF"].value_counts(normalize=True).unstack(fill_value=0)
    shares.rename(columns=codetodescription, inplace=True)

    print(f"Calculate shares, this is the result: {shares}")

    shares["country"] = country
    shares.reset_index(inplace=True)
    shares = shares[shares.year > 1992]

    correlations_base = pd.concat([correlations_base, shares],ignore_index=True)
    all_countries = pd.concat([all_countries, country_data],ignore_index=True)

correlations_base = correlations_base.set_index(["country","party_name","year"])
"""

data = pd.read_excel(join(SF_path, "Tables and graphs", "Results.xlsx")
					 , sheet_name="input python")
data = data.set_index(["Country", "Party", "Year"])
#correlations for belgium
correlations_BE = data.loc["Belgium"].corr()
correlations_SV = data.loc["Sweden"].corr()
correlations_US = data.loc["USA"].corr()

correlations_BE.index.name = "index"
correlations_SV.index.name = "index"
correlations_US.index.name = "index"


plt.figure(figsize=(8, 8))
corrplot(correlations_BE, size_scale=500)
plt.title("Belgium (Flanders)")
savepath = join(SF_path, "output", "BE_correlations.png")
plt.savefig(savepath, dpi=300, bbox_inches='tight')
plt.show()

plt.figure(figsize=(8, 8))
corrplot(correlations_SV, size_scale=500)
plt.title("Sweden", loc="left")
savepath = join(SF_path, "output", "SV_correlations.png")
plt.savefig(savepath, dpi=300, bbox_inches='tight')
plt.show()

plt.figure(figsize=(8, 8))
corrplot(correlations_US, size_scale=500)
plt.title("United States")
savepath = join(SF_path, "output", "US_correlations.png")
plt.savefig(savepath, dpi=300, bbox_inches='tight')
plt.show()


correlations_BE["country"] = "BE"
correlations_SV["country"] = "SV"
correlations_US["country"] = "USA"

correlations = pd.concat([correlations_BE, correlations_SV, correlations_US])
correlations.to_excel(join(SF_path, "output", "correlations.xlsx"))
