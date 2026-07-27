from dataclasses import dataclass

__all__ = [
    "TokenPackage",
    "TOKEN_PACKAGES",
    "TOKEN_PACKAGES_BY_CALLBACK",
    "TOKEN_PACKAGES_BY_PAYLOAD",
]


@dataclass(frozen=True)
class TokenPackage:
    tokens: int
    stars: int
    callback_data: str
    payload: str


TOKEN_PACKAGES = [
    TokenPackage(tokens=5_000, stars=1, callback_data="buy_tokens_5000", payload="tokens_5000"),
    TokenPackage(tokens=10_000, stars=10, callback_data="buy_tokens_10000", payload="tokens_10000"),
    TokenPackage(tokens=25_000, stars=25, callback_data="buy_tokens_25000", payload="tokens_25000"),
]

TOKEN_PACKAGES_BY_CALLBACK = {package.callback_data: package for package in TOKEN_PACKAGES}
TOKEN_PACKAGES_BY_PAYLOAD = {package.payload: package for package in TOKEN_PACKAGES}
