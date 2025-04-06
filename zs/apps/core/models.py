import ast
from django.db import models


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class AppSetting(TimeStampedModel):
    key = models.CharField(max_length=100, unique=True)
    value = models.CharField(max_length=1000)

    class Meta:
        verbose_name = "App Settings"

    def __str__(self):
        return f"{self.key}"

    @classmethod
    def get_value(cls, key: str) -> str:
        config = cls.objects.filter(key=key)
        if config.exists():
            return config.first().value
        return ""

    @classmethod
    def get_float_value(cls, key: str) -> float:
        config = cls.objects.filter(key=key)
        if config.exists():
            return float(config.first().value)
        return 0.0

    @classmethod
    def get_email_list(cls, key: str) -> list:
        data = cls.get_value(key=key)
        if data:
            return ast.literal_eval(data)
        return []

    @classmethod
    def get_value_as_list(cls, key: str) -> list:
        data = cls.get_value(key=key)
        if data:
            return ast.literal_eval(data)
        return []

    @classmethod
    def get_bool_value(cls, key: str) -> bool:
        config = cls.objects.filter(key=key)
        if config.exists():
            return ast.literal_eval(config.first().value)
        return False

    @classmethod
    def get_url_value(cls, key: str) -> str:
        config = cls.objects.filter(key=key)
        if config.exists():
            return config.first().value
        return ""