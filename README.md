# Flask-ApiConnector

Simplify to register views to flask app API.

## Example
```python
from flask import Flask
from flask_api_connector import ApiConnector, Paths

app = Flask(__name__)

# view class must have one or more methods, e.g. get, post
class Example:
    def get(self):
        return 'get'

    def post(self):
        return 'post'

class Something:
    def get(self, request):
      # do something

      # return json serializable object, e.g. dict
      return { ... }

paths = Paths([
  ('/example', Example),
  ('/something', Something)
])

ApiConnector(paths=paths, base_url='/api').init_app(app)

app.run()
```

Then, test them on terminal
```sh
$ curl 127.0.0.1:5000/api/example
"get"
$ curl -X POST 127.0.0.1:5000/api/example
"post"
```

## Note
- use `request`, `session`, `g`

  This will automatically bind these proxy to method function,
  so that you do not need to do `from flask import request` in the view script.
  What only needs to do is set as argument in the method function as in the example.


## TODO
- handle nested paths