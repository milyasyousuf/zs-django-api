from enum import Enum

from .typings import TypedResponse


class APPResponse:
    @staticmethod
    def get_response(
        success: str = False,
        message: str = "",
        status: int = 101,
        error_code: int = 400,
        response: dict = {},
        error: dict = {},
    ) -> TypedResponse:
        return {
            "success": success,
            "status": status,
            "message": message,
            "response": response,
            "error": error,
        }


class AppStatus(Enum):
    Success = "success"
    Error = "error"
    Warning = "warning"


def errors_messages(errors):
    errors = errors.get_full_details()
    error_dict = {}

    def extract_error_detail(error):
        if isinstance(error, list) and error:
            error = error[0]
        if isinstance(error, dict) and "message" in error and "code" in error:
            return {
                "error_string": error["message"].replace('"', ""),
                "error_code": error["code"],
            }
        return {
            "error_string": "Unknown error format.",
            "error_code": "unknown_error",
        }

    for field, error_list in errors.items():
        if isinstance(error_list, list) and error_list:
            error_dict[field] = extract_error_detail(error_list)
        elif isinstance(error_list, dict):
            if "message" in error_list and "code" in error_list:
                error_dict[field] = {
                    "error_string": error_list["message"].replace('"', ""),
                    "error_code": error_list["code"],
                }
            else:
                nested_errors = {}
                for subfield, sub_error in error_list.items():
                    nested_errors[subfield] = extract_error_detail(sub_error)
                error_dict[field] = nested_errors
        else:
            error_dict[field] = {
                "error_string": str(error_list).replace('"', ""),
                "error_code": "unexpected_error_format",
            }

    return error_dict
