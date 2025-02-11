import pandas as pd # type: ignore


text_file = './LDATA_BLOCK dbd_testbuffer.txt'
with open(text_file, "r") as file:
     for line in file:
        print(line.strip())


new_columns = [
    'bufferData', 'blankFromCell', 'dbdGtyMeasurement[1]', 'dbdGtyMeasurement[3]',
    'X', 'Y', 'Rotation', 'Quality', 'dbdTrspMeasurement[1]', 'dbdTrspMeasurement[2]', 'dbdTrspMeasurement[3]', 'dbdTrspMeasurement[4]'
]
df_new = pd.DataFrame(columns=new_columns)

for i in range(1, 501):
    new_record = {
        'bufferData': 4,
        'blankFromCell': 4,
        'dbdGtyMeasurement[1]': 4,
        'dbdGtyMeasurement[3]': 4,
        'X': 4,
        'Y': 4,
        'Rotation': 4,
        'Quality': 4,
        'dbdTrspMeasurement[1]': 4,
        'dbdTrspMeasurement[2]': 4,
        'dbdTrspMeasurement[3]': 4,
        'dbdTrspMeasurement[4]': 4
    }
    df_new.loc[len(df_new)] = new_record

df_new.to_excel('output.xlsx', index=False)