# Payment flow diagrams

Both providers share one shape: initiate a payment, let the provider confirm, verify the result, then settle. Settling marks the order paid and reduces stock atomically, or cancels the order on failure. Settlement is idempotent.

## Stripe

```mermaid
sequenceDiagram
    participant U as User
    participant API as Backend API
    participant S as Stripe

    U->>API: POST /payments/initiate/ {order, "stripe"}
    API->>S: create PaymentIntent(amount, metadata)
    S-->>API: intent id + client_secret
    API-->>U: Payment(pending) + client_secret
    U->>S: confirm payment with client_secret
    S->>API: webhook payment_intent.succeeded (signed)
    API->>API: verify signature, settle_payment
    API->>API: order paid, stock reduced (atomic, locked)
    API-->>S: 200 received
```

On `payment_intent.payment_failed` or a signature mismatch, the payment is marked failed and the order canceled; stock is untouched.

## bKash

```mermaid
sequenceDiagram
    participant U as User
    participant API as Backend API
    participant B as bKash

    U->>API: POST /payments/initiate/ {order, "bkash"}
    API->>B: grant token
    B-->>API: id_token
    API->>B: create payment(amount, invoice)
    B-->>API: paymentID + bkashURL
    API-->>U: Payment(pending) + bkashURL
    U->>B: pay at bkashURL
    U->>API: POST /payments/webhook/bkash/ {payment_id}
    API->>B: execute + query payment
    B-->>API: transactionStatus
    API->>API: settle_payment (success -> paid + stock, else canceled)
    API-->>U: 200 received
```

## Settlement rules (both providers)

- Runs in `transaction.atomic`.
- The payment row is locked with `select_for_update`; an already settled payment returns early, so repeated webhooks do not double-apply.
- On success, each product row is locked and re-checked before its stock is reduced, preventing overselling. If stock is short, the payment fails and the order is canceled.
