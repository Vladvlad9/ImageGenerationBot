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
    generations: int
    callback_data: str
    payload: str


TOKEN_PACKAGES = [
    TokenPackage(
        tokens=5_000,
        stars=15,
        generations=1,
        callback_data="buy_tokens_5000",
        payload="tokens_5000",
    ),
    TokenPackage(
        tokens=40_000,
        stars=100,
        generations=8,
        callback_data="buy_tokens_40000",
        payload="tokens_40000",
    ),
    TokenPackage(
        tokens=110_000,
        stars=250,
        generations=22,
        callback_data="buy_tokens_110000",
        payload="tokens_110000",
    ),
    TokenPackage(
        tokens=240_000,
        stars=500,
        generations=48,
        callback_data="buy_tokens_240000",
        payload="tokens_240000",
    ),
    TokenPackage(
        tokens=500_000,
        stars=1_000,
        generations=100,
        callback_data="buy_tokens_500000",
        payload="tokens_500000",
    ),
]

TOKEN_PACKAGES_BY_CALLBACK = {package.callback_data: package for package in TOKEN_PACKAGES}
TOKEN_PACKAGES_BY_PAYLOAD = {package.payload: package for package in TOKEN_PACKAGES}
