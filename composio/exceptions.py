class ComposioError(Exception):
    pass


class ApiKeyNotProvidedError(ComposioError):
    pass


class InvalidParams(ComposioError):
    pass


class NoItemsFound(ComposioError):
    pass


class WebhookSignatureVerificationError(ComposioError):
    pass


class WebhookPayloadError(ComposioError):
    pass


class ComposioSDKTimeoutError(ComposioError):
    pass


class ComposioMultipleConnectedAccountsError(ComposioError):
    pass
