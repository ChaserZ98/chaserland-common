import json
from dataclasses import asdict

import pytest
from chaserland_common.jwt import JWT, JWTBearer, JWTHeader, JWTPayload


class TestJWT:
    def setup_method(self):
        self.jwt_header = JWTHeader(alg="ES256", typ="JWT")
        self.jwt_payload = JWTPayload(
            sub="1234567890", name="John Doe", admin=True, iat=1516239022
        )
        self.jwt = JWT(header=self.jwt_header, payload=self.jwt_payload)

        self.jwt_bearer = JWTBearer(
            access_token="eyJhbGciOiJFUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiYWRtaW4iOnRydWUsImlhdCI6MTUxNjIzOTAyMn0.tyh-VfuzIxCyGYDlkBA7DfyjrqmSHu6pQ2hoZuFqUSLPNY2N0mpHb3nk5K17HWP_3cYHBw7AhHale5wky6-sVA",
            token_type="Bearer",
        )
        self.private_key = """-----BEGIN PRIVATE KEY-----
MIGHAgEAMBMGByqGSM49AgEGCCqGSM49AwEHBG0wawIBAQQgevZzL1gdAFr88hb2
OF/2NxApJCzGCEDdfSp6VQO30hyhRANCAAQRWz+jn65BtOMvdyHKcvjBeBSDZH2r
1RTwjmYSi9R/zpBnuQ4EiMnCqfMPWiZqB4QdbAd0E7oH50VpuZ1P087G
-----END PRIVATE KEY-----"""
        self.public_key = """-----BEGIN PUBLIC KEY-----
MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEEVs/o5+uQbTjL3chynL4wXgUg2R9
q9UU8I5mEovUf86QZ7kOBIjJwqnzD1omageEHWwHdBO6B+dFabmdT9POxg==
-----END PUBLIC KEY-----"""

    def test_jwt_encode(self):
        # Test dict data type
        assert (
            self.jwt_header.to_urlsafe_base64()
            == self.jwt_bearer.access_token.split(".")[0]
        )
        assert (
            self.jwt_payload.to_urlsafe_base64()
            == self.jwt_bearer.access_token.split(".")[1]
        )

        # Test bytes data type
        assert (
            JWT.encode(
                json.dumps(asdict(self.jwt_header), separators=(",", ":")).encode(
                    "utf-8"
                )
            )
            == self.jwt_bearer.access_token.split(".")[0]
        )
        assert (
            JWT.encode(
                json.dumps(self.jwt_payload, separators=(",", ":")).encode("utf-8"),
            )
            == self.jwt_bearer.access_token.split(".")[1]
        )

        # Test unsupported data type
        invalid_data = "paragraph shout complete question specific but hold center having lovely operation help product bee brain orange lonely available image wire political call bread village"

        with pytest.raises(Exception) as exc_info:
            JWT.encode(
                invalid_data,
            )
        assert isinstance(exc_info.value, ValueError)
        assert exc_info.value.args[0] == f"Unsupported data type: {type(invalid_data)}"

    def test_jwt_decode(self):
        assert JWT.decode(self.jwt_bearer.access_token.split(".")[0]) == asdict(
            self.jwt_header
        )
        assert (
            JWT.decode(self.jwt_bearer.access_token.split(".")[1]) == self.jwt_payload
        )

    def test_jwt_verify(self):
        # Test valid JWT
        assert self.jwt_bearer.verify(self.public_key)

        # Test invalid JWT with missing parts
        invalid_jwt_bearer = JWTBearer(
            "eyJhbGciOi",
            token_type="Bearer",
        )
        assert not invalid_jwt_bearer.verify(self.public_key)

        # Test invalid JWT with invalid signature
        invalid_jwt_bearer = JWTBearer(
            access_token="eyJhbGciOiJFUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiYWRtaW4iOnRydWUsImlhdCI6MTUxNjIzOTAyMn0.tyh-VfuzIxCyGYDlkBA7DfyjrqmSHu6pQ2hoZuFqUSLPNY2N0mpHb3nk5K17HWP_",
            token_type="Bearer",
        )
        assert not invalid_jwt_bearer.verify(self.public_key)

    def test_jwt_sign(self):
        # Test valid JWT
        bearer_string = self.jwt.generate_bearer_string(self.private_key)
        assert JWTBearer(access_token=bearer_string, token_type="Bearer").verify(
            self.public_key
        )

        # Test invalid mode
        invalid_mode = "unknown mode"
        with pytest.raises(Exception) as exc_info:
            self.jwt.generate_bearer_string(self.private_key, mode=invalid_mode)
        assert isinstance(exc_info.value, ValueError)
        assert exc_info.value.args[0] == f"Unsupported mode: {invalid_mode}"

    def test_bearer_to_jwt(self):
        assert self.jwt_bearer.to_jwt() == self.jwt

    def test_jwt_to_bearer(self):
        bearer = self.jwt.to_bearer(self.private_key)
        assert bearer.verify(self.public_key)
        assert JWT.decode(bearer.access_token.split(".")[0]) == asdict(self.jwt_header)
        assert JWT.decode(bearer.access_token.split(".")[1]) == self.jwt_payload
