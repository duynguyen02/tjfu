class SocketHandler:
    def __init__(
            self,
            event: str,
            namespace: str,
            handler
    ):
        self._event = event
        self._namespace = namespace
        self._handler = handler
    
    @property
    def event(self):
        return self._event
    
    @property
    def namespace(self):
        return self._namespace
    
    @property
    def handler(self):
        return self._handler
    
    