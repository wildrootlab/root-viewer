from enum import Enum, EnumMeta
from napari.utils.translations import trans

class StringEnumMeta(EnumMeta):
    def __getitem__(self, item):
        """set the item name case to uppercase for name lookup"""
        if isinstance(item, str):
            item = item.upper()

        return super().__getitem__(item)

    def __call__(
        cls,
        value,
        names=None,
        *,
        module=None,
        qualname=None,
        type=None,
        start=1,
    ):
        """set the item value case to lowercase for value lookup"""
        # simple value lookup
        if names is None:
            if isinstance(value, str):
                return super().__call__(value.lower())
            elif isinstance(value, cls):
                return value
            else:
                raise ValueError(
                    trans._(
                        '{class_name} may only be called with a `str` or an instance of {class_name}. Got {dtype}',
                        deferred=True,
                        class_name=cls,
                    )
                )

        # otherwise create new Enum class
        return cls._create_(
            value,
            names,
            module=module,
            qualname=qualname,
            type=type,
            start=start,
        )

    def keys(self):
        return list(map(str, self))

class StringEnum(Enum, metaclass=StringEnumMeta):
    def _generate_next_value_(name, start, count, last_values):
        """autonaming function assigns each value its own name as a value"""
        return name.lower()

    def __str__(self):
        """String representation: The string method returns the lowercase
        string of the Enum name
        """
        return self.value

    def __eq__(self, other):
        if type(self) is type(other):
            return self is other
        elif isinstance(other, str):
            return str(self) == other
        return NotImplemented

    def __hash__(self):
        return hash(str(self))