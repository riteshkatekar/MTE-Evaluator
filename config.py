#config.py

ENV = "local"  # ← Switch to "local" for personal Gmail testing

CONFIG = {
    "local": {
        "central_authority_email": "dadukatekar@gmail.com",
        "user_id": "me",  # Local Gmail alias
    },
    "production": {
        "central_authority_email": "monthly.thinking@gurujifoundation.in",
        "user_id": "monthly.thinking@gurujifoundation.in",  # Guruji Foundation account
    }
}


# import os

# ENV = os.getenv("ENV", "local")  # Default to production

# CONFIG = {
#     "local": {
#         "central_authority_email": os.getenv("LOCAL_EMAIL", "dadukatekar@gmail.com"),
#         "user_id": "me",
#     },
#     "production": {
#         "central_authority_email": os.getenv("PROD_EMAIL", "monthly.thinking@gurujifoundation.in"),
#         "user_id": os.getenv("PROD_EMAIL", "monthly.thinking@gurujifoundation.in"),
#     }
# }
