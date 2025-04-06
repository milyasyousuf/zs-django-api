from typing import TypedDict


class TypedResponse(TypedDict):
    success = bool
    status = int
    message = str
    response = dict
    error = dict
