from src.verification_service import VerificationRequest, process_verification


class FakeSms:
    def __init__(self):
        self.calls = []

    def events(self, message_id):
        self.calls.append(("events", message_id))
        return {"events": [{"status": "pending"}, {"status": "delivered"}]}

    def resend(self, message_id):
        self.calls.append(("resend", message_id))
        return {"message_id": message_id}


def test_delivered_creator_code_is_kept_without_duplicate_resend():
    client = FakeSms()
    job = VerificationRequest("msg-7", "subscriber-2", "asset-9", "ready")

    result = process_verification(job, client)

    assert result.action == "keep"
    assert result.delivery_state == "delivered"
    assert result.asset_id == "asset-9"
    assert client.calls == [("events", "msg-7")]
