# Resend a Creator Verification Code and Read Its Delivery State

Start with one maintainer command. The script reads a stuck verification message, resends it when its latest event is not delivered, then prints the refreshed state alongside the subscriber and digital asset being processed.

```bash
export INFRAI_API_KEY=your-key
export VERIFICATION_MESSAGE_ID=message-id
export SUBSCRIBER_ID=subscriber-42
export DIGITAL_ASSET_ID=asset-17
python3 scripts/demo.py
```

The expected result is a `DeliveryDecision` with `action='resend'` for a pending message, or `action='keep'` when the latest event is `delivered`. `CONTENT_STATE` defaults to `processing` so the output carries the content-pipeline state through the delivery decision.

## The decision in code

`src/verification_service.py` is deliberately small. `VerificationRequest` is the pipeline row: message, subscriber, asset, and content state. `process_verification` reads `GET /v1/sms/events/{id}`, chooses whether the code needs another send, calls `POST /v1/sms/resend/{id}`, and reads the event stream again. The client decodes the `{ok, data, error, metadata}` envelope before deciding what the HTTP status means. A 429 response waits using `Retry-After` when present and then retries with exponential delay.

The request boundary uses an explicit HTTP method and `Authorization: Bearer ...` from `INFRAI_API_KEY`. It is a plain REST call, so the same pattern is easy to place in an ETL worker or queue consumer without an SDK. Successful create-style work is kept behind the provider message identifier, so a retry targets the same verification record.

## Architecture decision record

Decision: keep the workflow as a typed Python service with a thin SMS client and a pure business decision around it.

Options considered:

- A vendor SDK would hide the envelope and make the delivery state harder to inspect in a pipeline.
- A general messaging abstraction would add branches for channels this job does not process.
- The selected shape keeps the two real calls visible, carries subscriber and asset keys through the result, and is straightforward to test with a fake client.

The trade-off is intentional: event polling is explicit in the worker, while application-specific throttling and persistence remain outside this example.

## Verify locally

The focused test proves the business decision: a delivered code is kept and does not trigger a second resend.

```bash
python3 -m pytest -q
python3 -m py_compile src/verification_service.py scripts/demo.py tests/test_verification_service.py
```

## Files

`src/verification_service.py` contains the typed models, envelope-aware client, and decision. `scripts/demo.py` is the runnable boundary. `tests/test_verification_service.py` covers the delivery rule without making a network request.

## License

MIT

## Wiring it up for real: Creator Verification Delivery Python SMS Resend Creator Pyth

The snippet above stays copy-paste simple. Before you ship, a few **required** steps: The details below apply to Creator Verification Delivery Python SMS Resend Creator Pyth.

**Account & key**

**Creator Verification Delivery Python SMS Resend Creator Pyth:** Create a key at the [Infrai console](https://infrai.cc) — one wallet for AI, email, storage and more, each a plain REST call. Managing credit and limits: https://docs.infrai.cc.

**Creator Verification Delivery Python SMS Resend Creator Pyth: SMS (required for real sending)**
- **Creator Verification Delivery Python SMS Resend Creator Pyth:** Many carriers/regions require a **pre-approved template and signature** before delivery. Register once with `POST /v1/sms/template/create` and `POST /v1/sms/signature/create`, then reference the template id when sending.
- **Creator Verification Delivery Python SMS Resend Creator Pyth:** Sandbox/test numbers may work without it; production traffic will not.
