from functools import wraps
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_socketio import SocketIO, emit
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from datetime import timedelta

from .route import Route
from .tj_socket import SocketEvent, SocketHandle
from .tj_utils import deprecated

class MissingPropertyException(Exception):
    def __init__(self, err) -> None:
        super().__init__(f"Missing property: {err}")

class TJFU:
    # app properties
    _HOST_NAME: str = None
    _HOST_PORT: int = None
    _ROOT_PATH: str = '.'
    _FLASK_APP: Flask = None
    # resources
    _TEMPLATE_FOLDER: str = 'templates'
    _STATIC_FOLDER: str = 'static'
    
    # jwt
    _JWT_SECRET_KEY: str = None
    _JWT_ACCESS_TOKEN_EXPIRES: timedelta = timedelta(days=7)
    _JWT_REFRESH_TOKEN_EXPIRES: timedelta = timedelta(days=14)
    _JWT: JWTManager = None
    
    # socket
    _SOCKET_ROOT: str = '.'
    _SOCKET_IO: SocketIO = None
    _SOCKET_ASYNC_MODE = None
    
    # cors
    _IGNORE_CORS: bool = True
    _CORS: CORS = None
    
    # limiter
    _DEFAULT_LIMITS: list[str] = []
    _LIMITER_STORAGE_URI = "memory://"
    _LIMITER: Limiter = None
    
    # dev
    _DEBUG: bool = True
    _USE_RELOADER: bool = True
    _LOG_OUTPUT: bool = True
    _ALLOW_UNSAFE_WERKZEUG: bool = True
    
    # error handler
    _ERROR_HANDLER: dict[int, any] = {}
    
    # app config
    _APP_CONFIG = {}
    
    
    def _after_build_func(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if TJFU._FLASK_APP is None:
                raise Exception("TJFU has not been built yet, please call TJFU.build() before using this function.")
            return func(*args, **kwargs)
        return wrapper
    
    def _build_func(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if TJFU._FLASK_APP is not None:
                raise Exception("This function cannot be used after TJFU.build()")
            return func(*args, **kwargs)
        return wrapper
    
    @staticmethod
    @_after_build_func
    def limiter():
        return TJFU._LIMITER
    
    @staticmethod
    @_after_build_func
    def app():
        return TJFU._FLASK_APP
    
    @staticmethod
    @_build_func
    def app_config(key: str, value: str):
        TJFU._APP_CONFIG[key] = value
        return TJFU
    
    @staticmethod
    @_build_func
    @deprecated("Use method add_status_code_handler instead")
    def add_error_handler(code:int, handler):
        TJFU._ERROR_HANDLER[code] = handler
        return TJFU
    
    @staticmethod
    @_build_func
    def add_status_code_handler(code:int, handler):
        TJFU._ERROR_HANDLER[code] = handler
        return TJFU
    
    @staticmethod
    @_build_func
    def limiter_storage_uri(limiter_storage_uri: str):
        TJFU._LIMITER_STORAGE_URI = limiter_storage_uri
        return TJFU
    
    @staticmethod
    @_build_func
    def default_limits(default_limits: list[str]):
        TJFU._DEFAULT_LIMITS = default_limits
        return TJFU
    
    @staticmethod
    @_build_func
    def host_name(host_name: str):
        TJFU._HOST_NAME = host_name
        return TJFU

    @staticmethod
    @_build_func
    def host_port(host_port: int):
        TJFU._HOST_PORT = host_port
        return TJFU
    
    @staticmethod
    @_build_func
    def root_path(root_path: str):
        TJFU._ROOT_PATH = root_path
        return TJFU

    @staticmethod
    @_build_func
    def template_folder(template_folder: str):
        TJFU._TEMPLATE_FOLDER = template_folder
        return TJFU
    
    @staticmethod
    @_build_func
    def static_folder(static_folder: str):
        TJFU._STATIC_FOLDER = static_folder
        return TJFU

    @staticmethod
    @_build_func
    def jwt_secret_key(jwt_secret_key: str):
        TJFU._JWT_SECRET_KEY = jwt_secret_key
        return TJFU
    
    @staticmethod
    @_build_func
    def jwt_access_token_expires(jwt_access_token_expires: timedelta):
        TJFU._JWT_ACCESS_TOKEN_EXPIRES = jwt_access_token_expires
        return TJFU
    
    @staticmethod
    @_build_func
    def jwt_refresh_token_expires(jwt_refresh_token_expires: timedelta):
        TJFU._JWT_REFRESH_TOKEN_EXPIRES = jwt_refresh_token_expires
        return TJFU
    
    @staticmethod
    @_build_func
    def socket_root(socket_root: str):
        TJFU._SOCKET_ROOT = socket_root
        return TJFU
    
    @staticmethod
    @_build_func
    def ignore_cors(ignore_cors: bool):
        TJFU._IGNORE_CORS = ignore_cors
        return TJFU
    
    @staticmethod
    @_build_func
    def debug(debug: bool):
        TJFU._DEBUG = debug
        return TJFU
    
    @staticmethod
    @_build_func
    def use_reloader(use_reloader: bool):
        TJFU._USE_RELOADER = use_reloader
        return TJFU
    
    @staticmethod
    @_build_func
    def log_output(log_output: bool):
        TJFU._LOG_OUTPUT = log_output
        return TJFU
    
    @staticmethod
    @_build_func
    def allow_unsafe_werkzeug(allow_unsafe_werkzeug: bool):
        TJFU._ALLOW_UNSAFE_WERKZEUG = allow_unsafe_werkzeug
        return TJFU
    
    _IS_RUNNING = False
    
    @staticmethod
    def build():
        if TJFU._HOST_NAME is None:
            raise MissingPropertyException("host_name")
        if TJFU._HOST_PORT is None:
            raise MissingPropertyException("host_port")
        
        # init flask app
        TJFU._FLASK_APP = Flask(
            __name__,
            root_path=TJFU._ROOT_PATH,
            template_folder=TJFU._TEMPLATE_FOLDER,
            static_folder=TJFU._STATIC_FOLDER
        )
        
        # add app config
        for key, value in TJFU._APP_CONFIG.items():
            TJFU._FLASK_APP.config[key] = value
        
        # add status code handler
        for code in TJFU._ERROR_HANDLER.keys():
            TJFU._FLASK_APP.errorhandler(code)(TJFU._ERROR_HANDLER[code])
        
        # ignore CORS
        if TJFU._IGNORE_CORS:
            CORS(TJFU._FLASK_APP, origins='*')
            TJFU._CORS = CORS(TJFU._FLASK_APP, resource={
                r"/*":{
                    "origins":"*"
                }
            })
        
        # init jwt
        if TJFU._JWT_SECRET_KEY is not None:
            TJFU._FLASK_APP.config['JWT_SECRET_KEY'] = TJFU._JWT_SECRET_KEY
            TJFU._FLASK_APP.config['JWT_ACCESS_TOKEN_EXPIRES'] = TJFU._JWT_ACCESS_TOKEN_EXPIRES
            TJFU._FLASK_APP.config['JWT_REFRESH_TOKEN_EXPIRES'] = TJFU._JWT_REFRESH_TOKEN_EXPIRES
            TJFU._JWT = JWTManager(TJFU._FLASK_APP)
            
        # init limiter
        TJFU._LIMITER = Limiter(
            get_remote_address,
            app=TJFU._FLASK_APP,
            default_limits=TJFU._DEFAULT_LIMITS,
            storage_uri=TJFU._LIMITER_STORAGE_URI,
        )
        
        # init socketio
        TJFU._SOCKET_IO = SocketIO(
            TJFU._FLASK_APP,
            cors_allowed_origins="*",
            async_mode=TJFU._SOCKET_ASYNC_MODE
        )
    
    def _routes_map_register(index_route: Route, routes_map: dict):
        if isinstance(routes_map, dict):
            for route, sub_routes_map in routes_map.items():
                if isinstance(route, Route):
                    index_route.register_route(route)
                    TJFU._routes_map_register(route, sub_routes_map)
        elif isinstance(routes_map, (set, list, tuple)):
            for route in routes_map:
                if isinstance(route, Route):
                    index_route.register_route(route)
        
    @staticmethod
    def init_app(index_route: Route, routes_map: dict=None):
        
        if routes_map is not None:
            TJFU._routes_map_register(index_route, routes_map)
        
        TJFU._FLASK_APP.register_blueprint(
            index_route.blueprint,
            url_prefix=index_route.url_prefix
        )
        return TJFU._FLASK_APP
    
    @staticmethod
    def run():
        if TJFU._IS_RUNNING:
            return
        
        TJFU._IS_RUNNING = True
        
        TJFU._SOCKET_IO.run(
            app=TJFU._FLASK_APP,
            host=TJFU._HOST_NAME,
            port=TJFU._HOST_PORT,
            debug=TJFU._DEBUG,
            use_reloader=TJFU._USE_RELOADER,
            log_output=TJFU._LOG_OUTPUT,
            allow_unsafe_werkzeug=TJFU._ALLOW_UNSAFE_WERKZEUG
        )
        
    @staticmethod
    def after_request(response):
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', '*')
        response.headers.add('Access-Control-Allow-Methods', '*')
        return response
        
    @staticmethod
    def register_socket_event(socket_event: SocketEvent, socket_handle: SocketHandle):
        TJFU._SOCKET_IO.on_event(
            socket_event.event,
            socket_handle.handle,
            f'/{TJFU._SOCKET_ROOT}/{socket_event.namespace}'
        )
        
    @staticmethod
    def no_context_emit(
        socket_event: SocketEvent,
        message
    ):
        """
        Send information to the client outside the socket context.
        """
        TJFU._SOCKET_IO.emit(
            socket_event.event,
            message,
            namespace=f'/{TJFU._SOCKET_ROOT}/{socket_event.namespace}'
        )

    @staticmethod
    def emit(
        socket_event: SocketEvent,
        message,
        broadcast=False,
        callback=None,
        to=None
    ):
        """
        Send information to the client inside the socket handle context.
        
        """  
        emit(
            socket_event.event,
            message,
            namespace=f'/{TJFU._SOCKET_ROOT}/{socket_event.namespace}',            
            broadcast=broadcast,
            callback=callback,
            to=to
        )
    
    