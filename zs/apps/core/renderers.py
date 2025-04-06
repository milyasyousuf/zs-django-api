import json
from uuid import UUID

from rest_framework.exceptions import ValidationError
from rest_framework.renderers import BaseRenderer

from zs.apps.core.response import APPResponse, AppStatus, errors_messages


class CustomJSONRenderer(BaseRenderer):
    media_type = "application/json"
    format = "json"

    def render(self, data, accepted_media_type=None, renderer_context=None):
        if renderer_context.get("response").status_code in (200, 201, 204):
            response_data = APPResponse.get_response(
                success=True,
                message="Success",
                status=AppStatus.Success.value,
                response=data,
            )
        else:
            response_data = APPResponse.get_response(
                success=False,
                message="Something went wrong.",
                status=AppStatus.Error.value,
                response=data.pop("response", {}),
                error=errors_messages(ValidationError(data)),
            )
        response_data = self._fix_boolean_values(response_data)
        return json.dumps(response_data, cls=UUIDEncoder)

    def _fix_boolean_values(self, data):
        """
        Recursively convert string representations of booleans to native booleans.
        """
        if isinstance(data, dict):
            return {key: self._fix_boolean_values(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [self._fix_boolean_values(item) for item in data]
        elif isinstance(data, str):
            if data.lower() == "true":
                return True
            if data.lower() == "false":
                return False
            if data.lower() == "null" or data == "None":
                return None
        return data


class UUIDEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, UUID):
            return str(obj)
        return super().default(obj)
