from re import sub

from django.core.exceptions import ValidationError

from recipes.constants import NON_VALID_USERNAME, USER_NAME_REGEX


def validate_username(value):
    if value == NON_VALID_USERNAME:
        raise ValidationError(
            message='Нельзя использовать me в качестве username',
            params={"value": value},
        )
    elif value in sub(USER_NAME_REGEX, "", value):
        raise ValidationError(
            message='Можно использовать латинские буквы и символы ., @, +, -.',
            params={"value": value},
        )
