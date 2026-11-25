def send_sms(phone_number, token, counter):
    message = (
        f"SmartQ Hospital: Your Token {token} "
        f"is called. Please proceed to Counter {counter}."
    )

    return {
        "phone": phone_number,
        "message": message,
        "status": "SMS Sent Successfully"
    }