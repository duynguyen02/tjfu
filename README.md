# TJFU
Python library helps optimize Flask development

### Installation
```
pip install tjfu
```

### Get started
Simple example:

```Python
from datetime import timedelta
from flask_cors import CORS
from flask_jwt_extended import get_jwt_identity, jwt_required
from tjfu import TJFU, Route

class RouteIndex(Route):
    def __init__(self):
        super().__init__("index", "/")
        self._my_class_value = "My Class Value"        
        self._blueprint.route('/')(self._index)
        self._blueprint.route('/subroute')(self._subroute)
        self._blueprint.route('/jwt_subroute')(self._jwt_subroute)
        
    @staticmethod
    def _index():
        return "Hello World!"
    
    def _subroute(
        self
    ):
        return {
            "name": "subroute",
            "value": self._my_class_value
        }
    
    @jwt_required()
    def _jwt_subroute(
        self
    ):
        identity = get_jwt_identity()
        return identity
    
class MySubRoute(Route):
    def __init__(self, name: str):
        super().__init__("mysubroute", "/mysubroute")
        self._name = name
        self._blueprint.route('/')(self._index)
    
    def _index(self):
        return f'Hello {self._name}'

def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', '*')
    response.headers.add('Access-Control-Allow-Methods', '*')
    return response

my_subroute = MySubRoute("Olivia Parker")
route = RouteIndex()
route.register_route(my_subroute)

tjfu = TJFU(
    host_name="0.0.0.0",
    host_port=3100,
    root_path=HERE,
    template_folder='templates',
    static_folder='static',
    index_route=route,
    socket_root="socket",
    ignore_cors=True,
    jwt_secret_key="your_jwt_secret_key",
    jwt_access_token_expires=timedelta(days=7),
    jwt_refresh_token_expires=timedelta(days=8),
    after_request=after_request,
    debug=True,
    use_reloader=True,
    log_output=True,
    allow_unsafe_werkzeug=True
)
tjfu.run()
```

Socket example:
```Python
class CustomSocketHandler(SocketHandler):
    def __init__(self):
        super().__init__("message", "message", self.handler)
        
    def handler():
        emit(
            super().event,
            "Hello From Default Socket Handler!",
            super().namespace
        )

socket_handler = CustomSocketHandler()

tjfu.register_socket_handler(
    socket_handler
)

tjfu.emit(
    socket_handler,
    "Hello From Custom Socket Handler!"
)
```