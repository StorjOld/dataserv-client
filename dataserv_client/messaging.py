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

        # FIXME pass testnet and dryrun options
        self._btctxstore = btctxstore.BtcTxStore()
        self._wif = wif

    def _get_wif(self):
        if not self._wif:
            raise exceptions.AuthWifRequired()
        if not self._btctxstore.validate_key(self._wif):
            raise exceptions.InvalidWif(self._wif)
        return self._wif

    def auth_address(self):
        return self._btctxstore.get_address(self._get_wif())

    def _url_query(self, api_path, retries=0, authenticate=True):
        try:
            req = urllib.request.Request(self._server_url + api_path)
            if self._get_wif() and authenticate:
                headers = self._create_authentication_headers()
                req.add_header("Date", headers["Date"])
                req.add_header("Authorization", headers["Authorization"])
            response = urllib.request.urlopen(req)
            if response.code == 200:
                return response.read()
        except urllib.error.HTTPError as e:
            if e.code == 409:
                raise exceptions.AddressAlreadyRegistered(self.auth_address(),
                                                          self._server_url)
            elif e.code == 404:
                raise exceptions.FarmerNotFound(self._server_url)
            elif e.code == 400:
                raise exceptions.InvalidAddress(self.auth_address())
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
        msg = self._get_node_address() + " " + header_date
        header_authorization = self._btctxstore.sign_unicode(self._get_wif(), msg)
        return {"Date": header_date, "Authorization": header_authorization}

    def _handle_connection_error(self, api_path, retries, authenticate):
        if retries >= self._connection_retry_limit:
            raise exceptions.ConnectionError(self._server_url)
        time.sleep(self._connection_retry_delay)
        return self._url_query(api_path, retries + 1, authenticate)

    def server_url(self):
        return self._server_url

    def address(self):
        data = self._url_query("/api/address", authenticate=False)
        return json.loads(data.decode("utf-8"))["address"]

    def register(self, payout_addr):
        """Attempt to register this client address."""
        if payout_addr and not self._btctxstore.validate_address(payout_addr):
            raise exceptions.InvalidAddress(payout_addr)
        if payout_addr:
            return self._url_query("/api/register/{0}/{1}".format(
                self.auth_address(), payout_addr
            ))
        data = self._url_query("/api/register/{0}".format(self.auth_address()))
        data = json.loads(data.decode("utf-8"))
        payout_addr = payout_addr if payout_addr else self.auth_address()
        return (data["btc_addr"] == self.auth_address() and 
                data["payout_addr"] == payout_addr)

    def ping(self):
        """Send a heartbeat message for this client address."""
        return self._url_query("/api/ping/%s" % self.auth_address())

    def height(self, height):
        """Set the height claim for this client address."""
        return self._url_query('/api/height/%s/%s' % (self.auth_address(),
                                                      height))
