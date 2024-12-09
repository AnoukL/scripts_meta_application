# -*- coding: utf-8 -*-
"""
Created on Tue Mar 14 10:47:35 2023

@author: ALuypaert
"""

import numpy as np
import statsmodels.api as sm
import pandas as pd



def log_regression(df, IV_fields, DV_field):
	y = df[DV_field]
	x = df[IV_fields]
	try:
		log_reg = sm.Logit(y, sm.add_constant(x)).fit()
		output = log_reg.summary().as_csv() + "\n\n"
		coef_df = pd.read_html(log_reg.summary().tables[1].as_html(), header=0, index_col=0)[0]
		signif_conditions = [coef_df['P>|z|'] < 0.001, coef_df['P>|z|'] < 0.010, coef_df['P>|z|'] < 0.050]
		coef_df["significance"] = np.select(signif_conditions, ["***", "**", "*"], default = 0)
	except np.linalg.LinAlgError as err:
		coef_df = pd.DataFrame({"significance": [err], "coef":["could not calculate"]})
		output = f"Could not calculate model because of {str(err)} \n\n"
		print(output)

	coef_df["DV"] = DV_field

	return output, coef_df


def lin_regression(df, IV_fields, DV_field):
	y = df[DV_field]
	x = df[IV_fields]
	try:
		lin_reg = sm.OLS(y, sm.add_constant(x)).fit()
		output = lin_reg.summary().as_csv() + "\n\n"
		coef_df = pd.read_html(lin_reg.summary().tables[1].as_html(), header=0, index_col=0)[0]
		print(coef_df.columns)
		coef_df["odds ratio"] = np.exp(coef_df.coef)
		signif_conditions = [coef_df['P>|t|'] < 0.001, coef_df['P>|t|'] < 0.010, coef_df['P>|t|'] < 0.050]
		coef_df["significance"] = np.select(signif_conditions, ["***", "**", "*"], default = 0)
	except np.linalg.LinAlgError as err:
		coef_df = pd.DataFrame({"significance": [err], "coef":["could not calculate"]})
		output = f"Could not calculate model because of {str(err)} \n\n"
		print(output)

	coef_df["DV"] = DV_field

	return output, coef_df
