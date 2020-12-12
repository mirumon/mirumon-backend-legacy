from datetime import datetime, timedelta
from typing import Dict, Final

from jose import jwt
from loguru import logger
from passlib.context import CryptContext
from pydantic import BaseModel, SecretStr

from mirumon.domain.devices.entities import Device, DeviceID
from mirumon.settings.environments.app import AppSettings


class MetaJWT(BaseModel):
    exp: datetime
    sub: str


class DeviceInToken(BaseModel):
    id: DeviceID

    def to_jwt_content(self) -> Dict[str, Dict[str, str]]:
        payload = self.dict()
        payload["id"] = str(self.id)
        return {"device": payload}


class DevicesAuthService:
    jwt_subject: Final = "access"
    algorithm: Final = "HS256"
    pwd_context: Final = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def __init__(self, settings: AppSettings):
        self.settings = settings
        self.token_expire = timedelta(days=365)  # noqa: WPS432

    def is_valid_shared_key(self, shared_key: SecretStr) -> bool:
        return (
            shared_key.get_secret_value() == self.settings.shared_key.get_secret_value()
        )

    def create_device_token(self, device: Device) -> str:
        content = DeviceInToken(id=device.id).to_jwt_content()
        secret_key = self.settings.secret_key.get_secret_value()
        delta = self.token_expire
        return self.create_jwt_token(
            jwt_content=content, secret_key=secret_key, expires_delta=delta
        )

    async def get_device_from_token(self, token: str) -> DeviceInToken:
        try:
            content = self.get_content_from_token(
                token, self.settings.secret_key.get_secret_value()
            )
        except ValueError:  # noqa: WPS329
            raise RuntimeError

        device_payload = content.get("device")
        return DeviceInToken.parse_obj(device_payload)

    def create_jwt_token(
        self,
        *,
        jwt_content: Dict[str, Dict[str, str]],
        secret_key: str,
        expires_delta: timedelta,
    ) -> str:
        to_encode = jwt_content.copy()
        expire = datetime.utcnow() + expires_delta
        to_encode.update(MetaJWT(exp=expire, sub=self.jwt_subject).dict())
        return jwt.encode(to_encode, secret_key, algorithm=self.algorithm)

    def get_content_from_token(self, token: str, secret_key: str) -> Dict[str, str]:
        try:
            return jwt.decode(token, secret_key, algorithms=[self.algorithm])
        except jwt.JWTError as decode_error:
            logger.debug("jwt decode error")
            raise ValueError("unable to decode JWT token") from decode_error
