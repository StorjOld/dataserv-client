from btctxstore.exceptions import *  # NOQA


class DataservClientException(Exception):
    pass


class ExistingConfig(DataservClientException):

    def __init__(self, path):
        msg = "Config already exists at '{0}'!".format(path)
        super(ExistingConfig, self).__init__(msg)


class InvalidConfig(DataservClientException):

    def __init__(self):
        super(InvalidConfig, self).__init__("Invalid Config!")


class ConfigNotFound(DataservClientException):

    def __init__(self, path):
        msg = "Config not found at '{0}'!".format(path)
        super(ConfigNotFound, self).__init__(msg)


class InvalidArgument(DataservClientException):

    def __init__(self):
        super(InvalidArgument, self).__init__("Invalid argument given!")


class AddressAlreadyRegistered(DataservClientException):

    def __init__(self, address, url):
        msg = "Address {0} already registered at {1}!".format(address, url)
        super(AddressAlreadyRegistered, self).__init__(msg)


class FarmerNotFound(DataservClientException):

    def __init__(self, url):
        msg = "Farmer not found at {0}!".format(url)
        super(FarmerNotFound, self).__init__(msg)


class FarmerError(DataservClientException):

    def __init__(self, url):
        msg = "Farmer error at {0}!".format(url)  # pragma: no cover
        super(FarmerError, self).__init__(msg)  # pragma: no cover


class InvalidAddress(DataservClientException):

    def __init__(self, address):
        msg = "Address {0} not valid!".format(address)
        super(InvalidAddress, self).__init__(msg)


class AuthWifRequired(DataservClientException):

    def __init__(self):
        msg = "Required authentication wif not given!"
        super(AuthWifRequired, self).__init__(msg)


class ConnectionError(DataservClientException):

    def __init__(self, url):
        msg = "Could not connect to server {0}!".format(url)
        super(ConnectionError, self).__init__(msg)
