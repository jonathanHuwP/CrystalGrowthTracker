import inspect

class SimulatedDataStore():
    def __init__(self):
        self._data = []
    
    def get_region(self, index):
        current_frame = inspect.currentframe()
        calling_frames = inspect.getouterframes(current_frame)
        print(f"getting region {index} out of {len(self._data)}")
        for item in calling_frames:
            print(f"\t{item.function}")

        return self._data[index]
        
    def append(self, datum):
        self._data.append(datum)
        return len(self._data)
        
    def remove(self, index):
        self._data.pop(index)
        
    def replace_region(self, rectangle, index):
        self._data[index] = rectangle
        
    @property
    def length(self):
        return len(self._data)