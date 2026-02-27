import os
import sys

def calculate_sum(a, b):
    return a + b

class DataProcessor:
    def __init__(self, data):
        self.data = data
    
    def process(self):
        return [x * 2 for x in self.data]

if __name__ == "__main__":
    result = calculate_sum(5, 3)
    processor = DataProcessor([1, 2, 3])
    processed_data = processor.process()
    print(f"Result: {result}, Processed data: {processed_data}")