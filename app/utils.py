from passlib.context import CryptContext


def remove_word(word:str , string:str):
    words = string.split(',')
    words.remove(word)
    result = ','.join(words)
    return result


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash(password:str):
    return pwd_context.hash(password)

def verify(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)