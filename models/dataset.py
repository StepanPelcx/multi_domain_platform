class Dataset:
    """Represents a data science dataset in the platform."""

    #creating variables of the class
    def __init__(self, dataset_id: int, name: str, size_bytes: int, rows: int, source: str):
        self.__id = dataset_id
        self.__name = name
        self.__size_bytes = size_bytes
        self.__rows = rows
        self.__source = source

    def calculate_size_mb(self) -> float:
        """Returns calculated size in mega bytes."""
        return self.__size_bytes / (1024 * 1024)
    
    def get_source(self) -> str:
        """Returns a source of the dataset."""
        return self.__source
    
    #self description
    def __str__(self) -> str:
        size_mb = self.calculate_size_mb()
        return f"Dataset {self.__id}: {self.__name} ({size_mb:.2f} MB, {self.__rows} rows)"
    