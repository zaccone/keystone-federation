#!/usr/bin/env python

import copy
import json
import requests
import pdb
import uuid

import idps
import protocols
import rules

class Infrastructure(object):
    HEADERS = {'X-Auth-Token': '',
            'Content-type': 'application/json'
    }

    URL = 'localhost'
    def __init__(self, idp=None, mapping=None, protocol=None):
        self.IDP = idp or 'testshib'
        self.MAPPING = mapping or 'basicmapping'
        self.PROTOCOL = protocol or 'saml2'

    def _url(self, url):
        return self.URL + url

    def _check_response(self, r, expected_status):
        return r.status_code == expected_status

    def _expose_reason(self, r):
        print "ERR: status code: %(err_code)d, response body: %(response)s" % {
            'response': r.text,
            'err_code': r.status_code
        }

    def delete_idp(self):
        url = self._url('/v3/OS-FEDERATION/identity_providers/' + self.IDP)
        resp = requests.delete(url, headers=self.HEADERS)
        if self._check_response(resp, 204):
            print "IdP %(idp)s deleted." % {'idp': self.IDP}
        else:
            self._expose_reason(resp)

    def add_idp(self):
        url = self._url('/v3/OS-FEDERATION/identity_providers/testshib')
        idp_body = idps.IDP
        resp = requests.put(url, headers=self.HEADERS,
                         data=json.dumps(idp_body), verify=False)
        if self._check_response(resp, 201):
            print "IdP %(idp)s added." % {'idp': self.IDP}
        else:
            self._expose_reason(resp)

    def delete_mapping(self):
        url = self._url('/v3/OS-FEDERATION/mappings/' + self.MAPPING)
        resp = requests.delete(url, headers=self.HEADERS)
        if self._check_response(resp, 204):
            print "Mapping %(mapping)s deleted." % {'mapping': self.MAPPING}
        else:
            self._expose_reason(resp)

    def add_mapping(self):
        url = self._url('/v3/OS-FEDERATION/mappings/' + self.MAPPING)
        resp = requests.put(url, headers=self.HEADERS,
                            data=json.dumps(rules.RULE),
                            verify=False)
        if self._check_response(resp, 201):
            print "Mapping %(map)s created" % {'map': self.MAPPING}
        else:
            self._expose_reason(resp)

    def delete_protocol(self):
        url = self._url('/v3/OS-FEDERATION/identity_providers/%(idp)s/'
                        'protocols/%(protocol)s' % {'idp': self.IDP,
                                                    'protocol': self.PROTOCOL})

        resp = requests.delete(url, headers=self.HEADERS,
                              verify=False)
        if self._check_response(resp, 204):
            print "Protocol %(protocol)s was deleted" % {'protocol':
                self.PROTOCOL}
        else:
            self._expose_reason(resp)

    def add_protocol(self):
        url = self._url('/v3/OS-FEDERATION/identity_providers/%(idp)s/'
                        'protocols/%(protocol)s' % {'idp': self.IDP,
                                                    'protocol': self.PROTOCOL})
        protocol_data = copy.deepcopy(protocols.PROTOCOL)
        protocol_data['protocol']['mapping_id'] = self.MAPPING
        resp = requests.put(url, headers=self.HEADERS,
                            data = json.dumps(protocol_data))
        if self._check_response(resp, 201):
            print "Protocol %(protocol)s added and tied" % {'protocol':
                                                            self.PROTOCOL}
        else:
            self._expose_reason(resp)

    def setup(self):
        self.add_idp()
        self.add_mapping()
        self.add_protocol()

    def clean(self):
        self.delete_protocol()
        self.delete_mapping()
        self.delete_idp()

if __name__ == '__main__':
    infra = Infrastructure()
    infra.clean()
    infra.setup()
