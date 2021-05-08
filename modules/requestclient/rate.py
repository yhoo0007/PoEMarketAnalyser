

class Rate:
    def __init__(self, num_requests, interval, timeout):
        self.num_requests = num_requests
        self.interval = interval
        self.timeout = timeout
    
    def __str__(self):
        return f'{self.num_requests}:{self.interval}:{self.timeout}'
