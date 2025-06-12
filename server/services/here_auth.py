import os
import time
import urllib.parse
from base64 import b64encode
import hmac
import hashlib
import binascii
import requests
from dotenv import load_dotenv

load_dotenv()


class TokenManager:
    def __init__(self):
        self.token = None
        self.token_expiry = 0  # Unix timestamp

    def is_token_valid(self):
        # Consider token valid if it expires in more than 2 minutes
        return self.token and (self.token_expiry - time.time() > 120)

    def get_token(self):
        if self.is_token_valid():
            return self.token
        self.token, self.token_expiry = self._fetch_new_token()
        return self.token

    def _fetch_new_token(self):
        grant_type = "client_credentials"
        oauth_consumer_key = os.getenv("HERE_ACCESS_KEY_ID")
        access_key_secret = os.getenv("HERE_ACCESS_KEY_SECRET")
        oauth_nonce = str(int(time.time() * 1000))
        oauth_timestamp = str(int(time.time()))
        oauth_signature_method = "HMAC-SHA256"
        oauth_version = "1.0"
        url = os.getenv(
            "HERE_TOKEN_ENDPOINT", "https://account.api.here.com/oauth2/token"
        )

        parameter_string = (
            f"grant_type={grant_type}"
            f"&oauth_consumer_key={oauth_consumer_key}"
            f"&oauth_nonce={oauth_nonce}"
            f"&oauth_signature_method={oauth_signature_method}"
            f"&oauth_timestamp={oauth_timestamp}"
            f"&oauth_version={oauth_version}"
        )
        encoded_parameter_string = urllib.parse.quote(parameter_string, safe="")
        encoded_base_string = (
            "POST"
            + "&"
            + urllib.parse.quote(url, safe="")
            + "&"
            + encoded_parameter_string
        )

        signing_key = access_key_secret + "&"
        oauth_signature = self.create_signature(signing_key, encoded_base_string)
        encoded_oauth_signature = urllib.parse.quote(oauth_signature, safe="")

        body = {"grant_type": grant_type}
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": (
                f'OAuth oauth_consumer_key="{oauth_consumer_key}",'
                f'oauth_nonce="{oauth_nonce}",'
                f'oauth_signature="{encoded_oauth_signature}",'
                f'oauth_signature_method="HMAC-SHA256",'
                f'oauth_timestamp="{oauth_timestamp}",'
                f'oauth_version="1.0"'
            ),
        }

        response = requests.post(url, data=body, headers=headers)
        response.raise_for_status()
        data = response.json()
        token = data["access_token"]
        expires_in = data.get("expires_in", 86400)  # Default to 24 hours
        expiry_time = time.time() + int(expires_in)
        return token, expiry_time

    @staticmethod
    def create_signature(secret_key, signature_base_string):
        encoded_string = signature_base_string.encode()
        encoded_key = secret_key.encode()
        temp = hmac.new(encoded_key, encoded_string, hashlib.sha256).hexdigest()
        byte_array = b64encode(binascii.unhexlify(temp))
        return byte_array.decode()


# import os
# import time
# import urllib.parse
# from base64 import b64encode
# import hmac
# import hashlib
# import binascii
# import requests
# from dotenv import load_dotenv

# load_dotenv()


# def create_signature(secret_key, signature_base_string):
#     encoded_string = signature_base_string.encode()
#     encoded_key = secret_key.encode()
#     temp = hmac.new(encoded_key, encoded_string, hashlib.sha256).hexdigest()
#     byte_array = b64encode(binascii.unhexlify(temp))
#     return byte_array.decode()


# def create_parameter_string(
#     grant_type,
#     oauth_consumer_key,
#     oauth_nonce,
#     oauth_signature_method,
#     oauth_timestamp,
#     oauth_version,
# ):
#     parameter_string = (
#         f"grant_type={grant_type}"
#         f"&oauth_consumer_key={oauth_consumer_key}"
#         f"&oauth_nonce={oauth_nonce}"
#         f"&oauth_signature_method={oauth_signature_method}"
#         f"&oauth_timestamp={oauth_timestamp}"
#         f"&oauth_version={oauth_version}"
#     )
#     return parameter_string


# def get_here_bearer_token():
#     grant_type = "client_credentials"
#     oauth_consumer_key = os.getenv("HERE_ACCESS_KEY_ID")
#     access_key_secret = os.getenv("HERE_ACCESS_KEY_SECRET")
#     oauth_nonce = str(int(time.time() * 1000))
#     oauth_timestamp = str(int(time.time()))
#     oauth_signature_method = "HMAC-SHA256"
#     oauth_version = "1.0"
#     url = os.getenv("HERE_TOKEN_ENDPOINT", "https://account.api.here.com/oauth2/token")

#     parameter_string = create_parameter_string(
#         grant_type,
#         oauth_consumer_key,
#         oauth_nonce,
#         oauth_signature_method,
#         oauth_timestamp,
#         oauth_version,
#     )
#     encoded_parameter_string = urllib.parse.quote(parameter_string, safe="")
#     encoded_base_string = (
#         "POST" + "&" + urllib.parse.quote(url, safe="") + "&" + encoded_parameter_string
#     )

#     signing_key = access_key_secret + "&"
#     oauth_signature = create_signature(signing_key, encoded_base_string)
#     encoded_oauth_signature = urllib.parse.quote(oauth_signature, safe="")

#     body = {"grant_type": grant_type}
#     headers = {
#         "Content-Type": "application/x-www-form-urlencoded",
#         "Authorization": (
#             f'OAuth oauth_consumer_key="{oauth_consumer_key}",'
#             f'oauth_nonce="{oauth_nonce}",'
#             f'oauth_signature="{encoded_oauth_signature}",'
#             f'oauth_signature_method="HMAC-SHA256",'
#             f'oauth_timestamp="{oauth_timestamp}",'
#             f'oauth_version="1.0"'
#         ),
#     }

#     response = requests.post(url, data=body, headers=headers)
#     response.raise_for_status()
#     return response.json()["access_token"]
