import pandas as pd # type: ignore
import re
import matplotlib.pyplot as plt
import sys



data_dict = {}
row_indices_stac_change = []

if len(sys.argv) > 1:
    thickness = float(sys.argv[1])
else:
    thickness = 0.76

if len(sys.argv) > 2:
    disp_stack_change = sys.argv[2].lower() in ['true', '1', 't', 'y', 'yes']
else:
    disp_stack_change = False
    disp_stack_change = True

if len(sys.argv) > 3:
    text_file = sys.argv[3]
else:
    #text_file = "./DATA_BLOCK dbd_testbuffer.txt"
    text_file = "./test.txt"

if len(sys.argv) > 4:
    output_file = sys.argv[4]
else:
    output_file = 'output.xlsx'

upper_trshld = round(1.3 * thickness, 3)
lower_trshld = round(0.8 * thickness, 3)

pattern = re.compile(
    r'bufferData\[(\d+)\]\.(blankFromCell|'
    r'dbdGtyMeasurement\[(1|3)\]|'
    r'visionCorrectionData\[1\]\.(X|Y|Rotation|Quality)|'
    r'dbdTrspMeasurement\[(1|2|3|4)\]) := ([\d\.-]+);'
)

def keep_unique_values(values, threshold=400):
    result = [values[0]]
    for num in values[1:]:
        if num - result[-1] > threshold:
            result.append(num)
    return result

def remove_values_above_range(values, threshold):
    return [num for num in values if num < threshold]

with open(text_file, "r") as file:
     for line in file:
        match = pattern.search(line)
        if match:
            buffer_index = int(match.group(1))
            key = match.group(2)
            value = float(match.group(6))

            if buffer_index not in data_dict:
                data_dict[buffer_index] = {
                    'bufferData': buffer_index,
                    'blankFromCell': None,
                    'dbdGtyMeasurement[1]': None,
                    'dbdGtyMeasurement[3]': None,
                    'X': None,
                    'Y': None,
                    'Rotation': None,
                    'Quality': None,
                    'dbdTrspMeasurement[1]': None,
                    'dbdTrspMeasurement[2]': None,
                    'dbdTrspMeasurement[3]': None,
                    'dbdTrspMeasurement[4]': None,
                }
            if key.startswith("visionCorrectionData[1]."):
                key = key.split(".")[-1]
            data_dict[buffer_index][key] = value

filtered_dict = {
    k: v for k, v in data_dict.items() if v['blankFromCell'] is None or int(v['blankFromCell']) != 0
}

df_new = pd.DataFrame.from_dict(filtered_dict, orient='index')

df_new.to_excel(output_file, index=False)

for index, row in df_new.iterrows():
    if (row['dbdTrspMeasurement[1]'] == 0 and 
        row['dbdTrspMeasurement[2]'] == 0 and 
        row['dbdTrspMeasurement[3]'] == 0 and 
        row['dbdTrspMeasurement[4]'] == 0):
            row_indices_stac_change.append(index)

df_dropped = df_new.drop(row_indices_stac_change)
row_indices_stac_change = keep_unique_values(row_indices_stac_change)
row_indices_stac_change = remove_values_above_range(row_indices_stac_change, len(df_dropped))
print(row_indices_stac_change)
row_indices_stac_change = [137,679, 1218]
print(row_indices_stac_change)
controller1 = ['dbdTrspMeasurement[2]']#['dbdTrspMeasurement[1]', 'dbdTrspMeasurement[2]']
controller2 = ['dbdTrspMeasurement[3]']#['dbdTrspMeasurement[3]', 'dbdTrspMeasurement[4]']

fig, axes = plt.subplots(2, 1, figsize=(28, 10))
df_dropped.plot(x='bufferData', y=controller1, kind='line', ax=axes[0])
axes[0].axhline(y=upper_trshld, color='yellow', linestyle='--', label=f'Threshold ({upper_trshld})')
axes[0].axhline(y=lower_trshld, color='yellow', linestyle='--', label=f'Threshold ({lower_trshld})')
axes[0].set_title("DBD controller 1 measurements tracking")
axes[0].set_xlabel("")
axes[0].set_ylabel("")
axes[0].legend()
axes[0].grid(True)

df_dropped.plot(x='bufferData', y=controller2, kind='line', ax=axes[1])
axes[1].axhline(y=upper_trshld, color='yellow', linestyle='--', label=f'Threshold ({upper_trshld})')
axes[1].axhline(y=lower_trshld, color='yellow', linestyle='--', label=f'Threshold ({lower_trshld})')
axes[1].set_title("DBD controller 2 measurements tracking")
axes[1].set_xlabel("")
axes[1].set_ylabel("")
axes[1].legend()
axes[1].grid(True)

if disp_stack_change:
    for idx in row_indices_stac_change:
        axes[0].axvline(x=df_dropped['bufferData'].iloc[idx], color='yellow', linestyle='--', linewidth=0.75)
        axes[1].axvline(x=df_dropped['bufferData'].iloc[idx], color='yellow', linestyle='--', linewidth=0.75)

#plt.tight_layout()
#plt.show()