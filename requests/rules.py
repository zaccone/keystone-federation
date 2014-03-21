RULE = { 
    "mapping": { 
        "rules":[
            {
                "local": [
                    {
                        "user": {
                            "name": "{0}"
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
