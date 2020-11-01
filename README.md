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
        # do something
        return 'post'

class Hello:
    def get(self, name):
        return f'Hello {name}!'

app_paths = Paths([
  ('/hello/<string:name>', App1),
], base_url='app')

paths = Paths([
  ('/example', Example),
  app_paths,  # can nest paths
])

ApiConnector(paths=paths, root_url='/api').init_app(app)

app.run()
```

Then, test them on terminal
```sh
$ curl 127.0.0.1:5000/api/example
"get"
$ curl -X POST 127.0.0.1:5000/api/example
"post"
$ curl 127.0.0.1:5000/api/app/hello/John
"Hello John!"
```

See other example usages in `./example/app.py`


## Note
- use `request`, `session`, `g`

  This will automatically bind these proxy to method function,
  so that you do not need to do `from flask import request` in the view script.
  What only needs to do is set as argument in the method function as in the example.


## TODO:
- handle trailing slash
- make marshal usable from `Paths`