from flask import Blueprint

class Route:
    def __init__(
        self,
        name: str,
        url_prefix: str
    ):
        self._name = name
        self._url_prefix = url_prefix

        self._blueprint = Blueprint(
            self._name,
            __name__
        )
        
        self._blueprint.route('/')(self._index)
    
    def _index(self):
        return f"Hello From: {self._name}"
    
    @property
    def name(self):
        return self._name
    
    @property
    def url_prefix(self):
        return self._url_prefix
    
    @property
    def blueprint(self):
        return self._blueprint
    
    def register_route(self, route):
        self._blueprint.register_blueprint(
            route.blueprint,
            url_prefix=route.url_prefix
        )
        