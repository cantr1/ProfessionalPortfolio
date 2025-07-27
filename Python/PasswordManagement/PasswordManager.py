import hashlib
import getpass

passwords ={}

def create_account():
    username = input("Enter New Username: ")
    password = getpass.getpass("Enter your password: ")
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    
    passwords[username] = hashed_password
    print("Account Created Successfully\n")

def login():
    username = input("Enter your username: ")
    password = getpass.getpass("Enter password: ")
    hashed_password = hashlib.sha256(password.encode()).hexdigest()

    if username in passwords.keys() and passwords[username] == hashed_password:
        print("Login Successful\n")
    else:
        print("Invalid username or password.")

def main():
    while True:
        choice = input("Choose: \n1-Login \n2-Create Account \n0-Exit \nInput: ")
        if choice == "1":
            login()
        elif choice == "2":
            create_account()
        elif choice == "0":
            print("Exiting program")
            break
        else:
            print("Invalid Choice")

main()