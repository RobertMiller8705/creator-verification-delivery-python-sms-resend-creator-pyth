import os

from src.verification_service import InfraiSms, VerificationRequest, process_verification


job = VerificationRequest(
    message_id=os.environ["VERIFICATION_MESSAGE_ID"],
    subscriber_id=os.environ["SUBSCRIBER_ID"],
    asset_id=os.environ["DIGITAL_ASSET_ID"],
    content_state=os.environ.get("CONTENT_STATE", "processing"),
)
result = process_verification(job, InfraiSms())
print(result)
