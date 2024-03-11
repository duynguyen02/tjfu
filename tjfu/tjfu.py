from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_socketio import SocketIO

from datetime import timedelta



from .route import Route
from .socket_handler import SocketHandler

class TJFU:
    def __init__(
        self,
        host_name: str,
        host_port: int,
        root_path: str,
        index_route: Route,
        socket_root: str = 'socket',
        template_folder: str = 'templates',
        static_folder: str = 'static',
        ignore_cors: bool = True,
        jwt_secret_key: str = None,
        jwt_access_token_expires: timedelta = timedelta(days=7),
        jwt_refresh_token_expires: timedelta = timedelta(days=14),
        after_request = None,
        debug: bool = False,
        use_reloader: bool = False,
        log_output: bool = True,
        allow_unsafe_werkzeug: bool = True
    ):
        self._host_name = host_name
        self._host_port = host_port
        self._root_path = root_path
        self._template_folder = template_folder
        self._static_folder = static_folder
        self._socket_root = socket_root
        
        self._jwt_secret_key = jwt_secret_key
        self._jwt_refresh_token_expires = jwt_refresh_token_expires
        self._jwt_access_token_expires = jwt_access_token_expires
        
        self._debug = debug
        self._use_reloader = use_reloader
        self._log_output = log_output
        self._allow_unsafe_werkzeug = allow_unsafe_werkzeug

        self._app = Flask(
            __name__,
            root_path=self._root_path,
            template_folder=self._template_folder,
            static_folder=self._static_folder
        )
        
        if ignore_cors:
            CORS(self._app, origins='*')
            cors = CORS(self._app, resource={
                r"/*":{
                    "origins":"*"
                }
            })

        
        # JWT configuration
        if jwt_secret_key is not None:
            self._app.config['JWT_SECRET_KEY'] = self._jwt_secret_key
            self._app.config['JWT_ACCESS_TOKEN_EXPIRES'] = self._jwt_access_token_expires
            self._app.config['JWT_REFRESH_TOKEN_EXPIRES'] = self._jwt_refresh_token_expires
            self._jwt = JWTManager(self._app)
        
        # after request configuration
        # self._app.after_request(
        #     (
        #         after_request
        #         if after_request is not None
        #         else self.after_request
        #     ) 
        # )
        
        self._app.register_blueprint(
            index_route.blueprint,
            url_prefix=index_route.url_prefix
        )
        
        self._socketio = SocketIO(self._app, cors_allowed_origins="*", async_mode=None)
    
    @property
    def app(self):
        return self._app
    
    @staticmethod
    def after_request(response):
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', '*')
        response.headers.add('Access-Control-Allow-Methods', '*')
        return response
    
    def register_socket_handler(self, socket_handler: SocketHandler):
        self._socketio.on_event(socket_handler.event, socket_handler.handler, f'{self._socket_root}/{socket_handler.namespace}')

    def emit(self, socket_handler: SocketHandler, message):
        self._socketio.emit(socket_handler.event, message, namespace=f'{self._socket_root}/{socket_handler.namespace}')
    
    def run(
        self
    ):
        self._socketio.run(
            app=self._app,
            host=self._host_name,
            port=self._host_port,
            debug=self._debug,
            use_reloader=self._use_reloader,
            log_output=self._log_output,
            allow_unsafe_werkzeug=self._allow_unsafe_werkzeug
        )