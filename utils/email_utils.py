from django.core.mail import send_mail

class EmailUtils:
    def otp_verification_mail(otp, email):
        send_mail(
                        'OTP Verification',
                        f'Your Verification otp is: {otp}',
                        'no-reply@example.com',
                        [email],
                        fail_silently=False,
                    )
        