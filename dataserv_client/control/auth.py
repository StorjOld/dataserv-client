import datetime
import email.utils
import time


def create_authentication_headers(btctxstore, remote_address, auth_wif):
    header_date = email.utils.formatdate(
        timeval=time.mktime(datetime.datetime.now().timetuple()),
        localtime=True, usegmt=True)
    msg = remote_address + " " + header_date
    header_authorization = btctxstore.sign_unicode(auth_wif, msg)
    return {"Date": header_date, "Authorization": header_authorization}
