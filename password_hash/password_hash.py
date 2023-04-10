import argon2

class PasswordHasher:
    def __init__(self):
        self.argon2Hasher = argon2.PasswordHasher(
        time_cost=2,
        memory_cost=64,
        parallelism=1,
        hash_len=16,
        salt_len=16,
        type=argon2.low_level.Type(2)
        )
        self.password = None
        self.hash=None
    def setPassword(self,password) -> None:
        self.password = password
    def getHash(self) -> str:
        if self.hash != None:
            return self.hash

    def Hash(self) -> None:
        self.hash = self.argon2Hasher.hash(self.password)

    def printHash(self) -> str:
        print(self.hash)

    def verify(self, password, hash_) -> bool:
        if hash_ == None:
            print("call Hash method first")
            return False
        try:
            self.argon2Hasher.verify(hash_,password)
            return True
        except argon2.exceptions.VerifyMismatchError:
            return False

"""
PasswordHasher = PasswordHasher()
PasswordHasher.setPassword("David")
PasswordHasher.Hash()
PasswordHasher.printHash()
print(PasswordHasher.verify("David",PasswordHasher.getHash()))
"""