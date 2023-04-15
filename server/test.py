from argon2 import PasswordHasher



def hash2():
    Ph = PasswordHasher()
    password = Ph.hash("David")
    return password


def verify():
    Ph = PasswordHasher()
    if Ph.verify(hash2(),"David"):
        print("hejz")

hash2()
verify()