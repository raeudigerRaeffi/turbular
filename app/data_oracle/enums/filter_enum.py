from .base_enum import BaseEnum

class Filter_Type(BaseEnum):
    NAME = "Table Name Filter"
    REGEX = "Regex Filter"
    EMBEDDING = "Embedding Based Filter"
