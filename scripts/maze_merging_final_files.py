import pandas as pd

df_non_exp = pd.read_csv('merged_results_non_expert.csv')
df_exp = pd.read_csv('merged_results_expert.csv')

merged_final = pd.merge(df_exp, df_non_exp, on='Filename', how='inner')
merged_final.to_excel('merged_final.xlsx')
