class Timer:
    
    def __init__(self):
        self.ticks = 0
        self.funs = {}
        
    def bind(self, fun, delay):
        self.funs[delay] = fun
        
    def unbind(self, fun):
        self.funs = {key: value for key, value in self.funs if fun != value}

    def reset(self):
        self.funs = {}
        
    def tick(self):
        self.ticks += 1
        try:
            for delay, fun in self.funs.items():
                if abs(self.ticks % delay) == 0:
                    fun()
        except:
            pass
