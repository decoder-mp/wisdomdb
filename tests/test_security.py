import unittest

from core.security import hash_password, verify_password


class SecurityTests(unittest.TestCase):
    def test_password_hash_roundtrip_with_long_password(self):
        password = "a" * 100
        hashed_password = hash_password(password)
        self.assertTrue(verify_password(password, hashed_password))


if __name__ == "__main__":
    unittest.main()
