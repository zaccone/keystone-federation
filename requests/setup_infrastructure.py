#!/usr/bin/env python

import copy
import json
import uuid
import sys

import requests

import fixtures
try:
    import settings
except ImportError:
    sys.stderr.write("Cannot import settings "
                     "(check for settings.py file)")
    sys.exit(-2)


class Infrastructure(object):

    def __init__(self, config):
        self.IDP = 'testshib'
        self.MAPPING = 'basicmapping'
        self.PROTOCOL = 'saml2'

        self.DOMAIN = {}
        self.GROUP = {}
        self.PROJECT = {}
        self.ROLE = {}

        self.HEADERS = config['HEADERS']
        self.URL = config['URL']


    def _url(self, url):
        return self.URL + url

    def _check_response(self, r, expected_status):
        return r.status_code == expected_status

    def _expose_reason(self, r):
        print ("ERR: status code: %(err_code)d, "
               "response body: %(response)s") % {
                    'err_code': r.status_code,
                    'response': r.text
             }

    def _assign_group_to_rule(self):
        rules = copy.deepcopy(fixtures.RULE)
        gid = self.GROUP['id']
        if rules['mapping']['rules'][0]['local'][1]['group']['id'] is None:
            rules['mapping']['rules'][0]['local'][1]['group']['id'] = gid
        return rules

    def _get_id(self, url, name, attribute, dest):
        """Get id of already existing object in the Keystone"""
        resp = requests.get(url, headers=self.HEADERS, verify=False)
        if not resp.ok:
            self._expose_reason(resp)
            return

        data = resp.json().get(attribute)
        for x in data:
            if x['name'] == name:
                dest.update(x)
                break

    def delete_domain(self):
        raise NotImplemented()

    def add_domain(self):
        url = self._url('/v3/domains')
        body = fixtures.DOMAIN
        resp = requests.post(url, headers=self.HEADERS,
                         data=json.dumps(body), verify=False)
        if self._check_response(resp, 201):
            self.DOMAIN.update(resp.json().get('domain'))
            print "Domain %(domain)s added." % {'domain': self.DOMAIN['name']}
        elif self._check_response(resp, 409):
            self._get_id(url, fixtures.DOMAIN['domain']['name'], 'domains',
                         self.DOMAIN)
        else:
            self._expose_reason(resp)

    def delete_groups(self):
        raise NotImplemented()

    def add_groups(self):
        url = self._url('/v3/groups')
        body = copy.deepcopy(fixtures.GROUP)
        if body['group']['domain_id'] is None:
            body['group']['domain_id'] = self.DOMAIN['id']
        resp = requests.post(url, headers=self.HEADERS,
                         data=json.dumps(body), verify=False)
        if self._check_response(resp, 201):
            self.GROUP.update(resp.json().get('group'))
            print "Group %(group)s added." % {'group': self.GROUP['name']}
        elif self._check_response(resp, 409):
            self._get_id(url, fixtures.GROUP['group']['name'], 'groups',
                         self.GROUP)
        else:
            self._expose_reason(resp)

    def delete_project(self):
        raise NotImplemented()

    def add_project(self):
        url = self._url('/v3/projects')
        body = copy.deepcopy(fixtures.PROJECT)
        if body['project']['domain_id'] is None:
            body['project']['domain_id'] = self.DOMAIN['id']
        resp = requests.post(url, headers=self.HEADERS,
                         data=json.dumps(body), verify=False)
        if self._check_response(resp, 201):
            self.PROJECT.update(resp.json().get('project'))
            print "Project %(project)s added." % {'project':
                self.PROJECT['name']}
        elif self._check_response(resp, 409):
            self._get_id(url, fixtures.PROJECT['project']['name'], 'projects',
                         self.PROJECT)
        else:
            self._expose_reason(resp)

    def delete_roles(self):
        raise NotImplemented()

    def add_roles(self):
        url = self._url('/v3/roles')
        body = fixtures.ROLE
        resp = requests.post(url, headers=self.HEADERS,
                         data=json.dumps(body), verify=False)
        if self._check_response(resp, 201):
            self.ROLE.update(resp.json().get('role'))
            print "Role %(role)s added." % {'role': self.ROLE['name']}
        elif self._check_response(resp, 409):
            self._get_id(url, fixtures.ROLE['role']['name'], 'roles',
                         self.ROLE)
        else:
            self._expose_reason(resp)

    def assign_roles(self):
        url = "/v3/projects/%(project)s/groups/%(group)s/roles/%(role)s"
        url = url % {
            'project': self.PROJECT['id'],
            'group': self.GROUP['id'],
            'role': self.ROLE['id']
        }
        url = self._url(url)
        resp = requests.put(url, headers=self.HEADERS,
                             verify=False)

        if self._check_response(resp, 204):
            data = {
                'project': self.PROJECT['name'],
                'group': self.GROUP['name']
            }
            print "Group %(group)s can access %(project)s." %  data
        else:
            self._expose_reason(resp)

    def delete_idp(self):
        url = self._url('/v3/OS-FEDERATION/identity_providers/' + self.IDP)
        resp = requests.delete(url, headers=self.HEADERS, verify=False)
        if self._check_response(resp, 204):
            print "IdP %(idp)s deleted." % {'idp': self.IDP}
        else:
            self._expose_reason(resp)

    def add_idp(self):
        url = self._url('/v3/OS-FEDERATION/identity_providers/testshib')
        idp_body = fixtures.IDP
        resp = requests.put(url, headers=self.HEADERS,
                         data=json.dumps(idp_body), verify=False)
        if self._check_response(resp, 201):
            print "IdP %(idp)s added." % {'idp': self.IDP}
            self.IDP = resp.json().get('identity_provider')
        else:
            self._expose_reason(resp)

    def delete_mapping(self):
        url = self._url('/v3/OS-FEDERATION/mappings/' + self.MAPPING)
        resp = requests.delete(url, headers=self.HEADERS, verify=False)
        if self._check_response(resp, 204):
            print "Mapping %(mapping)s deleted." % {'mapping': self.MAPPING}
        else:
            self._expose_reason(resp)

    def add_mapping(self):
        url = self._url('/v3/OS-FEDERATION/mappings/' + self.MAPPING)
        rules = self._assign_group_to_rule()
        resp = requests.put(url, headers=self.HEADERS,
                            data=json.dumps(rules),
                            verify=False)
        if self._check_response(resp, 201):
            print "Mapping %(map)s created" % {'map': self.MAPPING}
            self.MAPPING = resp.json().get('mapping')
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
                        'protocols/%(protocol)s' % {'idp': self.IDP['id'],
                                                    'protocol': self.PROTOCOL})
        protocol_data = copy.deepcopy(fixtures.PROTOCOL)
        if protocol_data['protocol']['mapping_id'] is None:
            protocol_data['protocol']['mapping_id'] = self.MAPPING['id']
        resp = requests.put(url, headers=self.HEADERS,
                            data = json.dumps(protocol_data), verify=False)
        if self._check_response(resp, 201):
            print "Protocol %(protocol)s added and tied" % {'protocol':
                                                            self.PROTOCOL}
            self.PROTOCOL = resp.json().get('protocol')
        else:
            self._expose_reason(resp)

    def setup(self):
        self.add_domain()
        self.add_groups()
        self.add_project()
        self.add_roles()
        self.assign_roles()

        self.add_idp()
        self.add_mapping()
        self.add_protocol()

    def clean(self):
        self.delete_protocol()
        self.delete_mapping()
        self.delete_idp()


    def __repr__(self):
        title = "Federation objects:"
        result = [title]

        idp = """Identity Provider:
        id: %(id)s
        """ % {'id': self.IDP['id']}
        result.append(idp)

        mapping = """Mapping:
        id: %(id)s
        rules: %(rules)s
        """ % {
        'id': self.MAPPING['id'],
        'rules': self.MAPPING['rules']
        }
        result.append(mapping)
        protocol = """Protocol:
        id: %(id)s
        mapping: %(mapping)s
        """ % {
            'id': self.PROTOCOL['id'],
            'mapping': self.PROTOCOL['mapping_id']
        }
        result.append(protocol)

        project = """PROJECT:
        id: %(id)s
        name: %(name)s
        """ % {'id': self.PROJECT['id'],
                'name': self.PROJECT['name']}
        result.append(project)

        group = """GROUP:
        id: %(id)s
        name: %(name)s
        """ % {'id': self.GROUP['id'],
                'name': self.GROUP['name']}
        result.append(group)

        domain = """DOMAIN:
        id: %(id)s
        name: %(name)s
        """ % {'id': self.DOMAIN['id'],
                'name': self.DOMAIN['name']}
        result.append(domain)

        role = """ROLE:
        id: %(id)s
        name: %(name)s
        """ % {'id': self.ROLE['id'],
                'name': self.ROLE['name']}
        result.append(role)

        return '\n'.join(result)


if __name__ == '__main__':

    _config = {
        'HEADERS': settings.HEADERS,
        'URL': settings.URL
    }
    infra = Infrastructure(_config)
    infra.clean()
    infra.setup()

    print infra
