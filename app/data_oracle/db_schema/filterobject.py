from ..enums import Filter_Type


class EmbeddingContainer:

    def __init__(self, _embedding, natural_language_question, _cosine_dist_threshold):
        self.embedding = _embedding
        self.threshold = _cosine_dist_threshold
        self.nl_question = natural_language_question


class FilterObject:
    def __init__(self, value, _type: Filter_Type, nl_question=None, threshold=None):
        """
        Filter object representing an active filter
        @param value: can be either list[str], str, or EmbeddingContainer
        @param _type:
        """
        self.value: list[str] | EmbeddingContainer | str | None = None
        if _type == Filter_Type.EMBEDDING:
            self.value = EmbeddingContainer(value, nl_question, threshold)
        else:
            self.value = value
        self.classification = _type
