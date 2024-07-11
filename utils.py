from passlib.hash import bcrypt

def hash_pwd(pwd):
    return bcrypt.hash(pwd)

def verify_pwd(pwd, hashed_pwd):
    return bcrypt.verify(pwd, hashed_pwd)