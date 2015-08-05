

class DataservClientException(Exception):
    pass


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


class AddressRequired(DataservClientException):

    def __init__(self):
        super(AddressRequired, self).__init__("Required address not given!")


class ConnectionError(DataservClientException):

    def __init__(self, url):
        msg = "Could not connect to server {0}!".format(url)
        super(ConnectionError, self).__init__(msg)
