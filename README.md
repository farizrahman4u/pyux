# pyux
Utility to check API integrity in Python libraries


Use pyux if:
* you are obsessed about API integrity,
* you would like to detect API changes as part of your CI,
* you want to track all API changes in a single place.



## Installation

```shell
pip install git+https://www.github.com/farizrahman4u/pyux.git
```

## Usage

For your Python project `myproject`:

* Create `update_api.py` in the root of your project (next to `setup.py`):

```python
# update_api.py

import myproject
import pyux
import json

sign0 = pyux.sign(myproject)
sign1 = pyux.sign(myproject.module1)
sign2 = pyux.sign(myproject.module2)

current_api = [sign0, sign1, sign2]

with open('api.json', 'w') as f:
    json.dump(current_api, f)

```

* Create `test_api.py` in the root of your project (next to `setup.py`):

```python
import myproject
import pyux
import json

sign0 = pyux.sign(myproject)
sign1 = pyux.sign(myproject.module1)
sign2 = pyux.sign(myproject.module2)

current_api = [sign0, sign1, sign2]

with open('api.json', 'r') as f:
    previous_api = json.load(f)
 
diff = pyux.diff(current_api, previous_api)

if diff:
    raise Exception("API change detected ! \n " + '\n'.join([str(x) for x in diff]))

```
* Install your package (`python setup.py install`).
* Run `update_api.py` once to create an "API hash" which will be saved to `api.json ('python update_api.py').
* Include `test_api.py` in your CI build.

Any API changes beyond this point will break your build!

If you really want to make an API change:
* Install your package after making the changes (`python setup.py install`).
* Run `update_api.py`



