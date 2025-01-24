import json
import pandas as pd

json_file = 'output_data_misc.json' 
with open(json_file, 'r') as file:
    data = json.load(file)

# Extract the 'externallink' from each dictionary
links = [item['externallink'] for item in data if 'externallink' in item and 'usda' in item['externallink']]

# Create a DataFrame with the extracted links
df = pd.DataFrame(links, columns=['externallink'])

# Save to CSV
output_csv = 'extracted_links.csv'
df.to_csv(output_csv, index=False)

print(f"CSV saved as {output_csv}")
