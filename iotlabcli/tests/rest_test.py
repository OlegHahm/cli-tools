# -*- coding:utf-8 -*-
""" Test the iotlabcli.rest module """

# pylint: disable=too-many-public-methods
# pylint: disable=protected-access

import unittest
try:
    # pylint: disable=import-error,no-name-in-module
    from mock import patch, Mock
except ImportError:  # pragma: no cover
    # pylint: disable=import-error,no-name-in-module
    from unittest.mock import patch, Mock
from iotlabcli import rest
from iotlabcli.helpers import json_dumps
from iotlabcli.tests.my_mock import RequestRet


class TestRest(unittest.TestCase):
    """ Test the iotlabcli.rest module
    As the interface itself cannot really be unit-tested against the remote
    REST server, I only test the internal functionnalities.

    Also, most of the internal code execution has been done by the upper layers
    So I don't re-check every method that just does formatting.
    """
    _url = 'http://url.test.org/rest/method/query'

    def test__method(self):
        """ Test Api._method rest submission """
        ret = {'test': 'val'}
        ret_val = RequestRet(content=json_dumps(ret).encode('utf-8'),
                             status_code=200)
        post = patch('requests.post', return_value=ret_val).start()
        delete = patch('requests.delete', return_value=ret_val).start()
        get = patch('requests.get', return_value=ret_val).start()

        # pylint:disable=protected-access
        _auth = Mock()

        # call get
        ret = rest.Api._method(self._url)
        get.assert_called_with(self._url, auth=None)
        self.assertEquals(ret, ret)
        ret = rest.Api._method(self._url, method='GET', auth=_auth)
        get.assert_called_with(self._url, auth=_auth)
        self.assertEquals(ret, ret)

        # call delete
        ret = rest.Api._method(self._url, method='DELETE')
        delete.assert_called_with(self._url, auth=None)
        self.assertEquals(ret, ret)

        # call post
        ret = rest.Api._method(self._url, method='POST', data={})
        post.assert_called_with(
            self._url, data='{}'.encode('utf-8'),
            headers={'content-type': 'application/json'},
            auth=None)
        self.assertEquals(ret, ret)

        # call multipart
        _files = {'entry': '{}'}
        ret = rest.Api._method(self._url, method='MULTIPART', data=_files)
        post.assert_called_with(self._url, files=_files, auth=None)
        self.assertEquals(ret, ret)
        patch.stopall()

    def test__method_raw(self):
        """ Run as Raw mode """
        ret_val = RequestRet(content='text_only'.encode('utf-8'),
                             status_code=200)
        with patch('requests.get', return_value=ret_val):
            ret = rest.Api._method(self._url, raw=True)
            self.assertEquals(ret, 'text_only'.encode('utf-8'))

    def test__method_errors(self):
        """ Test Api._method rest submission error cases """

        # invalid status code
        ret_val = RequestRet(content='return_text'.encode('utf-8'),
                             status_code=404)
        with patch('requests.get', return_value=ret_val):
            self.assertRaises(RuntimeError, rest.Api._method, self._url)
