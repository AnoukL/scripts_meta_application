# -*- coding: utf-8 -*-
"""
Created on Tue Aug 23 14:30:43 2022

@author: Anouk
"""

import os
import pandas as pd
from os.path import join
from datetime import datetime
import nltk
from nltk.corpus import stopwords
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt

import spacy
nlp = spacy.load("en_core_web_sm")
nlp_dutch = spacy.load('nl_core_news_sm')

os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'


def get_doc_info(row, sentence_field, region):
	if region == "USA" or region == "Sweden":
		doc = nlp(str(row[sentence_field]), disable=['ner'])
	elif region == "Flanders":
		doc = nlp_dutch(str(row[sentence_field]), disable=['ner'])

	row['lemmas'] = " ".join([str(elem).lower()
							 for elem in [token.lemma_ for token in doc]])

	return row


# change the value to black
def black_color_func(word, font_size, position, orientation, random_state=None, **kwargs):
	return("hsl(0,100%, 1%)")


basepath = r"C:\Users\aluypaert\OneDrive - Universiteit Antwerpen\Solidarity frame analysis"
datapath = join(basepath, "output", "onegram")
wordlist_file = join(basepath, "sourcedata", 'ES_wordlist.xlsx')


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

country_files = {"Flanders": join(basepath, "Flanders", "analyzed_manifestos_Flanders.xlsx")				 # , "Sweden": join(basepath, "SV","analyzed_manifestos_sv.xlsm")
				 , "USA": join(basepath, "US", "Tagged manifestos_recoding_042023.xlsx")
				 , "Sweden": join(basepath, "SV", "analyzed_manifestos_sv_eu_analysis_update202305.xlsm")
				 }

columns = ["sentence", "party_name", "year", "SF"]

""" load data """
# get sentences with ES frame
textdata = pd.DataFrame()

for country in country_files:
	filename = country_files[country]
	new_data = pd.read_excel(filename, sheet_name="Sentences")

	print(f"Loaded {len(new_data)} lines for {country}.")

	new_data = new_data[new_data.SF > 0]

	if country == "Sweden":
		new_data["sentence"] = new_data["translation"]
		new_data["SF"].replace({1:1, 2:3, 3:5, 4:7}, inplace=True)

	print(new_data.dtypes)
	new_data = new_data[columns]
	new_data["region"] = country

	# get lemmas
	new_data = new_data.apply(
		get_doc_info, sentence_field='sentence', region=country, axis=1)
	textdata = pd.concat([textdata, new_data], ignore_index=True)

print(textdata)
print(textdata.dtypes)

""" create word cloud """


stopwords_en = set(stopwords.words('english'))
stopwords_en.update(["republican", "democrat", "democrats"], STOPWORDS)

stopwords_nl = set(stopwords.words('dutch'))
stopwords_nl.update(["we"])

common_words = pd.DataFrame()
for region in textdata.region.unique():

	wordcloud_options = {"background_color": "white",
						 "max_words": 60, "prefer_horizontal": 1}

	if region == "USA" or region == "Sweden":
		wordcloud_options["stopwords"] = stopwords_en
		language = "english"
	elif region == "Flanders":
		wordcloud_options["stopwords"] = stopwords_nl
		language = "dutch"

	for frame in textdata.SF.unique():
		print(f"checking {region}, and frame {frame}")

		text = " ".join(textdata.lemmas[(textdata.region == region)
										& (textdata.SF == frame)]).lower()

		if len(text) < 1:
			continue

		# Create and generate a word cloud image:
		wordcloud = WordCloud(**wordcloud_options).generate(text)
		wordcloud.recolor(color_func=black_color_func)

		# Display the generated image:
		print("generating figure")
		plt.figure(dpi=300)
		plt.imshow(wordcloud, interpolation='bilinear')
		plt.axis("off")
		plt.title(f"{region} - {codetodescription[frame]}", size=8)

		savepath = join(
			datapath, f'wordcloud_{region}_{frame}_{wordcloud_options["max_words"]}.png')
		plt.savefig(savepath, dpi=300, bbox_inches='tight')
		print(f"plot saved in {savepath}")
		plt.show()

		for party in textdata[textdata.region == region].party_name.unique():

			print(f"checking {region}, party {party} and frame {frame}")

			text = " ".join(textdata.lemmas[(textdata.party_name == party)
											& (textdata.region == region)
											& (textdata.SF == frame)]).lower()
			if len(text) < 1:
				print("skipping this part")
				continue

			# Create and generate a word cloud image:
			print("generating wordcloud")
			wordcloud = WordCloud(**wordcloud_options).generate(text)
			wordcloud.recolor(color_func=black_color_func)

			# Display the generated image:
			print("generating figure")
			plt.figure(dpi=300)
			plt.imshow(wordcloud, interpolation='bilinear')
			plt.axis("off")
			plt.title(f"{party} - {codetodescription[frame]}", size=8)

			savepath = join(
				datapath, f'wordcloud_{region}_{party}_{frame}_{wordcloud_options["max_words"]}.png')
			plt.savefig(savepath, dpi=300, bbox_inches='tight')
			print(f"plot saved in {savepath}")
			plt.show()

			tokens = nltk.tokenize.word_tokenize(text, language=language)
			freqDist = nltk.FreqDist(w.lower() for w in tokens
									 if w.lower() not in wordcloud_options["stopwords"]
									 and w.isalpha()
									 and (len(w) > 2))

			common_words_temp = pd.DataFrame(freqDist.most_common(wordcloud_options["max_words"]),
											 columns=["word", "frequency"])

			common_words_temp["party"] = party
			common_words_temp["frame"] = frame
			common_words_temp["region"] = region
			common_words_temp["word_share"] = common_words_temp.frequency / \
				len(tokens)

			common_words = pd.concat([common_words, common_words_temp],
									 ignore_index=True)

# export to excel
print(f"{datetime.now()}: Exporting file to {join(datapath, 'wordcloud_numbers.xlsx')}.")
common_words.to_excel(join(datapath, "wordcloud_numbers.xlsx"), index=False)
print(f"{datetime.now()}: Exporting file to {join(datapath, 'wordcloud_numbers.xlsx')}.")
common_words.to_excel(join(datapath, "wordcloud_numbers.xlsx"), index=False)
