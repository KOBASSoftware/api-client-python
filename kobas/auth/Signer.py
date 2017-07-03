#!/usr/bin/env python

import time
from urlparse import urlparse
import urllib
import hmac
import hashlib
import re
import binascii


class Signer:
    def __init__(self, company_id, identifier, secret):
        self.company_id = company_id
        self.identifier = identifier
        self.secret = secret

        self.region = 'uk-lon-1'
        self.terminator = 'kbs_request'
        self.auth_type = 'Bearer'

        self.url = None
        self.parsed_url = None
        self.http_method = None
        self.params = None
        self.service = None
        self.headers = None
        self.signed_headers = {}

    def sign_request(self, http_method, url, signed_headers=None, params=None):
        self.set_url(url)
        self.http_method = http_method
        self.params = params

        now = time.gmtime()

        signed_headers['X-Kbs-Date'] = time.strftime('%Y%m%dT%H%M%SZ', now)

        self.headers = signed_headers

        signature = self.get_signature(now)

        signed_headers['Authorization'] = self.get_authorisation(now, signature)

        headers = {}

        for key, value in signed_headers.items():
            headers[key] = value

        return headers

    def get_authorisation(self, now, signature):
        authorisation = self.auth_type + ' Credential=' + str(self.company_id) + '-' + self.identifier + '/'
        authorisation += self.credential_scope(now) + ',' + 'SignedHeaders=' + ';'.join(self.signed_headers) + ','
        authorisation += 'Signature=' + self.hex16(signature)
        return authorisation

    def get_signature(self, now):
        k_date = self.h_mac('KBS3' + self.secret, time.strftime('%Y%m%d', now))
        k_region = self.h_mac(k_date, self.region)
        k_service = self.h_mac(k_region, self.service)
        k_credentials = self.h_mac(k_service, self.terminator)

        return self.h_mac(k_credentials, self.string_to_sign(now))

    def string_to_sign(self, now):
        string_to_sign = self.auth_type + "\n"
        string_to_sign += time.strftime('%Y%m%dT%H%M%SZ', now) + "\n"
        string_to_sign += self.credential_scope(now) + "\n"
        string_to_sign += self.hex16(self.hash(self.canonical_request()))
        return string_to_sign

    def canonical_request(self):
        cr = str(self.http_method) + "\n"
        cr += self.canonical_uri(self.parsed_url.path) + "\n"
        cr += self.canonical_query_string(self.parsed_url.query) + "\n"
        cr += self.canonical_headers(self.headers) + "\n"
        cr += self.payload_hash(self.params)
        return cr

    def canonical_uri(self, path):
        if len(path) > 0:
            return path
        return '/'

    def canonical_query_string(self, query):

        params = query.split('&')
        params = sorted(params)
        canonical = []
        for kv in params:
            if kv == '':
                continue
            key, value = kv.split('=')
            canonical.append(self.rfc3986encode(key) + "=" + self.rfc3986encode(self.rfc3986decode(value)))

        return '&'.join(canonical)

    def canonical_headers(self, headers):
        headers = self.get_filtered_headers(headers)
        canonical_headers = ''
        signed_headers = []

        for key in sorted(headers.iterkeys()):
            # Strip line breaks and remove consecutive spaces. Services collapse whitespace in signature calculation
            value = headers[key]
            value = re.sub('/\s+/', ' ', value.strip())
            canonical_headers += key.lower() + ':' + value + "\n"
            signed_headers.append(key.lower())

        self.signed_headers = signed_headers

        return canonical_headers + "\n" + ';'.join(signed_headers)

    def credential_scope(self, now):
        return time.strftime('%Y%m%d', now) + '/' + self.region + '/' + str(self.service) + '/' + self.terminator

    def get_filtered_headers(self, headers):
        if len(self.signed_headers) == 0:
            return headers

        for k, v in headers.items():
            if k in self.signed_headers:
                del (headers[k])

        return headers

    def payload_hash(self, params):
        if params:
            string = urllib.urlencode(params)
        else:
            string = ''

        return self.hex16(self.hash(string))

    def set_url(self, url):
        self.parsed_url = urlparse(url=url)

        if self.parsed_url.query:
            self.parsed_url._replace(query=self.rfc3986decode(self.parsed_url.query))

        self.service = self.parsed_url.path.replace('/v2', '')
        self.service = self.service.strip('/')

    def rfc3986decode(self, string):
        string.replace('~', '%7E')
        return urllib.unquote(string)

    def rfc3986encode(self, string):
        string.replace('%7E', '~')
        return urllib.quote(string)

    def hex16(self, string):
        return binascii.hexlify(string)

    def hash(self, string):
        return hashlib.sha256(string).digest()

    def h_mac(self, key, string):
        return hmac.new(key=key, msg=string, digestmod=hashlib.sha256).digest()
