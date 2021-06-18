class UmaUmaDriveException(Exception):
    pass


class FileNotFoundException(UmaUmaDriveException):
    pass


class InvalidKeyException(UmaUmaDriveException):
    pass


class InvalidTypeException(UmaUmaDriveException):
    pass


class InvalidValueException(UmaUmaDriveException):
    pass
