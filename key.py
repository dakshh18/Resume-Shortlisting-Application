import secrets

# Generate a 32-byte (256-bit) secure key
secure_key = secrets.token_hex(32)

print(f"Secure key: {secure_key}")
