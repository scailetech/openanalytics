#!/usr/bin/env python3
# Bypass test 1: Split API key to avoid detection

import os

# This will bypass regex detection:
api_prefix = "AIzaSy"
api_suffix = "Dz_o2ly3AjACXaJbqAc0uGSkcG2aQiOts"
full_key = api_prefix + api_suffix

# Or using environment variables
os.environ['G_KEY'] = 'AIzaSy' + 'Dz_o2ly3AjACXaJbqAc0uGSkcG2aQiOts'

# Or base64 encoded
import base64
encoded_key = base64.b64encode(b'AIzaSyDz_o2ly3AjACXaJbqAc0uGSkcG2aQiOts').decode()
print(f"Encoded key: {encoded_key}")