# Train.py
from abc import ABC, abstractmethod

class Train(ABC):
    def __init__(self, model):
        self.model = model

    @abstractmethod
    def train_data(self, dataset):
        pass

    @abstractmethod
    def save_model(self, filepath):
        pass
