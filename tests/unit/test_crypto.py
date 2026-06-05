import tempfile
from pathlib import Path
from src.config.crypto import encrypt_token, decrypt_token


class TestCrypto:
    def test_encrypt_decrypt_roundtrip(self):
        with tempfile.TemporaryDirectory() as tmp:
            key_file = Path(tmp) / ".key"
            token = "ghp_1234567890abcdef"
            encrypted = encrypt_token(token, key_file)
            assert encrypted != token.encode()
            decrypted = decrypt_token(encrypted, key_file)
            assert decrypted == token

    def test_different_tokens_different_ciphertext(self):
        with tempfile.TemporaryDirectory() as tmp:
            key_file = Path(tmp) / ".key"
            t1 = encrypt_token("token_a", key_file)
            t2 = encrypt_token("token_b", key_file)
            assert t1 != t2

    def test_decrypt_with_wrong_key_fails(self):
        with tempfile.TemporaryDirectory() as tmp1, tempfile.TemporaryDirectory() as tmp2:
            key_file_1 = Path(tmp1) / ".key"
            key_file_2 = Path(tmp2) / ".key"
            token = "secret_token"
            encrypted = encrypt_token(token, key_file_1)
            import pytest
            with pytest.raises(Exception):
                decrypt_token(encrypted, key_file_2)

    def test_empty_token(self):
        with tempfile.TemporaryDirectory() as tmp:
            key_file = Path(tmp) / ".key"
            encrypted = encrypt_token("", key_file)
            decrypted = decrypt_token(encrypted, key_file)
            assert decrypted == ""
