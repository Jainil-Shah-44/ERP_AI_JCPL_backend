from fastapi_mail import ConnectionConfig

conf = ConnectionConfig(
    MAIL_USERNAME="jainilshah330@gmail.com",
    MAIL_PASSWORD="kshxglkndkkdfugy",
    MAIL_FROM="jainilshah330@gmail.com",
    MAIL_PORT=587,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
)