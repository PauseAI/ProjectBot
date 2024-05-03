KUDO_EMAIL = """🥳 Kudos to **{volunteer_name}** for sending an email to a `{target_type}`: {target_name} 🙌"""
KUDO_MEETING = """🥳 Kudos to **{volunteer_name}** for meeting with a `{target_type}`: {target_name} 🙌"""
KUDO_CALL = """🥳 Kudos to **{volunteer_name}** for calling a `{target_type}`: {target_name} 🙌"""
KUDO_MESSAGE = """🥳 Kudos to **{volunteer_name}** for sending a message to a `{target_type}`: {target_name} 🙌"""
KUDO_SNAILMAIL = """🥳 Kudos to **{volunteer_name}** for sending a snail-mail to a `{target_type}`: {target_name} 🙌"""
KUDO_OTHER = """🥳 Kudos to **{volunteer_name}** for logging their work with {target_name} 🙌"""

KUDO_TEMPLATES = {
    "email": KUDO_EMAIL,
    "meeting": KUDO_MEETING,
    "call": KUDO_CALL,
    "message": KUDO_MESSAGE,
    "snail-mail": KUDO_SNAILMAIL,
    "other": KUDO_OTHER,
}
