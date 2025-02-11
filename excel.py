import pandas as pd # type: ignore


excel_file = './Log.xlsx'
df = pd.read_excel(excel_file, usecols=[1, 3])
df.iloc[:, 1] = pd.to_numeric(df.iloc[:, 1], errors='coerce')

new_columns = [
    'bufferData', 'blankFromCell', 'dbdGtyMeasurement[1]', 'dbdGtyMeasurement[3]',
    'X', 'Y', 'Rotation', 'Quality', 'dbdTrspMeasurement[1]', 'dbdTrspMeasurement[2]', 'dbdTrspMeasurement[3]', 'dbdTrspMeasurement[4]'
]
df_new = pd.DataFrame(columns=new_columns)

for i in range(1, 501):
    find_record = f"bufferData[{i}]"
    for index, record in df.iloc[:, 0].items():
        if (record == find_record) and (df.iloc[(index + 3), 1] != 0):
            new_record = {
                'bufferData': df.iloc[index, 0],
                'blankFromCell': df.iloc[(index + 3), 1],
                'dbdGtyMeasurement[1]': round(df.iloc[index + 5, 1],2),
                'dbdGtyMeasurement[3]': round(df.iloc[index + 7, 1],2),
                'X': df.iloc[index + 11, 1],
                'Y': df.iloc[index + 12, 1],
                'Rotation': df.iloc[index + 13, 1],
                'Quality': df.iloc[index + 14, 1],
                'dbdTrspMeasurement[1]': round(df.iloc[index + 25, 1],2),
                'dbdTrspMeasurement[2]': round(df.iloc[index + 26, 1],2),
                'dbdTrspMeasurement[3]': round(df.iloc[index + 27, 1],2),
                'dbdTrspMeasurement[4]': round(df.iloc[index + 28, 1],2)
            }
            df_new.loc[len(df_new)] = new_record

df_new.to_excel('output.xlsx', index=False)