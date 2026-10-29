class Rectangle:
    """A rectangle defined by integer length and width.

    Iterating over an instance yields the length first, then the width:

        >>> list(Rectangle(10, 5))
        [{'length': 10}, {'width': 5}]
    """

    def __init__(self, length: int, width: int):
        for name, value in (("length", length), ("width", width)):
            # bool is a subclass of int, so exclude it explicitly.
            if not isinstance(value, int) or isinstance(value, bool):
                raise TypeError(
                    f"{name} must be an int, got {type(value).__name__}"
                )
        self.length = length
        self.width = width

    def __iter__(self):
        yield {"length": self.length}
        yield {"width": self.width}

    def __repr__(self):
        return f"Rectangle(length={self.length}, width={self.width})"
