import pandas as pd # type: ignore
import re
import matplotlib.pyplot as plt
import sys


text_file = "./DATA_BLOCK dbd_testbuffer.txt"
data_dict = {}

if len(sys.argv) > 1:
    thickness = float(sys.argv[1])
else:
    thickness = 0.76

upper_trshld = round(1.3 * thickness, 3)
lower_trshld = round(0.7 * thickness, 3)

pattern = re.compile(
    r'bufferData\[(\d+)\]\.(blankFromCell|'
    r'dbdGtyMeasurement\[(1|3)\]|'
    r'visionCorrectionData\[1\]\.(X|Y|Rotation|Quality)|'
    r'dbdTrspMeasurement\[(1|2|3|4)\]) := ([\d\.-]+);'
)

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

df_new.to_excel('output.xlsx', index=False)

df_new = df_new[
    (df_new['dbdTrspMeasurement[1]'] != 0) &
    (df_new['dbdTrspMeasurement[2]'] != 0) & 
    (df_new['dbdTrspMeasurement[3]'] != 0) & 
    (df_new['dbdTrspMeasurement[4]'] != 0)
]


fig, axes = plt.subplots(2, 1, figsize=(28, 10))
df_new.plot(x='bufferData', y=['dbdTrspMeasurement[1]', 'dbdTrspMeasurement[2]'], kind='line', ax=axes[0])
axes[0].axhline(y=upper_trshld, color='yellow', linestyle='--', label=f'Threshold ({upper_trshld})')
axes[0].axhline(y=lower_trshld, color='yellow', linestyle='--', label=f'Threshold ({lower_trshld})')
axes[0].set_title("DBD controller 1 measurements tracking")
axes[0].set_xlabel("")
axes[0].set_ylabel("")
axes[0].legend()
axes[0].grid(True)

df_new.plot(x='bufferData', y=['dbdTrspMeasurement[3]', 'dbdTrspMeasurement[4]'], kind='line', ax=axes[1])
axes[1].axhline(y=upper_trshld, color='yellow', linestyle='--', label=f'Threshold ({upper_trshld})')
axes[1].axhline(y=lower_trshld, color='yellow', linestyle='--', label=f'Threshold ({lower_trshld})')
axes[1].set_title("DBD controller 2 measurements tracking")
axes[1].set_xlabel("")
axes[1].set_ylabel("")
axes[1].legend()
axes[1].grid(True)

plt.tight_layout()
plt.show()