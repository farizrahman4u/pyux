import os
import pyux
import json

sign = pyux.sign(pyux)

with open('api.json', 'w') as f:
    json.dump(sign, f)
