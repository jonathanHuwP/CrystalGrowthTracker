class SimulatedDataStore():
    def __init__(self):
        self._data = []
    
    def get_region(self, index):
        return self._data[index]
        
    def append(self, datum):
        self._data.append(datum)
        return len(self._data)
        
    def remove(self, index):
        self._data.pop(index)
        
    def replace_region(self, rectangle, index):
        self._data[index] = rectangle