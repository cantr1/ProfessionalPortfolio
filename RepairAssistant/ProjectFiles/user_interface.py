import tkinter as tk
from tkinter import messagebox
from user_admin import UserAdministration
from fail_logs import RepairLog
from fail_methods import FailureMethods


class RepairApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Repair Assistant")
        self.user_admin_instance = UserAdministration()
        self.fail_logs_instance = RepairLog()
        self.fail_methods_instance = FailureMethods(repair_log=self.fail_logs_instance)

        # Define additional attributes
        self.change_password_window = None
        self.change_username_entry = None
        self.old_password_entry = None
        self.new_password_entry = None
        self.login_frame = None
        self.create_user_window = None
        self.username_entry = None
        self.active_user = None
        self.new_user_entry = None
        self.password_entry = None
        self.new_user_password_entry = None
        self.server_sn_entry = None
        self.failure_code_entry = None
        self.display_area = None

        # Create and place widgets for login
        self.create_login_widgets()

    def create_login_widgets(self):
        # Creating a frame to contain all login widgets
        self.login_frame = tk.Frame(self.root)
        self.login_frame.pack()

        # Creating labels, entry boxes, and buttons for login
        tk.Label(self.login_frame, text="Username:").pack()
        self.username_entry = tk.Entry(self.login_frame)
        self.username_entry.pack()

        tk.Label(self.login_frame, text="Password:").pack()
        self.password_entry = tk.Entry(self.login_frame, show="*")
        self.password_entry.pack()

        tk.Button(self.login_frame, text="Login", command=self.login).pack()
        tk.Button(self.login_frame, text="Change Password", command=self.show_change_password_window).pack()
        tk.Button(self.login_frame, text="Create New User", command=self.show_create_user_window).pack()

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        if self.user_admin_instance.verify_password(password, username):
            messagebox.showinfo("Login Info", "Login Successful")
            # Store the current user as an instance
            self.active_user = username
            # Destroy the widgets safely
            self.login_frame.destroy()
            # Now create the main window
            self.create_main_window()
        else:
            messagebox.showerror("Login Info", "Invalid Username or Password")
        return username

    def show_change_password_window(self):
        self.change_password_window = tk.Toplevel(self.root)
        self.change_password_window.title("Change Password")

        tk.Label(self.change_password_window, text="Username:").pack()
        self.change_username_entry = tk.Entry(self.change_password_window)
        self.change_username_entry.pack()

        tk.Label(self.change_password_window, text="Old Password:").pack()
        self.old_password_entry = tk.Entry(self.change_password_window, show="*")
        self.old_password_entry.pack()

        tk.Label(self.change_password_window, text="New Password:").pack()
        self.new_password_entry = tk.Entry(self.change_password_window, show="*")
        self.new_password_entry.pack()
        tk.Button(self.change_password_window, text="Change Password", command=self.change_password).pack()

    def change_password(self):
        user = self.change_username_entry.get()
        old_password = self.old_password_entry.get()
        new_password = self.new_password_entry.get()

        if self.user_admin_instance.verify_password(old_password, user):
            self.user_admin_instance.change_password(user, new_password)
            messagebox.showinfo("Password Change", "Password successfully changed")
            self.change_password_window.destroy()
        else:
            messagebox.showerror("Password Change", "Invalid Username or Old Password")

    def show_create_user_window(self):
        self.create_user_window = tk.Toplevel(self.root)
        self.create_user_window.title("Create New User")

        tk.Label(self.create_user_window, text="Username:").pack()
        self.new_user_entry = tk.Entry(self.create_user_window)
        self.new_user_entry.pack()

        tk.Label(self.create_user_window, text="Password:").pack()
        self.new_user_password_entry = tk.Entry(self.create_user_window, show="*")
        self.new_user_password_entry.pack()

        tk.Button(self.create_user_window, text="Create User", command=self.create_new_user).pack()

    def create_new_user(self):
        new_user = self.new_user_entry.get()
        new_password = self.new_user_password_entry.get()
        if self.user_admin_instance.add_user(new_user, new_password):
            messagebox.showinfo("User Creation", "New user created successfully")
            self.create_user_window.destroy()
        else:
            messagebox.showerror("User Creation", "Failed to create new user")

    def create_main_window(self):
        # This method sets up the main application window

        # Create and place input fields for server SN and failure code
        tk.Label(self.root, text="Server SN:").pack()
        self.server_sn_entry = tk.Entry(self.root)
        self.server_sn_entry.pack()

        tk.Label(self.root, text="Failure Code:").pack()
        self.failure_code_entry = tk.Entry(self.root)
        self.failure_code_entry.pack()

        # Create buttons for different actions
        tk.Button(self.root, text="Repair Info", command=self.retrieve_info).pack()
        # tk.Button(self.root, text="Log Failure", command=self.log_failure).pack()
        tk.Button(self.root, text="Clear Logs", command=self.clear_logs).pack()
        tk.Button(self.root, text="View Logs", command=self.view_logs).pack()
        tk.Button(self.root, text="Query Logs by Server SN", command=self.query_logs).pack()

        # Create a text widget to display information
        self.display_area = tk.Text(self.root, height=20, width=60)
        self.display_area.pack()

    def retrieve_info(self):
        # Get inputs
        server = self.server_sn_entry.get()
        failure = self.failure_code_entry.get()
        user = self.active_user

        # Use the FailureMethods class to retrieve the repair information
        repair_info = self.fail_methods_instance.get_repair_info(failure)
        if repair_info:
            self.display_area.insert(tk.END, f"Repair info for {server}: {repair_info}\n")
            # Now ask for repair confirmation and log the repair if confirmed
            if self.fail_methods_instance.log_repair(user, failure, repair_info, server):
                self.display_area.insert(tk.END, "Repair Logged Successfully\n")
            else:
                self.display_area.insert(tk.END, "Repair Log Unsuccessful\n")
        else:
            self.display_area.insert(tk.END, "No repair info found for the given failure code.\n")

    # def log_failure(self):
    #     # Get inputs
    #     server = self.server_sn_entry.get()
    #     failure = self.failure_code_entry.get()
    #     user = self.active_user
    #
    #     # Use the FailureMethods class to log the failure
    #     repair_info = self.fail_methods_instance.fail_search(failure, user, server)
    #     if repair_info:
    #         self.display_area.insert(tk.END, f"Repair info for {server}: {repair_info}\n")
    #     else:
    #         self.display_area.insert(tk.END, "No repair info found for the given failure code.\n")

    def clear_logs(self):
        # Clear the logs using the RepairLog class
        self.fail_logs_instance.clear_logs()
        self.display_area.insert(tk.END, "Logs have been cleared.\n")

    def view_logs(self):
        # Display the current logs
        logs = self.fail_logs_instance.repair_log
        self.display_area.insert(tk.END, f"Current Logs: {logs}\n")

    def query_logs(self):
        # Query the logs by server SN
        server = self.server_sn_entry.get()
        matching_logs = self.fail_logs_instance.query_logs_by_server_sn(server)
        if matching_logs:
            self.display_area.insert(tk.END, f"Matching logs for {server}: {matching_logs}\n")
        else:
            self.display_area.insert(tk.END, "No matching logs found for the given Server SN.\n")


def main():
    root = tk.Tk()
    root.geometry('800x600')
    app = RepairApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
