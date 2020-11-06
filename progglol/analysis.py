import abc


class Analysis(metaclass=abc.ABCMeta):
    def __init__(self, player):
        self.player = player

    @abc.abstractmethod
    def run(self):
        pass
