import bcrypt 

def create_saltpassword(password: str): # cоздание функции для хэширования пароля 
    salt = bcrypt.gensalt() # генерация соли для хэширования пароля
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt) # обьеденение пароля в байтах и соли 

    return hashed_password

def virify_saltpassword(hash_password: bytes, password: str):
    print(password.encode('utf-8'))
    print(hash_password)
    return bcrypt.checkpw(password.encode('utf-8'), hash_password) 

# print(create_saltpassword("123"))
print(virify_saltpassword(create_saltpassword("12323"), "124"))
print(virify_saltpassword(create_saltpassword("123"), "123"))


