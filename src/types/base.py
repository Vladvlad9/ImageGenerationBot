from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

__all__ = ["DTO", "ImmutableDTO"]


def model_title_generator(dto: object) -> str:
    return dto.__name__.replace("DTO", "")


def make_dto_config(frozen: bool = False) -> ConfigDict:
    return ConfigDict(
        frozen=frozen,

        # Генерация и отображение
        model_title_generator=model_title_generator,
        use_attribute_docstrings=True,

        # Валидация и безопасность
        extra="forbid",
        validate_default=True,
        validate_return=True,
        allow_inf_nan=False,

        # Преобразование данных
        str_strip_whitespace=True,
        coerce_numbers_to_str=True,
        use_enum_values=True,
        populate_by_name=True,
        from_attributes=True,

        # Сериализация
        ser_json_timedelta="float",
        ser_json_bytes="base64",
        val_json_bytes="base64",

        # Именование
        alias_generator=to_camel,
        regex_engine="python-re",
    )


class DTO(BaseModel):
    model_config = make_dto_config(frozen=False)


class ImmutableDTO(DTO):
    model_config = make_dto_config(frozen=True)
