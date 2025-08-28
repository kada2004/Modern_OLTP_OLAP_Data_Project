import pandas as pd
import numpy as np

# Load the dataset
df = pd.read_csv('fifth_batch.csv', sep='\t')

# Convert InvoiceDate to datetime and format it
df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
df['InvoiceDate'] = df['InvoiceDate'].dt.strftime('%d/%m/%Y %H:%M')  

# Rename CustomerName to customerName
df.rename(columns={'CustomerName': 'customerName'}, inplace=True)

# Convert each row to JSON string (newline-delimited JSON)
df['json'] = df.to_json(orient='records', lines=True).splitlines()

# Extract the JSON strings
dfjson = df['json']

# Save to output.txt
np.savetxt('./output.txt', dfjson.values, fmt='%s')

print("Transformation complete. Output saved to output.txt")
