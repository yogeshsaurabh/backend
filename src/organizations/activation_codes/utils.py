import secrets
import string


def generate_otp() -> str:
    """Generate an OTP for each student for manual activation, OTP need not be strictly unique
    since OTP can be entered only by the logged-in user and not by any other user.

    An OTP must contain
    * at least one lower case character
    * at least one upper case character
    * at least three digits

    Returns:
        str: random 10 character cryptographically secure OTP.
    """

    alphabet: str = string.ascii_letters + string.digits
    otp_length = 10
    otp: str = ""

    while True:
        otp = "".join(secrets.choice(alphabet) for _ in range(otp_length))
        if (
                any(c.islower() for c in otp)
                and any(c.isupper() for c in otp)
                and sum(c.isdigit() for c in otp) >= 3
        ):
            return otp
