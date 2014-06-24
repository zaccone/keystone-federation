#!/usr/bin/env python

import json

import requests

from keystoneclient import exceptions
from keystoneclient import session
from keystoneclient.contrib.auth.v3 import saml2

VALID_PROJECT_ID='52d153c6814745eca2a6061adc327985'
INVALID_PROJECT_ID='52d153c6814745eca2a6061adc327985ERROR'

IDENTITY_PROVIDER = 'testshib'
IDENTITY_PROVIDER_URL = "https://idp.testshib.org/idp/profile/SAML2/SOAP/ECP"

# Parameters are as follows: (auth_url, IdP_user, IdP_password, 
#                             IdP_name(registered in Keystone)
#                              IdP_url
                            
ARGS_PARAMS = ('https://openstack5000.local:5000/v3', 'myself', 'myself',
               IDENTITY_PROVIDER, IDENTITY_PROVIDER_URL)

class Client(object):
    def __init__(self, auth_url, username, password,
                 identity_provider, identity_provider_url,
                 project_id=None, domain_id=None):
        self.username = username
        self.password = password
        self.identity_provider = identity_provider
        self.identity_provider_url = identity_provider_url
        self.project_id = project_id
        self.domain_id = domain_id

        self.session = session.Session(session=requests.session(),
                                       verify=False)
        self.unscoped_plugin = saml2.Saml2UnscopedToken(
            auth_url, identity_provider, identity_provider_url,
            username, password)

        self.scoped_plugin = saml2.Saml2ScopedToken(
            auth_url, unscoped_auth=self.unscoped_plugin,
            project_id=project_id, domain_id=domain_id)

        self.scoped_token, self.unscoped_token = None, None

    def __str__(self):
        t = tuple([json.dumps(x, indent=4, separators=(', ', ': ')) 
                   for x in (self.scoped_token, self.unscoped_token)])
        return "Unscoped token: %s\n Scoped token %s" % t 
    def login(self):
        self.unscoped_token = self.unscoped_plugin.get_auth_ref(self.session)
        try:
            self.scoped_token = self.scoped_plugin.get_auth_ref(self.session)
        except exceptions.ScopingTokenError as e:
            print e.projects[0] + json.dumps(e.projects[1], sort_keys=True,
                                             indent=4, separators=(',', ': '))
            print e.domains[0] + json.dumps(e.domains[1], sort_keys=True,
                                            indent=4, separators=(',', ': '))



def main():
    client = Client(*ARGS_PARAMS)
    client.login()

    client_scoped = Client(*ARGS_PARAMS, project_id=VALID_PROJECT_ID)
    client_scoped.login()

    print client
    print client_scoped

if __name__ == '__main__':
    main()
