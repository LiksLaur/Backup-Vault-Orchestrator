from Crypto.Random import get_random_bytes # создание ключей из байтов
from Crypto.Cipher import AES # тк я использую алгоритм шифрования aes импортирую класс
from Crypto.Util.Padding import pad, unpad # добавление и удаления дополнения что бы их 
# длиннв была кратна размеру блока aes 16 байт

# Генерация ключа и IV Для AES-128
# При каждлм запуске генерация ключей разная поэтому надо понять 
# как на разных устройства расшифрововать код одинаково
key = get_random_bytes(16) # случайный ключ шифрования 16 байт
iv = get_random_bytes(16) # случайный вектор инициализации 16 байт


# Шифрование
cipher_encrypt = AES.new(key, AES.MODE_CBC, iv) #создание обьекта шитфрования aes, он требует 
# iv. В параметрах указывается сгенерированный ключ, метод шифрования cbc самый 
# распространненый метод, и вектор инициализации 
data = "Секретное сообщение" # само сообщение  для шифровки 
padded_data = pad(data.encode(), AES.block_size) # data.encode() преобразует строку в байы т.к. 
# шифрование работает с байтовыми данными, aes block size указывает размер блока 
# с дополнениями = 16 байтам
encrypted_data = cipher_encrypt.encrypt(padded_data) # cipher_encrypt это обьект шифрования 
# с данными сгенерированными до этого. Функция encrypt шифрует данные padded_data которые
#  уже были подготовленны к шифрованию и переведены в байты

# Важно: сохранить IV для дешифровки. Обычно его передают вместе с зашифрованными данными.
# Например, можно объединить iv и encrypted_data
encrypted_data_with_iv = iv + encrypted_data

# Дешифровка
# Извлечь IV из начала данных
iv_received = encrypted_data_with_iv[:16]  # Первые 16 байт - это IV
encrypted_data_received = encrypted_data_with_iv[16:]  # Остальное - зашифрованные данные

cipher_decrypt = AES.new(key, AES.MODE_CBC, iv_received) # создание обьекта для дешифрования 
# key и iv используются из обьекта шифрования 
decrypted_data = cipher_decrypt.decrypt(encrypted_data_received) # передаем зишифрованные 
# данные без iv 
original_data = unpad(decrypted_data, AES.block_size).decode() # удаление дополнения 

print("Зашифрованные данные (в байтах):", encrypted_data)
print("Расшифрованное сообщение:", decrypted_data)