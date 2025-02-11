"""Custom exceptions for Neuron Lab API."""


class TratumAPIException(Exception):
    def __repr__(self):
        template = "{class_name}: {message}"
        return template.format(
            class_name=self.__class__.__name__,
            message=self.message)

    def __str__(self):
        return self.__repr__()

    def __init__(self, message: str, payload: dict = {}):
        self.message = message
        self.payload = payload

    def to_dict(self):
        rv = {
            "payload": self.payload,
            "type": self.__class__.__name__,
            "message": self.message}
        return rv


class TratumAPIInvalidDocumentException(TratumAPIException):
    pass


class TratumAPIProblemAPIException(TratumAPIException):
    pass


class TratumAPIInvalidS3UrlException(TratumAPIException):
    pass