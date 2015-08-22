import datetime
import email.utils
import json
import http.client
import socket
import time
import urllib
import urllib.error
import urllib.request

import btctxstore

from dataserv_client import exceptions


class Messaging(object):

    def __init__(self, server_url, wif, connection_retry_limit,
                 connection_retry_delay):
        self._server_url = server_url
        self._server_address = None
        self._connection_retry_limit = connection_retry_limit
        self._connection_retry_delay = connection_retry_delay

        # FIXME wif and client_address do not belong here
        # FIXME pass testnet and dryrun options
        self._blockchain = btctxstore.BtcTxStore()
        # set wif and address
        if wif and not self._blockchain.validate_key(wif):
            raise exceptions.InvalidWif(wif)
        self._wif = wif
        if wif:
            self._client_address = self._blockchain.get_address(wif)
        else:
            self._client_address = None
        if not self._client_address:
            raise exceptions.AddressRequired()

    def _url_query(self, api_path, retries=0, authenticate=True):
        try:
            req = urllib.request.Request(self._server_url + api_path)
            if self._wif and authenticate:
                headers = self._create_authentication_headers()
                req.add_header("Date", headers["Date"])
                req.add_header("Authorization", headers["Authorization"])
            response = urllib.request.urlopen(req)
            if response.code == 200:
                return response.read()
        except urllib.error.HTTPError as e:
            if e.code == 409:
                raise exceptions.AddressAlreadyRegistered(self._client_address,
                                                          self._server_url)
            elif e.code == 404:
                raise exceptions.FarmerNotFound(self._server_url)
            elif e.code == 400:
                raise exceptions.InvalidAddress(self._client_address)
            elif e.code == 500:  # pragma: no cover
                raise exceptions.FarmerError(self._server_url)
            else:
                raise e  # pragma: no cover
        except http.client.HTTPException:
            self._handle_connection_error(api_path, retries, authenticate)
        except urllib.error.URLError:
            self._handle_connection_error(api_path, retries, authenticate)
        except socket.error:
            self._handle_connection_error(api_path, retries, authenticate)

    def _get_node_address(self):
        if not self._server_address:
            # TODO validate address
            self._server_address = self.address()
        return self._server_address

    def _create_authentication_headers(self):
        header_date = email.utils.formatdate(
            timeval=time.mktime(datetime.datetime.now().timetuple()),
            localtime=True, usegmt=True)
        message = self._get_node_address() + " " + header_date
        header_authorization = self._blockchain.sign_unicode(
            self._wif, message)
        return {"Date": header_date,
                "Authorization": header_authorization}

    def _handle_connection_error(self, api_path, retries, authenticate):
        if retries >= self._connection_retry_limit:
            raise exceptions.ConnectionError(self._server_url)
        time.sleep(self._connection_retry_delay)
        return self._url_query(api_path, retries + 1, authenticate)

    def server_url(self):
        return self._server_url

    def client_address(self):
        return self._client_address

    def address(self):
        data = self._url_query("/api/address", authenticate=False)
        return json.loads(data.decode("utf-8"))["address"]

    def register(self):
        """Attempt to register this client address."""
        return self._url_query("/api/register/%s" % self._client_address)

    def ping(self):
        """Send a heartbeat message for this client address."""
        return self._url_query("/api/ping/%s" % self._client_address)

    def height(self, height):
        """Set the height claim for this client address."""
        return self._url_query('/api/height/%s/%s' % (self._client_address,
                                                      height))
