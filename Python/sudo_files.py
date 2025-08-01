#!/usr/bin/env python3
import os
def write_te() -> str:
    """
    :returns file_path: str - returns the file path of created file
    """
    content: str = "%qmn_sel_te_mod ALL=(ALL) ALL"
    file_path: str = "/etc/sudoers.d/te"
    with open(file_path, "w") as f:
        f.write(content)
    print("Applied sudo perms for TE...")

    return file_path

def write_it() -> str:
    """
    :returns file_path: str - returns the file path of created file
    """
    content: str = '%it_tech_mod ALL=(ALL) ALL'
    file_path: str = "etc/sudoers.d/it"
    with open(file_path, "w") as f:
        f.write(content)
    print("Applied sudo perms for IT")

    return file_path

def modify_file_perms(files: list) -> None:
    """
    :param files: list - files to modify permissions on
    This function changes the file permissions to the standard '0440'
    """
    for file in files:
        try:
            os.chmod(file, 0o440)
            print(f"Changed permissions on {file}")
        except OSError:
            print("OSError - Issues when modifying file permissions...")

def main():
    try:
        te_file: str = write_te()
        it_file: str = write_it()
        file_list = [te_file, it_file]
        modify_file_perms(file_list)
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    print("Apply Permissions")
    main()
