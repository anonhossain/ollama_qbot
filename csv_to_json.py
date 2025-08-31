import csv
import json

# Open the CSV file
file = 'file/data.csv'
with open(file, mode='r') as csv_file:
    csv_reader = csv.DictReader(csv_file)
    data = [row for row in csv_reader]

# Write to JSON file
with open('file/data.json', mode='w') as json_file:
    json.dump(data, json_file, indent=4)

print("CSV has been converted to JSON!")