import os
import sys
import hashlib
import getpass


class UserAdministration:
    def __init__(self):
        # Store hashed usernames and their corresponding hashed passwords
        self.user_dict = {
            hashlib.sha256("kcantrell".encode()).hexdigest(): hashlib.sha256("Pass".encode()).hexdigest(),
        }

    def identify_user(self):
        """
        Asks the user for their credentials before using the application.
        """
        username_attempts = 0  # Counter for username attempts

        while username_attempts < 3:
            user = input("Please provide your username: ")
            hashed_user = hashlib.sha256(user.encode()).hexdigest()

            if hashed_user in self.user_dict:
                attempt_count = 0  # Counter for password attempts

                while attempt_count < 3:
                    password = getpass.getpass("Enter your password: ")
                    hashed_password = hashlib.sha256(password.encode()).hexdigest()

                    if self.verify_password(hashed_password, hashed_user):
                        self.clear_screen()
                        print("Login Successful!")
                        return hashed_user

                    attempt_count += 1
                    if attempt_count < 3:
                        print(f"Incorrect Password. You have {3 - attempt_count} attempts left.")
                    else:
                        self.clear_screen()
                        print("Incorrect Password")

                if attempt_count >= 3:
                    if self.request_password_change():
                        self.change_password(hashed_user)
                        return self.identify_user()  # Restart function after password change
                    else:
                        self.clear_screen()
                        print("Login Unsuccessful")
                        sys.exit()

            else:
                username_attempts += 1
                if username_attempts < 3:
                    print(f"Username not found. You have {3 - username_attempts} attempts left.")
                else:
                    self.clear_screen()
                    print("Username not found")
                    if self.request_user_creation():
                        self.add_user()
                        return self.identify_user()  # Recursive call to restart the function
                    else:
                        print("Exiting the application.")
                        sys.exit()

        return None  # Return None if the loop exits without successful login

    def verify_password(self, hashed_password, hashed_user):
        """
        Verifies the provided password against the stored password.

        Args:
            hashed_password (str): The hashed password provided by the user.
            hashed_user (str): The hashed username of the user.

        Returns:
            bool: True if the password is correct, False otherwise.
        """
        return hashed_password == self.user_dict[hashed_user]

    def change_password(self, hashed_user):
        """
        Allows the user to change their password by altering the user_dict.
        """
        new_pw = getpass.getpass("Enter your new password: ")
        new_hashed_password = hashlib.sha256(new_pw.encode()).hexdigest()
        self.user_dict[hashed_user] = new_hashed_password
        print("Your password has been changed.")

    def add_user(self):
        """
        Allows for the creation of a new user.
        """
        new_user = input("Create your username: ")
        new_user_hashed = hashlib.sha256(new_user.encode()).hexdigest()
        new_user_password = getpass.getpass("Create your password: ")
        new_user_hashed_password = hashlib.sha256(new_user_password.encode()).hexdigest()
        self.user_dict[new_user_hashed] = new_user_hashed_password
        print("Your account has been created.")

    @staticmethod
    def clear_screen():
        """Clears the terminal screen."""
        # For Windows
        if os.name == 'nt':
            os.system('cls')
        # For Unix/Linux/Mac
        else:
            os.system('clear')

    @staticmethod
    def request_password_change():
        change_request = input("Would you like to change your password? (Y/N) ")
        return change_request.upper() == "Y"

    @staticmethod
    def request_user_creation():
        creation_request = input("Would you like to create a new user? (Y/N) ")
        return creation_request.upper() == "Y"

