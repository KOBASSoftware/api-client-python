#!/usr/bin/env python
import requests
import urllib


class Client:
    def __init__(self, signer):
        self.signer = signer
        self.api_base_url = 'https://api.kobas.co.uk'
        self.api_version = 'v2'
        self.ssl_verify_peer = True
        self.requests = requests.Session()

    def get(self, route, params, headers):
        return self.call(http_method='GET', route=route, params=params, headers=headers)

    def post(self, route, params, headers):
        return self.call(http_method='POST', route=route, params=params, headers=headers)

    def put(self, route, params, headers):
        return self.call(http_method='PUT', route=route, params=params, headers=headers)

    def delete(self, route, params, headers):
        return self.call(http_method='DELETE', route=route, params=params, headers=headers)

    def call(self, http_method, route, params, headers):
        url = self.api_base_url + '/' + self.api_version + '/' + route

        if http_method == 'GET':
            if len(params) > 0:
                url += "?" + urllib.urlencode(params)
                params = {}

        headers = self.signer.sign_request(http_method=http_method, url=url, signed_headers=headers, params=params)

        if http_method == 'POST':
            r = self.requests.post(url=url, headers=headers, params=params, verify=self.ssl_verify_peer)
        elif http_method == 'PUT':
            r = self.requests.put(url=url, headers=headers, params=params, verify=self.ssl_verify_peer)
        elif http_method == 'DELETE':
            r = self.requests.delete(url=url, headers=headers, params=params, verify=self.ssl_verify_peer)
        else:
            r = self.requests.get(url=url, headers=headers, params=params, verify=self.ssl_verify_peer)

        if r.status_code >= 400:
            try:
                raise HttpException(r.status_code, r.json)
            finally:
                raise HttpException(r.status_code)

        return r.json()


class HttpException(Exception):
    pass
