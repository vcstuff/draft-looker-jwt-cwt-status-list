from jwcrypto import jwk, jwt
from status_list import StatusList
from datetime import datetime
from typing import Dict
import status_types
import json

DEFAULT_ALG = "ES256"


class StatusListJWT:
    list: StatusList
    issuer: str
    typ: str
    _key: jwk.JWK
    _alg: str

    def __init__(
        self,
        issuer: str,
        key: jwk.JWK,
        typ: str = None,
        list: StatusList = None,
        size: int = 2**20,
        bits: int = 1,
        alg: str = None,
    ):
        if typ in status_types.BIT_SIZES:
            bits = status_types.BIT_SIZES[typ]
        elif typ is None:
            typ = "revocation-list"
        if list is not None:
            self.list = list
        else:
            self.list = StatusList(size, bits)
        self.issuer = issuer
        self._key = key
        self.typ = typ
        if alg is not None:
            self._alg = alg
        else:
            self._alg = DEFAULT_ALG

    @classmethod
    def fromJWT(cls, input: str, key: jwk.JWK):
        decoded = jwt.JWT(jwt=input, key=key, expected_type="JWS")
        claims = json.loads(decoded.claims)
        status_list = claims["status_list"]
        typ = status_list["typ"]
        lst = status_list["lst"]
        issuer = claims["iss"]
        bits = status_types.BIT_SIZES[typ]
        list = StatusList.fromEncoded(encoded=lst, bits=bits)
        header = json.loads(decoded.header)
        alg = header["alg"]
        return cls(
            issuer=issuer,
            key=key,
            typ=typ,
            list=list,
            size=list.size,
            bits=list.bits,
            alg=alg,
        )

    def set(self, pos: int, value: int):
        self.list.set(pos, value)

    def get(self, pos: int) -> int:
        return self.list.get(pos)

    def buildJWT(
        self,
        iat: datetime = datetime.utcnow(),
        exp: datetime = None,
        optional_claims: Dict = None,
        optional_header: Dict = None,
        compact=True,
    ) -> str:
        # build claims
        if optional_claims is not None:
            claims = optional_claims
        else:
            claims = {}
        claims["iss"] = self.issuer
        claims["iat"] = int(iat.timestamp())
        if exp is not None:
            claims["exp"] = int(exp.timestamp())
        encoded_list = self.list.encode()
        claims["status_list"] = {
            "typ": self.typ,
            "lst": encoded_list,
        }

        # build header
        if optional_header is not None:
            header = optional_header
        else:
            header = {}
        if self._key.key_id:
            header["kid"] = self._key.key_id
        header["alg"] = self._alg

        token = jwt.JWT(header=header, claims=claims)
        token.make_signed_token(self._key)
        return token.serialize(compact=compact)