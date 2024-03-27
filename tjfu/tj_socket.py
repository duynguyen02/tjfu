class SocketEvent:
    def __init__(
        self,
        namespace: str,
        event: str
    ):
        self._namespace = namespace
        self._event = event
    
    @property
    def event(self):
        return self._event

    @property
    def namespace(self):
        return self._namespace

    
class SocketHandle:
    def __init__(
        self,
        handle
    ):
        self._handle = handle
    
    @property
    def handle(self):
        return self._handle
        