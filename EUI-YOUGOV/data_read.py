# -*- coding: utf-8 -*-
"""
Created on Mon Mar  6 15:39:41 2023

@author: ALuypaert
"""

"""
[exp1_all_2] When thinking about the kind of society you’d like to live in, which
THREE of these are most important to your definition of a good society?
(Please select up to three answer options)

<1> A society in which everyone has access to quality healthcare
<2> A society in which no-one is homeless
<3> A society in which everyone has a basic income level 	CS
<4> A society in which everyone has access to a good education ESu
<6> A society in which hard work and initiative pays EBS
<7> A society in which men and women are equal in work, pay and household chores ESp
<8 fixed xor> None of these
<9 fixed xor> Don’t know


[Q62] Some people talk about 'left', 'right' and 'centre' to describe parties and politicians.
With this in mind, where would you place yourself on this scale?
<1> Very left-wing
<2> Fairly left-wing
<3> Slightly left-of-centre
<4> Centre
<5> Slightly right-of-centre
<6> Fairly right-wing
<7> Very right-wing
<8> Don’t know
<100> prefer not to say

[exp1_all_3] Which of these would you be prepared to support with higher taxes?
(Please select ALL those which you be prepared to pay more for)
<1> A society in which everyone has access to quality healthcare CS
<2> A society in which no-one is homeless CS
<3> A society in which everyone has a basic income level CS
<4> A society in which everyone has access to a good education ESu
<6> A society in which hard work and initiative pays EBS
<7> A society in which men and women are equal in work, pay and household chores ESp
<8 fixed xor> None of these
<9 fixed xor> Don’t know


GBS?
[Q18_r] Some people think that the member states of the European Union should
mostly spend their resources on their own countries. Other people think that
the member states of the European Union should pool their resources and spend
them on all countries of the European Union collectively.
What about you – on a scale of 0 to 10, where 0 means 'Spending resources only on your own country’,
and 10 means 'Spending resources equally on all countries in the European Union',
where would you put your opinion?
<0> 0 - Spend resources only on own country
10 - Spend resources equally on all countries in the European Union
<11> Don’t know


[Q18a] Which statement comes closer to your view…?
<1> ‘I would prefer all of my taxes to be spent on helping the people of $Qcountry’
<2> ‘I would prefer some of my taxes to be spent on helping people in other countries in the European Union’
<3> Don’t know


[New_Q70] To what extent, if at all, are you proud of being $Qnationality?
<1> Not proud at all
<2> Not very proud
<3> A little proud
<4> Very proud
<5> Don’t know

[Q13_r] Please tell us in which Europe you would prefer to live
<2> A global Europe that acts as a leader on climate, human rights and global peace   => ES
<3> A protective Europe that defends its citizens against internal and external threats => GBS
<4> A market Europe stressing economic integration, growth and jobs => EBS
<6> A social Europe that promotes equivalent and adequate living standards and social protection  =>CS
<7 fixed xor> None of the above
<8 fixed xor> Don’t know

Interval = L-R

Dummies = Age, Country, ES-EBS-CS, Gender, Voted_party

"""

import os
import pandas as pd
import numpy as np
import variables as var



""" import data """
data = pd.read_csv(var.datafile, sep=",")
map_label = pd.read_excel(var.codebook, sheet_name= "MAP Label")
map_label.Variables = map_label.Variables.fillna(method="ffill")
map_var = pd.read_excel(var.codebook, sheet_name= "MAP Variable")

""" transform and clean data """

# create column that contains all party votes
vote_party = {"UK": "pastvote_ge_2019"
			 , "Slovakia":'pastvote20SK'
			 , "Netherlands":'pastvote2020NL'
			 , "Hungary":'pastvote2018HU'
			 , "Croatia":'pastvote2020HR'
			 , "Bulgaria":'pastvote21BG_we'
			 , "Lithuania":'pastvote2020LT'
			 , "Romania":'pastvote2020RO'
			 , "Greece":'pastvote2019EL'
			 , "Poland":'pastvoteSejm_2019'
			 , "Spain":'ES_pastvoteNov_2019'
			 , "France": 'Presidential_vote17'
			 , "Germany":'q_BTW21_Quote'
			 , "Italy":'PDL_Vote_18_Quote_IT'
			 , "Denmark": "FT19_dk"
			 , "Sweden": "FT18"
			 , "Finland": "FT19"
			 }

map_country_to_label = dict(zip(map_label[map_label.Variables == "country"]['Value'],
								map_label[map_label.Variables == "country"]['Label']))


def get_vote(row):
	country_name = map_country_to_label[row.country]
	fieldname = vote_party[country_name]
	return row[fieldname]

data["voted_party"] = data.apply(get_vote, axis =1)

#remove all unnecessary fields
fields_to_keep = [x for x in list(data.columns) if x.startswith("exp1_all_2") or x.startswith("exp1_all_3")]
fields_to_keep = fields_to_keep + ["country", "age_grp_all", "gender_all", "Q18_r",
								    "Q62", "Q13_r", "voted_party", "New_Q70", "Q18a"]
data = data[fields_to_keep]

# add filter column to retain only those respondents that chose 1-2-3 categories
sum_cols = data['exp1_all_2_1'] + data['exp1_all_2_2'] + data['exp1_all_2_3'] \
	+ data['exp1_all_2_4'] + data['exp1_all_2_5'] + data['exp1_all_2_6'] + data['exp1_all_2_7']
data["chose3"]= sum_cols.apply(lambda x: 1 if x == 3 else 0)
data["chose2"]= sum_cols.apply(lambda x: 1 if x == 2 else 0)
data["chose1"]= sum_cols.apply(lambda x: 1 if x == 1 else 0)
data["chose_min2"]= sum_cols.apply(lambda x: 1 if x >= 2 else 0)
data["chose_min1"]= sum_cols.apply(lambda x: 1 if x >= 1 else 0)


data["no_fin_choices"] = data['exp1_all_3_1'] + data['exp1_all_3_2'] + data['exp1_all_3_3'] \
	+ data['exp1_all_3_4'] + data['exp1_all_3_5'] + data['exp1_all_3_6'] + data['exp1_all_3_7']

#define missing
data.Q62 = data.Q62.replace([8, 100], np.NaN)
data.Q18_r = data.Q18_r.replace([11], np.NaN)
data.Q13_r = data.Q13_r.replace([8], np.NaN)
data.New_Q70 = data.New_Q70.replace([5], np.NaN)
data.Q18a = data.Q18a.replace([3], np.NaN)

"""
party_other = ["Ne znam/ Nisam glasovao/la", "Havde ikke stemmeret", "Husker ikke"
		, "Vil ikke svare","Stemte ikke/stemte blankt", "Andet parti/Kandidat uden for partierne"
		, "I didn't vote or abstain", "No, I did not vote, I was not yet 18"
		,"No, I did not vote", "Prefer not to say", "Yes, but I can't remember which candidate I voted for"
		, "Yes, I voted blank", "I can't remember if I voted or not"
		, "Skipped, Don't know", "Non-voter (invalid, did not vote, ineligible)"
		, "Other party", "voted invalid/ blank", "I don't remember"
		, "Blank", "Void vote", "Other party", "Voted blank", "Did not vote"
		, "Don't know", 'Yes, I voted for another candidate (Nathalie Arthaud, \
		  Jean Lassalle, François Asselineau, Philippe Poutou, Jacques Chem']
data["voted_party"] = data["voted_party"].replace(party_other, "Other")
"""

#make sure others are unique per country
data["voted_party"] = np.where(data["voted_party"] == "Other", data["voted_party"].str.cat(data['country'].map(str),sep="_"), data["voted_party"])

# calculate party l-r pos based on respondents' average
partylr = data.groupby(["country", "voted_party"]).mean()["Q62"].reset_index().rename(columns={"Q62": "l-r_party"})
data = data.merge(partylr, how="left", left_on=["country", "voted_party"], right_on=["country", "voted_party"])
partylr.to_csv(os.path.join(var.output_path, "partylr.csv"), sep=",", index=False)
partylr["country_name"] =  partylr.country.map(map_country_to_label)
partylr.to_excel(os.path.join(var.output_path, "partylr.xlsx"), index=False)

data.index.name = "respondent_id"
data = data.rename(columns = {"exp1_all_2_1": "ESu_1",
						"exp1_all_2_2" : "CS_2",
						"exp1_all_2_3" : "CS_3",
						"exp1_all_2_4" : "ESu_4",
						"exp1_all_2_6" : "EBS_6",
						"exp1_all_2_7" : "ESp_7",
						"Q18_r" : "GBS",
						"New_Q70" : "GBS_2",
						"Q18a": "GBS_fin_2",
						"exp1_all_3_1" : "ESu_fin_1",
						"exp1_all_3_2" : "CS_fin_2",
						"exp1_all_3_3" : "CS_fin_3",
						"exp1_all_3_4" : "ESu_fin_4",
						"exp1_all_3_6" : "EBS_fin_6",
						"exp1_all_3_7" : "ESp_fin_7",
						"Q62" : "l-r_indv",
						"Q13_r": "EU_type"})
data.drop(columns=["exp1_all_3_5",
					"exp1_all_3_8",
					"exp1_all_3_9",
					"exp1_all_2_5",
					"exp1_all_2_8",
					"exp1_all_2_9"
					], inplace=True)

data["gender_all"] = data.gender_all.map({1:"male", 2:"female"})
data["GBS_2"] = data.GBS_2.map({1:0, 2:0, 3:1, 4:1})
data["GBS_fin_2"] = data.GBS_fin_2.map({1:1, 2:0})
data["EU_type"] = data.EU_type.map({2:"global", 3:"protective", 4: "market", 6:"social", 7: "None"})

data[["voted_party","country"]].drop_duplicates().to_csv(os.path.join(var.output_path, "party_to_country.csv"), sep=",", index=False)
"""
#create choice sets
choice_options = ["ESu_1","CS_2","CS_3","ESu_4", "EBS_6","ESp_7"]
choicesets = list(itertools.combinations(choice_options, 3)) + \
	list(itertools.combinations(choice_options, 2))


for choiceset in choicesets:
	set_name = str(choiceset).replace("', ", "-").replace("'","")
	var.idv.append(set_name)

	if len(choiceset) == 2:
		conditions2 = [(data.chose2 == 1) & (data[choiceset[0]] + data[choiceset[1]] == 2)]
		data[set_name] = np.select(conditions2, [1], default = 0)
	elif len(choiceset) == 3:
		conditions3 = [(data.chose3 == 1) & (data[choiceset[0]] + data[choiceset[1]] + data[choiceset[2]] == 3)]
		data[set_name] = np.select(conditions3, [1], default = 0)
"""
# create final cleaned data that can be used for regression
data_cleaned = data[(data.chose3 == 1) & (~pd.isna(data["GBS_2"])) &
					(~pd.isna(data["l-r_indv"]))].copy()

#Dummification of variables
data_cleaned = pd.get_dummies(data_cleaned, columns = ["gender_all", "l-r_indv",
													   "voted_party", "EU_type"])


""" exports for regression
"""

data_cleaned.to_csv(var.reg_data, sep=",")


"""
Calculations for analysis in excel on individual, party, and country level + filters
"""

data.country = data.country.map(map_country_to_label)
data = pd.get_dummies(data, columns = ["EU_type"])


filters = ["none", "chose1", "chose2", "chose3", "chose_min2", "chose_min1"]
levels = ["country", "country-party", "individual"]

aggregations = {"ESu_1": "sum", "CS_2": "sum", 'CS_3': 'sum',"ESu_4": "sum",
		'EBS_6': 'sum',  'ESp_7': 'sum',
		"ESu_fin_1": "sum", "CS_fin_2": "sum", 'CS_fin_3': 'sum', "ESu_fin_4": "sum",
		'EBS_fin_6': 'sum',  'ESp_fin_7': 'sum',
		'GBS': "mean", "GBS_2": "sum", "GBS_fin_2":"sum",
		'respondent_id': 'count', "no_fin_choices": "mean",
		"EU_type_None":"sum", "EU_type_global":"sum","EU_type_market":"sum",
		"EU_type_protective":"sum",	"EU_type_social": "sum"}
shares_to_calc = ["ESu_1", "CS_2", "CS_3", "ESu_4","EBS_6","ESp_7", "GBS_2",
				  "ESu_fin_1", "CS_fin_2","CS_fin_3","ESu_fin_4","EBS_fin_6",
				  "ESp_fin_7", "GBS_fin_2",
				  "EU_type_None","EU_type_global","EU_type_market",
				  "EU_type_protective","EU_type_social"]

"""
for choiceset in choicesets:
	set_name = str(choiceset).replace("', ", "-").replace("'","")
	aggregations[set_name] = "sum"
	shares_to_calc.append(set_name)
"""
full_data_export = pd.DataFrame()

for f in filters:
	if f == "chose3":
		filtered_data = data[data.chose3 == 1].copy()
	elif f == "chose2":
		filtered_data = data[data.chose2 == 1].copy()
	elif f == "chose1":
		filtered_data = data[data.chose1 == 1].copy()
	elif f == "chose_min2":
		filtered_data = data[data.chose_min2 == 1].copy()
	elif f == "chose_min1":
		filtered_data = data[data.chose_min1 == 1].copy()
	elif f == "none":
		filtered_data = data.copy()

	for l in levels:
		if l == "country":
			grouped = filtered_data.reset_index().groupby(['country']).agg(aggregations).reset_index()
		elif l == "country-party":
			grouped = filtered_data.reset_index().groupby(['country', "voted_party", "l-r_party"]).agg(aggregations).reset_index()
		elif l == "individual":
			grouped = filtered_data.copy()
			grouped["count"] = 1
			grouped = grouped.reset_index()

		if l != "individual":
			grouped = grouped.rename(columns={"respondent_id": "count"})

		grouped["level"] = l
		grouped["filter"] = f

		for field in shares_to_calc:
			field_name = f"{field}_share"
			grouped[field_name] = grouped[field]/grouped["count"]

		full_data_export = pd.concat([full_data_export, grouped])

full_data_export.to_excel(os.path.join(var.output_path, "data_excel_analysis.xlsx"),
						  index=False)


#data for maps
fields = [col for col in full_data_export.columns if "share" in col] + ["count"]
ISO_codes = pd.read_excel(var.country_data, sheet_name="Sheet1")[["Country", "ISO"]]
fields = fields + ["country"]
country_data = full_data_export[(full_data_export.level == "country") &
								(full_data_export["filter"] == "none")][fields]
country_data = country_data.merge(ISO_codes, how="left", left_on="country",
								  right_on="Country").drop(columns=["Country"])

country_data.to_excel(os.path.join(var.output_path, "data_for_maps.xlsx"), index=False)
