from fastapi import FastAPI, HTTPException
from typing import List
from pydantic import BaseModel
from passlib.context import CryptContext
import jwt

class Payload(BaseModel):
    numbers: List[int]


class BinarySearchPayload(BaseModel):
    numbers: List[int]
    target: int

fake_db = {"users": {}}

SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(data: dict):
    to_encode = data.copy()
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    print(plain_password, hashed_password)
    return pwd_context.verify(plain_password, hashed_password)


app = FastAPI()


class Credentials(BaseModel):
    username: str
    password: str

#//implemetar un endopoint como metodo post para crear un usuario
#//entrada:{"username":"user1","password":"password1"} salida:{"message":"user created"}
#//status code: 200 Registro exitoso 400:El usuario ya existe

@app.post("/register")
def register(payload: Credentials):
    username = payload.username
    password = payload.password

    if username in fake_db["users"].keys():
        raise HTTPException(status_code=400, detail="User already exists")
    hashed_password = get_password_hash(password)
    fake_db["users"][username] = {"password": hashed_password}
    return {"message": "User registered successfully"}


#Ruta /login metodo post entrada {"username":"user1","password":"pass1"} salida{"access_token:<token_de_acceso>"}
#status code 200 login exitoso 401 Credenciales invalidas
@app.post("/login")
def login(payload: Credentials):
    username = payload.username
    password = payload.password

    if username not in fake_db["users"]:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    user = fake_db["users"][username]
    if not verify_password(password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token(data={"sub": username})
    return {"access_token": access_token}

#funcion para verificar el token
def get_current_user(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=401, detail="Invalid authentication credentials"
            )
        if username not in fake_db["users"].keys():
            raise HTTPException(
                status_code=401, detail="Invalid authentication credentials"
            )
    except:
        raise HTTPException(
            status_code=401, detail="Invalid authentication credentials"
        )
    
#// ruta bubble_sort metodo post entrada {"numbers":[1,2,3,4,5]} salida {"sorted_numbers":[1,2,3,4,5]}
# agregar en el endopoint la validacion del token
#//agregar en el endopoint la validacion del token
@app.post("/bubble-sort")
def bubble_sort(payload: Payload,token: str):

    get_current_user(token)  
    numbers = payload.numbers
    n = len(numbers)
    for i in range(n):
        for j in range(0, n - i - 1):
            if numbers[j] > numbers[j + 1]:
                numbers[j], numbers[j + 1] = numbers[j + 1], numbers[j]
    return {"numbers": numbers}

# Ruta /filter-even metodo post
#descripcion recibe una lista de numeros y devuelve unicamente aquellos que son pares
# Input: {number:[list of numbers]}
# This is the input format for the endpoint that receives a list of numbers.
#entrada {number:[lista de numeros]}
#salida {even_numbers:[lista de numeros pares]}
#solicitar el token que se genera cuando me logeoº
@app.post("/filter-even")
def filter_even(payload: Payload,token:str):
    #agregar la funcion para validar el token
    get_current_user(token)
    numbers = payload.numbers
    even_numbers = [num for num in numbers if num % 2 == 0]
    return {"even_numbers": even_numbers}   

#Ruta /sum-elements
# metodo post
# Descripcion Recibe una lista de numeros y devuelve la suma de sus elementos
#Entrada {"numbers":[liusta de numeros]}
#Salida {sum:int}
#agregar funcion para verificar el token

@app.post("/sum-elements")
#agregar funcion para verificar el token
def sum_elements(payload: Payload,token:str):
    get_current_user(token)
    numbers = payload.numbers
    return {"sum":sum(numbers)}

#Ruta /max-value
#metodo post
#Descripcion Recibe una lista de numeros y devuelve el valor maximo
#Entrada {"numbers":[lista de numeros]}
#Salida {max_value:int}
#agregar funcion para verificar el token
@app.post("/max-value")
def max_value(payload: Payload,token:str):
    get_current_user(token)
    numbers = payload.numbers
    return {"max": max(numbers)}
#ruta /binary-search
#metodo post
#Descripcion Recibe una lista de numeros ordenados y un numero objetivo, y devuelve la posicion del numero objetivo en la lista
#Entrada {"numbers":[lista de numeros ordenados],"target":int}
#Salida {"found":booleano ,"index":int}
#agregar funcion para verificar token
@app.post("/binary-search")
def binary_search(payload: BinarySearchPayload, token: str):
    user = get_current_user(token)  # Valida el token
    numbers = payload.numbers
    target = payload.target

    left, right = 0, len(numbers) - 1
    while left <= right:
        mid = (left + right) // 2
        if numbers[mid] == target:
            return {"found": True, "index": mid}
        elif numbers[mid] < target:
            left = mid + 1
        else:
            right = mid - 1

    return {"found": False, "index": -1}