from enums import Part_of_Speech


class Concept:
    """
    Class Concept is cretaed to represent concept entity in ConceptNet or the set of entities in language
    """

    def __init__(
        self, lang: str, type: Part_of_Speech = None, label: str = None
    ) -> None:
        if type and label is None:
            raise ValueError("`string` cannot be None when `type` has a value.")
        self.type = type
        self.lang = lang
        self.label = label

    def get_uri(self):
        uri = f"/c/{self.lang}"
        if self.label:
            uri += f"/{self.label}"
            if self.type:
                uri += f"{self.type.value}"
        return uri
