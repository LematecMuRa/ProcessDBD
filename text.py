import pandas as pd # type: ignore
import re


text_file = "./DATA_BLOCK dbd_testbuffer.txt"
data_dict = {}

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