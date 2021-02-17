class SimulatedDataStore():
    def __init__(self):
        self._data = []
    
    def get_region(self, index):
        return self._data[index]
        
    def append(self, datum):
        self._data.append(datum)
        
    def remove(self, index):
        self._data.pop(index)