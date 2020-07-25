DEVICES_LIST_EXAMPLES = {
    200: {
        "description": "Available devices for user",
        "content": {
            "application/json": {
                "example": [
                    {
                        "id": "dd8475c9-80b8-472a-a7ba-c5aeff36fb9d",
                        "online": True,
                        "name": "Manjaro-Desktop",
                        "domain": "mirumon.dev",
                        "os":[
                            {
                                "name": "Windows 10 Edu",
                                "version": "1.12.12",
                                "os_architecture": "amd64",
                                "serial_number": "AGFNE-34GS-RYHRE",
                                "number_of_users": 4,
                                "install_date": "2020-09-12"
                            }
                        ],
                        "last_user": {
                            "name": "nick",
                            "fullname": "Nick Khitrov",
                            "domain": "mirumon.dev",
                        },
                    },
                    {
                        "id": "8f27dd84-5547-4873-bb80-3e59e5717546",
                        "online": False,
                        "name": "RED-DESKTOP",
                        "domain": "mirumon.dev",
                        "last_user": {
                            "name": "aredruss",
                            "fullname": "Alexander Medyanik",
                            "domain": "mirumon.dev",
                        },
                    },
                ],
            },
        },
    },
}
