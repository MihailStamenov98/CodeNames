from enums import Part_of_Speech


class Concept:
    """
    Class Concept is cretaed to represent concept entity in ConceptNet or the set of entities in language
    """

    def __init__(
        self, lang: str, type: Part_of_Speech = None, string: str = None
    ) -> None:
        if type and string is None:
            raise ValueError("`string` cannot be None when `type` has a value.")
        self.type = type
        self.lang = lang
        self.string = string

    def get_uri(self):
        uri = f"/c/{self.lang}"
        if self.string:
            uri += f"/{self.string}"
            if self.type:
                uri += f"/{self.type.value}"
        return uri
