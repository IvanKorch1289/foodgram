import re

from django.core.exceptions import ValidationError

from recipes.constants import NON_VALID_USERNAME, USER_NAME_REGEX


def username_validator(value):
    unmatched = re.sub(USER_NAME_REGEX, "", value)
    if value == NON_VALID_USERNAME:
        raise ValidationError(
            f'Имя пользователя "{NON_VALID_USERNAME}" использовать нельзя!'
        )
    elif value in unmatched:
        raise ValidationError(f"Имя пользователя не должно содержать {unmatched}")
    return value
