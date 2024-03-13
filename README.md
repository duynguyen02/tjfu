# TJFU
Python library helps optimize Flask development to be flexible and object-oriented.
#### Version: 2.0.0
### Extensions have been integrated
1. JWT
2. SocketIO
3. Limiter
### Installation
```
pip install tjfu
```

### Get started
Define a route:

```Python
from flask_jwt_extended import jwt_required
from tjfu import Route, TJFU


class RouteIndex(Route):
    def __init__(
        self,
        name: str
    ):
        super().__init__("index", "/")
        
        self._name = name
        
        self._blueprint.route('/')(self._index)
        self._blueprint.route('/jwt')(self._jwt)
        self._blueprint.route('/class_variable')(self._class_variable)
        self._blueprint.route('/limiter')(self._limiter)
    
    # Basic route function
    @staticmethod
    def _index():
        return "Hello World!"
    
    # JWT route function
    @staticmethod
    @jwt_required()
    def _jwt():
        return "Hello From JWT!"
    
    # Class variable route function
    def _class_variable(
        self
    ):
        return f"Hello {self._name}!"
    
    # Limiter route function
    @staticmethod
    @TJFU.limiter().limit('1/second')
    def _limiter():
        return "Hello from Limiter!"
```

Configuration and run Flask:
```Python
from os import path
from datetime import timedelta

from flask_socketio import emit
from tjfu import TJFU, Route
from tjfu.socket_handler import SocketHandler

def error_404(error):
    return "Not Found!!!", 404

def error_500(error):
    return "Error!!!", 500

if __name__ == '__main__':
    """
    The TJFU configuration must be placed
    at the beginning of the main function.
    """
    HERE = path.abspath(path.dirname(__file__))
    (
        TJFU
        .host_name("0.0.0.0") # required
        .host_port(3100) # required        
        .root_path(HERE) # optinal (default: '.')        
        .template_folder("templates") # optinal (default: 'templates')
        .static_folder("static") # optinal (default: 'static')
        .jwt_secret_key("your_jwt_secret_key")
            # optinal / enter value if you want to use JWT, 
            # Otherwise the jwt_required function will throw an error
        .jwt_access_token_expires(timedelta(days=7)) # optinal (default: 'timedelta(days=7)')
        .jwt_refresh_token_expires(timedelta(days=14)) # optinal (default: 'timedelta(days=14)')
        .socket_root("socket") # optinal (default: 'socket') 
        .ignore_cors(True) # optinal (default: 'True')
        .add_error_handler(404, error_404) # optional
        .add_error_handler(500, error_500) # optional
        .limiter_storage_uri("memory://") # optinal (default: 'memory://')
        .default_limits(["200 per day", "50 per hour"]) # optinal (default: '[]')
        .log_output(False) # optinal (default: 'True')
        .debug(False) # optinal (default: 'True')
        .use_reloader(False) # optinal (default: 'True')
        .allow_unsafe_werkzeug(False) # optinal (default: 'True')
        .build()
    )
    """
    Absolutely do not define or import any Route
    before calling the build() function because an error may occur.
    """
    
    
    from my_route_module import RouteIndex
    """
    Define route/subroute
    """
    class AnotherSubroute(Route):
        def __init__(self):
            super().__init__("another", "/another")
    
    # 0.0.0.0:3100/
    route_index = RouteIndex("John Doe")
    # 0.0.0.0:3100/another
    route_index.register_route(AnotherSubroute())
    
    """
    Define socket
    """
    class CustomSocketHandler(SocketHandler):
        def __init__(self):
            super().__init__("message", "message", self.handler)
            
        def handler():
            emit(
                super().event,
                "Hello From Default Socket Handler!",
                super().namespace
            )

    # 0.0.0.0:3100/socket/message
    socket_handler = CustomSocketHandler()
    TJFU.register_socket_handler(socket_handler)
    
    """
    This function can only be used in other classes
    after the TJFU.run() function has been called.
    """
    TJFU.emit(socket_handler, "Hello From Custom Socket Handler!")
    
    TJFU.run(route_index)
```