class Error(Exception):
    """Base class for all exceptions in this module."""

    pass


class EncoderError(Error):
    """Base class for all encoding and decoding related errors."""

    def __init__(self, message, encoder_name):
        self.encoder_name = encoder_name

        Error.__init__(self, message)


class EncodingError(EncoderError):
    """Raised when encoding a Python object into a byte string has failed
    due to some problem with the input data."""

    def __init__(self, encoder_name, original):
        self.original = original

        msg = "Object encoding error: {}".format(original)
        EncoderError.__init__(self, msg, encoder_name)


class DecodingError(EncoderError):
    """Raised when decoding a byte string to a Python object has failed due to
    some problem with the input data."""

    def __init__(self, encoder_name, original):
        self.original = original

        msg = "Object decoding error: {}".format(original)
        EncoderError.__init__(self, msg, encoder_name)
