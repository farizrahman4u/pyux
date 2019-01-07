import pyux
import json

with open('api.json', 'r') as f:
    previous_api = json.load(f)

current_api = pyux.sign(pyux)

diff = pyux.diff(current_api, previous_api)

if diff:
    raise Exception("API change detected ! \n " + '\n'.join([str(x) for x in diff]))
