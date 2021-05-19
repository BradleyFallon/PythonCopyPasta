import json

# dump
with open('data.txt', 'w') as outfile:
    json.dump(data, outfile)

# load
with open('data.txt') as json_file:
    data = json.load(json_file)