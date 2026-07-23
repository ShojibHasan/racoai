from .bkash_provider import BkashProvider
from .stripe_provider import StripeProvider

# Adding a provider is one entry here plus its class, order logic stays untouched
PROVIDERS = {
    StripeProvider.name: StripeProvider,
    BkashProvider.name: BkashProvider,
}


def get_provider(name):
    try:
        return PROVIDERS[name]()
    except KeyError:
        raise ValueError(f"Unknown payment provider: {name}")
