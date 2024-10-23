from django.utils.crypto import get_random_string


class OtpUtils:
    def six_digit_otp():
        otp = get_random_string(length=6, allowed_chars='0123456789')
        return otp