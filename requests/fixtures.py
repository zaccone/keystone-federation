ROLE = {
    "role": {
        "name": "fed-role"
    }
}

IDP = {
    "identity_provider": {
        "description": "testshib @ https://www.testshib.org",
        "enabled": True
    }
}

PROTOCOL = {
    "protocol": {
        "mapping_id": None
    }
}

RULE = {
    "mapping": {
        "rules":[
            {
                "local": [
                    {
                        "user": {
                            "name": "testhib user"
                        }
                    },
                    {
                    	"group": {
                    		"id": None
                    	}
                    }
                ],
                "remote": [
                    {
                        "type": "eppn",
                        "any_one_of": [
                            "myself@testshib.org",
                            "alterego@testshib.org"
                        ]
                    }
                ]
            }
        ]
    }
}

PROJECT = {
    "project": {
    	"description": "Project for federation test",
    	"domain_id": None,
    	"enabled": True,
    	"name": "federation project"
    }
}

DOMAIN = {
    "domain": {
        "description": "Federation Domain",
        "enabled": True,
        "name": "federation"
    }
}

GROUP = {
    "group": {
        "description": "federation group",
        "name": "fedgroup"
    }
}
