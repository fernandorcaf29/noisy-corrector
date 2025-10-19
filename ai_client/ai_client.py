from abc import ABC, abstractmethod


class AIClient(ABC):
    @abstractmethod
    def ask_correction(self, transcription, model, custom_prompt=None):
        pass
