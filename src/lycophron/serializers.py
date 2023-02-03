from abc import ABC, abstractmethod
from .format import Format

class SerializerFactory():
    def create_serializer(self, format):
        return self._get_serializer(format)

    @abstractmethod
    def serialize(self, data, format):
        pass

    def _get_serializer(self, format):
        if format == Format.CSV:
            return CSVSerializer()
        else:
            raise NotImplementedError(
                f"Format {format} is not supported yet! Supported formats: {[e.value for e in Format]}"
            )


class Serializer(ABC):

    @abstractmethod
    def serialize(data):
        pass

class CSVSerializer(Serializer):
    extension_type = Format.CSV

    def __init__(self) -> None:
        super().__init__()

    def serialize(self, data: list) -> list:
        # [d for d in data] 

        # breakpoint()
        pass
