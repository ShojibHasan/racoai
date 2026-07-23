from abc import ABC, abstractmethod
from dataclasses import dataclass, field


class ProviderConfigError(Exception):
    # Raised when a provider is used without its keys configured
    pass


@dataclass
class InitiateResult:
    transaction_id: str
    client_data: dict = field(default_factory=dict)
    raw_response: dict = field(default_factory=dict)


@dataclass
class VerifyResult:
    transaction_id: str
    success: bool
    raw_response: dict = field(default_factory=dict)


class PaymentProvider(ABC):
    name = ""

    @abstractmethod
    def initiate(self, order):
        # Start a payment for the order, return an InitiateResult
        raise NotImplementedError

    @abstractmethod
    def verify(self, payload):
        # Interpret a webhook or query payload, return a VerifyResult
        raise NotImplementedError
