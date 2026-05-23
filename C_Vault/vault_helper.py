import requests
import logging

_SERVER_IP = "192.168.1.150"
_SERVER_PORT = 8080

class Entry:
    def __init__(self):
        self.entry_name = None
        self.username = None
        self.password = None
        self.action = None

    def set_entry_name(self) -> None:
        self.entry_name = input("What is the entry name: ")
    
    def set_entry_username(self) -> None:
        self.username = input("What is your username: ")

    def set_entry_pw(self) -> None:
        self.password = input("What is your password: ")
    
    def build_dict(self) -> dict:
        return {
            "entry_name": self.entry_name,
            "entry_username": self.username,
            "entry_pw": self.password,
            "action": self.action,
            "method": self.action,
        }

class VaultHelper:
    def __init__(self, logger):
        self.logger = logger
        self.crud_options = "C - Create | R - Read | U - Update | D - Delete"
        self.logger.info("Vault Helper Initialized")
    
    def get_request_type(self) -> str:
        acceptable_options = ["C", "R", "U", "D"]
        request_type = None
        while request_type not in acceptable_options:
            request_type = input(f"What action would you like to take?\n{self.crud_options}\n").upper()

            if request_type not in acceptable_options:
                print("Don't be silly...")

        # Convert the single char which is easier for user input into 
        # the format the internal API expects
        if request_type == "C":
            request_type = "CREATE"
        elif request_type == "R":
            request_type = "READ"
        elif request_type == "U":
            request_type = "UPDATE"
        elif request_type == "D":
            request_type = "DELETE"
        
        return request_type
    
    def build_entry(self) -> Entry:
        self.logger.info("Building entry to push to internal API")
        entry = Entry()
        entry.set_entry_name()
        entry.set_entry_username()
        entry.set_entry_pw()
        return entry
    
    def generate_request(self, entry: Entry) -> tuple[int, str]:
        url = f"http://{_SERVER_IP}:{_SERVER_PORT}"
        payload = entry.build_dict()

        self.logger.info(f"Beginning request to {url}")

        # track returncode
        rc = 1
        try:
            if entry.action == "CREATE":
                response = requests.post(url, json=payload, timeout=5)
            elif entry.action == "READ":
                response = requests.get(url, json=payload, timeout=5)
            elif entry.action == "UPDATE":
                response = requests.put(url, json=payload, timeout=5)
            elif entry.action == "DELETE":
                response = requests.delete(url, json=payload, timeout=5)
        except requests.RequestException as exc:
            raise VaultError(f"Request failed: ({exc})")
        except Exception as exc:
            raise
        
        if response.status_code != 200:
            raise VaultRequestError(
            f"Vault API returned {response.status_code}: {response.text}"
        )
        else:
            rc = 0

        return rc, response.text
    
    def main(self) -> None:
        entry = self.build_entry()
        entry.action = self.get_request_type()

        rc, data = self.generate_request(entry)
        if rc != 0:
            raise VaultRequestError
        
        self.logger.info(f"Recieved the following data: {data}")


class VaultError(Exception):
    """General Exception"""
    pass


class VaultRequestError(Exception):
    """Error during request process"""
    pass


def main():
    # Configure basic logger
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    logger = logging.getLogger(__name__)

    v_helper = VaultHelper(logger)
    v_helper.main()

if __name__ == "__main__":
    main()