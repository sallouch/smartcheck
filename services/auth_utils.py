import bcrypt

def hash_password(password: str) -> str:
    # Tronquer à 72 caractères si nécessaire
    password = password[:72]
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return hashed.decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    password = password[:72]  # même troncature à la vérification
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
