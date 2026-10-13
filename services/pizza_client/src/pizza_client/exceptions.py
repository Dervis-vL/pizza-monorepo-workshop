"""Exceptions raised by the pizza client."""


class PizzaClientError(Exception):
    """Base class for every client error."""


class TransientAPIError(PizzaClientError):
    """The API did not answer properly, but might on the next try."""


class MalformedPayloadError(PizzaClientError):
    """The API answered with something we do not understand."""
