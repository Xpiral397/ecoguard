# Model.py
from abc import ABC, abstractmethod

class Model(ABC):
    @abstractmethod
    def train(self, data):
        pass

    @abstractmethod
    def predict(self, data):
        pass
