import json
import http.client
import socket
import time
from datetime import datetime
from future.moves.urllib.parse import urlparse, urlencode  # NOQA
from future.moves.urllib.request import urlopen, Request
from future.moves.urllib.error import HTTPError, URLError
import btctxstore
import storjcore
from dataserv_client import exceptions
from dataserv_client import logmessages
from dataserv_client import common


logger = common.logging.getLogger(__name__)


class Messaging(object):

    def __init__(self, server_url, wif, connection_retry_limit,
                 connection_retry_delay):
        self._server_url = server_url
        self._server_address = None
        self.retry_limit = connection_retry_limit
        self.retry_delay = connection_retry_delay

        # TODO pass testnet and dryrun options
        self.btctxstore = btctxstore.BtcTxStore()
        self.wif = wif

    def auth_address(self):
        return self.btctxstore.get_address(self.wif)

    def get_nodeid(self):
        return common.address2nodeid(self.auth_address())

    def _url_query(self, api_path, authenticate=True):  # NOQA
        i = 0
        while i <= self.retry_limit:
            i += 1
            try:
                query_url = self._server_url + api_path
                req = Request(query_url)
                starttime = datetime.utcnow()
                if self.wif and authenticate:
                    headers = storjcore.auth.create_headers(
                        self.btctxstore, self._get_server_address(), self.wif
                    )
                    req.add_header("Date", headers["Date"])
                    req.add_header("Authorization", headers["Authorization"])
                logger.info("Query: {0} generated in {1}".format(
                                    query_url, datetime.utcnow()-starttime))
                response = urlopen(req, timeout=30)
                if 200 <= response.code <= 299:
                    return response.read()
            except HTTPError as e:
                if e.code == 409:
                    raise exceptions.AddressAlreadyRegistered(
                        self.auth_address(), self._server_url
                    )
                elif e.code == 404:
                    raise exceptions.ServerNotFound(self._server_url + api_path)
                elif e.code == 400:
                    raise exceptions.InvalidAddress(self.auth_address())
                elif e.code == 401:  # auth error (likely clock off)
                    # log "HTTP Error 401: UNAUTHORIZED"
                    logger.warning(logmessages.InvalidAuthenticationHeaders())
                elif e.code == 500:  # pragma: no cover
                    raise exceptions.ServerError(self._server_url)
                else:
                    raise e  # pragma: no cover
            except http.client.HTTPException as e:
                logger.warning(repr(e))
            except URLError as e:
                logger.warning(repr(e))
            except socket.error as e:
                logger.warning(repr(e))

            # retry
            delay = self.retry_delay
            logger.info("Query retry in {0} seconds.".format(delay))
            time.sleep(delay)

        # retry limit
        logger.error("Failed to connect to {0}".format(self._server_url))
        raise exceptions.ConnectionError(self._server_url)

    def _get_server_address(self):
        if not self._server_address:
            data = self._url_query("/api/address", authenticate=False)
            self._server_address = json.loads(data.decode("utf-8"))["address"]
            if not self.btctxstore.validate_address(self._server_address):
                logger.error("Invalid server address '{0}'".format(
                    self._server_address
                ))
                raise exceptions.InvalidAddress(self._server_address)
        return self._server_address

    def server_url(self):
        return self._server_url

    def register(self, payout_addr):
        """Attempt to register this client address."""
        if payout_addr and not self.btctxstore.validate_address(payout_addr):
            logger.error("Invalid payout address '{0}'".format(payout_addr))
            raise exceptions.InvalidAddress(payout_addr)
        if payout_addr:
            return self._url_query("/api/register/{0}/{1}".format(
                self.get_nodeid(), payout_addr
            ))

    def set_bandwidth(self, upload, download):
        """Attempt to set bandwidth values for this client."""
        url = "/api/bandwidth/{nodeid}/{upload}/{download}"
        return self._url_query(url.format(
            nodeid=self.get_nodeid(), upload=upload, download=download
        ))

    def ping(self):
        """Send a heartbeat message for this client address."""
        return self._url_query("/api/ping/{0}".format(self.get_nodeid()))

    def audit(self, block_height, response):
        """Send audit response for this client address."""
        return self._url_query('/api/audit/%s/%s/%s' % (self.get_nodeid(),
                                                        block_height,
                                                        response))

    def height(self, height):
        """Set the height claim for this client address."""
        return self._url_query('/api/height/%s/%s' % (self.get_nodeid(),
                                                      height))
