# TJFU
Python library helps optimize Flask development to be flexible and object-oriented.
#### Version: 3.1.0
### Extensions have been integrated
1. [JWT](https://flask-jwt-extended.readthedocs.io/en/stable/)
2. [SocketIO](https://flask-socketio.readthedocs.io/en/latest/)
3. [Limiter](https://flask-limiter.readthedocs.io/en/stable/)
### Installation
```
pip install tjfu
```

### Get started
Basic example:
```Python
from os import path
from tjfu import TJFU
from datetime import timedelta

HERE = path.abspath(path.dirname(__file__))

def error_404(error):
    return "Not Found!!!", 404

def error_500(error):
    return "Error!!!", 500

"""
    The TJFU configuration must be placed
    at the beginning of the main function.
    Absolutely do not define or import any Route
    before calling the build() function because an error may occur.
"""
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

from tjfu import Route

app = TJFU.init_app(Route("index", "/"))

IS_PRODUCTION = False

if __name__ == "__main__":
    if IS_PRODUCTION:
        app.run()
    else:
        TJFU.run()
```

Define a Custom Route:
```Python
# OTHER CODE...
from tjfu import Route, SimpleRenderTemplateRoute

class MyCustomRoute(Route):
    def __init__(
        self,
        your_name: str
    ):
        super().__init__("mycustomroute", "/mycustomroute")
        self._your_name = your_name
    
        self._blueprint.route('/')(self._index) # /mycustomroute
        self._blueprint.route('/jwt')(self._jwt) # /mycustomroute/jwt
        self._blueprint.route('/class_variable')(self._class_variable) # /mycustomroute/class_variable
        self._blueprint.route('/limiter')(self._limiter) # /mycustomroute/limiter
    
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
        return f"Hello {self._your_name}!"
    
    # Limiter route function
    @staticmethod
    @TJFU.limiter().limit('1/second')
    def _limiter():
        return "Hello from Limiter!"
    

index_route = Route("index", "/")
my_custom_route = MyCustomRoute("John Doe")
another_my_custom_route = MyCustomRoute("Lisa")

# /mycustomroute
index_route.register_route(my_custom_route)

"""
    You can easily define a route to
    render an HTML file
    using the SimpleRenderTemplateRoute class
"""
# /my_html_file
index_route.register_route(
    SimpleRenderTemplateRoute(
        "my_html_file",
        "/my_html_file",
        "my_html_file.html"
    )
)

# /mycustomroute/mycustomroute
my_custom_route.register_route(another_my_custom_route)

# You must register routes and sockets before calling the init_app function
app = TJFU.init_app(index_route)

# OTHER CODE...
```
Register Routes using Dictionary (>=3.1.0):
```Python
# OTHER CODE...

app = TJFU.init_app(
    Route("index", "/"), 
    {
        Route("api", "/api"):{
            
            Route("v1", "/v1"):{
                
                Route("user", "/user"):{
            
                }    
                
            }
            
        },
        Route("tool", "/tool"):{
            SimpleRenderTemplateRoute(
                "my_tool",
                "/my_tool",
                "my_tool.html"
            )
        },
        SimpleRenderTemplateRoute(
            "hello_world",
            "/hello_world",
            "hello_world.html"
        ): None
    }
)

# OTHER CODE...
```

Define a Socket Handle:
```Python
# OTHER CODE...

from tjfu import SocketEvent, SocketHandle
from flask import request
class MySocketHandle(SocketHandle):
    def __init__(self):
        super().__init__(self._my_handle)
        
    def _my_handle(self, msg):
        print(f"Client id: {request.sid}")
        print(f"Msg from client: {msg}")
        TJFU.emit(
            SocketEvent("chat", "send"),
            "Hello client from socket handle!!!"
        )
        
TJFU.register_socket_event(
    SocketEvent("chat", "send"),
    MySocketHandle()
) 

app = TJFU.init_app(index_route)

# OTHER CODE...
```
You can send data to the client via Socket in places outside the Socket Handle context (such as Route) through the TJFU.no_context_emit function

```Python
class SendMsgRoute(Route):
    def __init__(
        self
    ):
        super().__init__("send_msg", "/send_msg")
        self._blueprint.route('/')(self._index)
        
    @staticmethod
    def _index():
        TJFU.no_context_emit(
            SocketEvent("chat", "send"),
            "Hello client from route!!!"
        )
        return "Hello World!"
```
Simple HTML code to receive and send data from Socket
```HTML
<!DOCTYPE html>
<html>
<head>
    <title>Socket.IO Example</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.1.3/socket.io.js"></script>
    <script type="text/javascript">
        var socket = io('http://0.0.0.0:3100/socket/chat');
        socket.on('connect', function () {
            console.log('Connected to the server');
        });
        socket.on('send', function (data) {
            console.log('Message received: ' + data);
        });
        socket.on('disconnect', function () {
            console.log('Disconnected from server');
        });
        function sendMessage() {
            var message = document.getElementById('message').value;
            socket.emit('send', message);
        }
    </script>
</head>

<body>
    <h1>Socket.IO Example</h1>
    <input type="text" id="message" placeholder="Enter message">
    <button onclick="sendMessage()">Send</button>
</body>

</html>
```