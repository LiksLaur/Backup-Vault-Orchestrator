import bcrypt 

def create_saltpassword(password: str): 
    salt = bcrypt.gensalt() 
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt) 

    return hashed_password

def virify_saltpassword(hash_password: bytes, password: str):
    return bcrypt.checkpw(password.encode('utf-8'), hash_password) 
