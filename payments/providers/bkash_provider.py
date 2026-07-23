import os

import requests

from .base import InitiateResult, PaymentProvider, ProviderConfigError, VerifyResult


class BkashProvider(PaymentProvider):
    name = "bkash"
    TIMEOUT = 30

    def _config(self):
        cfg = {
            "base_url": os.environ.get("BKASH_BASE_URL"),
            "app_key": os.environ.get("BKASH_APP_KEY"),
            "app_secret": os.environ.get("BKASH_APP_SECRET"),
            "username": os.environ.get("BKASH_USERNAME"),
            "password": os.environ.get("BKASH_PASSWORD"),
        }
        if not all(cfg.values()):
            raise ProviderConfigError("bKash credentials are not fully set")
        return cfg

    def _token(self, cfg):
        resp = requests.post(
            f"{cfg['base_url']}/tokenized/checkout/token/grant",
            json={"app_key": cfg["app_key"], "app_secret": cfg["app_secret"]},
            headers={"username": cfg["username"], "password": cfg["password"]},
            timeout=self.TIMEOUT,
        )
        resp.raise_for_status()
        return resp.json()["id_token"]

    def _headers(self, cfg, token):
        return {"Authorization": token, "X-APP-Key": cfg["app_key"]}

    def initiate(self, order):
        cfg = self._config()
        token = self._token(cfg)
        resp = requests.post(
            f"{cfg['base_url']}/tokenized/checkout/create",
            json={
                "mode": "0011",
                "amount": str(order.total_amount),
                "currency": "BDT",
                "intent": "sale",
                "merchantInvoiceNumber": f"order-{order.id}",
            },
            headers=self._headers(cfg, token),
            timeout=self.TIMEOUT,
        )
        resp.raise_for_status()
        data = resp.json()
        return InitiateResult(
            transaction_id=data["paymentID"],
            client_data={"bkash_url": data.get("bkashURL"), "payment_id": data["paymentID"]},
            raw_response=data,
        )

    def verify(self, payload):
        # bKash confirms by executing then querying the payment status
        cfg = self._config()
        token = self._token(cfg)
        payment_id = payload["payment_id"]
        resp = requests.post(
            f"{cfg['base_url']}/tokenized/checkout/execute",
            json={"paymentID": payment_id},
            headers=self._headers(cfg, token),
            timeout=self.TIMEOUT,
        )
        resp.raise_for_status()
        data = resp.json()
        success = data.get("transactionStatus") == "Completed"
        return VerifyResult(transaction_id=payment_id, success=success, raw_response=data)
