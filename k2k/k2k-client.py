#!/usr/bin/env python

import os
import requests
import pdb


class K2KClient(object):

    def __init__(self):
        self.token_id = os.environ.get('OS_TOKEN')
        self.region_id = os.environ.get('OS_REGION')
        self.keystone_idp_url = os.environ.get('OS_KEYSTONE_IDP')
        self.session = requests.Session()
        self.verify = False

        self.HEADERS = {
            'Content-type': 'application/json',
            'X-Auth-Token': self.token_id
        }

    def _generate_token_json(self):
        return {
            "auth": {
                "identity": {
                    "methods": [
                        "token"
                    ],
                    "token": {
                        "id": self.token_id
                    }
                },
                "scope": {
                    "region": {
                        "id": self.region_id
                    }
                }
            }
        }

    def get_saml2_assertion(self):
        token = self._generate_token_json()

        r = self.session.post(url=self.keystone_idp_url,
                              data=token, headers=self.HEADERS,
                              verify=self.verify)
        if not r.ok:
            raise Exception("Something went wrong, %s" % r.response)
        pdb.set_trace()
        print r.response

if __name__ == "__main__":
    client = K2KClient()
    client.get_saml2_assertion()
