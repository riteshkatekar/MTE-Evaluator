#config.py

ENV = "local"  # ← Switch to "local" for personal Gmail testing

CONFIG = {
    "local": {
        "central_authority_email": " " # use your own mail id,
        "user_id": "me",  # Local Gmail alias
    },
    "production": {
        "central_authority_email": "", #use foundation mail id
        "user_id": "",  # Guruji Foundation account
    }
}



