import pandas as pd

file = r"C:\Users\djord\Downloads\Visual maze test analysis study_ready.xlsx"
scores = r"C:\Users\djord\Documents\Coding\VeterinaryAnalysisAutomation\video_results\Visual maze test analysis study example July 2025 Non-Expert.csv"
df = pd.read_excel(file)
df_scores = pd.read_csv(scores)

df['Filename'] = df['Filename'].astype(str).str.strip()
df_scores['Filename'] = df_scores['Filename'].astype(str).str.strip()

merged_df = pd.merge(df, df_scores, on='Filename', how='left')


merged_df = pd.merge(df, df_scores, on= 'Filename', how='left')

"""blind_df = merged_df[merged_df['Blind']== 1]
visual_df = merged_df[merged_df['Visual']== 1]
vis_impaired_df = merged_df[merged_df['Visually Impaired']== 1]

blind_df.to_csv('blind_group.csv', index=False)
visual_df.to_csv('visual_group.csv',index= False)
vis_impaired_df.to_csv('visually_impaired_group.csv',index=False)"""

import numpy as np

def expert_label(row):
    if row['Blind'] == 1:
        return '1'
    elif row['Visual'] == 1:
        return '3'
    elif row['Visually Impaired'] == 1:
        return '3'
    return np.nan

merged_df['Expert Status'] = merged_df.apply(expert_label, axis=1)
merged_df['Visual Status'] = merged_df.apply(expert_label, axis=1)
merged_df.to_csv('merged_results_non_expert.csv')
