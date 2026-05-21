import requests
import logging

class Entry:
    def __init__(self):
        self.entry_name = None
        self.entry_username = None
        self.entry_pw = None

    def set_entry_name(self) -> None:
        self.name = input("What is the entry name: ")
    
    def set_entry_username(self) -> None:
        self.username = input("What is your username: ")

    def set_entry_pw(self) -> None:
        self.password = input("What is your password: ")

class VaultHelper:
    def __init__(self, logger):
        self.logger = logger
        self.crud_options = "C - Create | R - Read | U - Update | D - Delete"
    
    def get_request_type(self) -> int:
        acceptable_options = ["C", "R", "U", "D"]
        request_type = input(f"What action would you like to take?\n{self.crud_options}\n")

        if request_type.lower() not in acceptable_options:
            raise VaultError
        
        rc = self.generate_request(request_type)
        if rc != 0:
            raise VaultRequestError
        
        return 0
    
    def build_entry(self) -> Entry:
        entry = Entry()
        entry.set_entry_name()
        entry.set_entry_username()
        entry.set_entry_pw()
        return entry
        
        
        


class VaultError(Exception):
    """General Exception"""
    pass

class VaultRequestError(Exception):
    """Error during request process"""
    pass