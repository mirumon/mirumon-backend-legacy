from mirumon.api.api_model import APIModel


class Software(APIModel):
    name: str
    vendor: str
    version: str


class GetListDeviceSoftware(APIModel):
    __root__: list[Software]
