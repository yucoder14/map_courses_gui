#! /usr/bin/python3 
import tkinter as tk
from tkinter import messagebox

from ldap3 import ALL, Connection, Server
from ldap3.core.exceptions import LDAPException 

import os 
import subprocess

def create_secret_file(username, password): 
    filename = f"/home/{username}/.credential"
    try: 
        with open(filename, 'w') as file:
            file.write(f"username={username}\n")
            file.write(f"password={password}\n")

        os.chmod(filename, 0o600)
    except IOError as e: 
        print("Error: ", e)
        exit(1)
    except Exception as e:
        print("Error: ", e)
        exit(69)

def mount_course(username): 
    remote_path = "//courses.ads.carleton.edu/courses"
    local_path = f"/home/{username}/COURSES"
    get_uid = subprocess.run(["id", "-u", username], capture_output=True, text=True) 
    uid = get_uid.stdout

    os.makedirs(local_path, exist_ok=True)

    command = [ 
        "sudo", "/sbin/mount.cifs", remote_path, local_path,
        "-o", f"username=/home/{username}/.credentials,uid={uid},gid={uid},vers=2.0"
    ]

    subprocess.run(command)
    

def validate_login():
    userid = username_entry.get()
    password = password_entry.get()
   
    server = Server("ldaps://ldap.its.carleton.edu", get_info=ALL)
    base_dn = "ou=People,dc=carleton,dc=edu"
    user_dn = f"carlNetId={userid},{base_dn}"
    
    try: 
        conn = Connection(server, user=user_dn, password=password)
        conn.bind()
        if conn.result['description'] == "success":
            create_secret_file(userid, password)
            mount_course(userid) 
            os.remove(f"/home/{userid}/.credential")
            messagebox.showinfo("Login Successful", f"Welcome, {userid}!")
            exit(0)
        else:
            messagebox.showerror("Login Failed", "Invalid username or password")
    except LDAPException: 
        messagebox.showerror("LDAP Failed", "Unable to connect to LDAP server")

# Create the main window
my_width = 350
my_height = 100
root = tk.Tk()
root.title("Map COURSES")
root.geometry(f"{my_width}x{my_height}")
root.resizable(False, False)
root.grid_columnconfigure(0, weight=1) # Left "empty" column
root.grid_columnconfigure(1, weight=0) # Column with widget (optional, default is 0)
root.grid_columnconfigure(2, weight=1) # Right "empty" column
root.grid_rowconfigure(0, weight=1) # Left "empty" row
root.grid_rowconfigure(1, weight=0) # Column with widget (optional, default is 0)
root.grid_rowconfigure(2, weight=1) # Right "empty" row

content_padx = 10
content_pady = 10
content = tk.Frame(root)

box_padx = 5
box_pady = 5
user_box = tk.Frame(content)
user_box.grid_columnconfigure(0, weight=1)
user_box.grid_rowconfigure(0, weight=1)

password_box = tk.Frame(content)
password_box.grid_columnconfigure(0, weight=1)
password_box.grid_rowconfigure(0, weight=1)

# Create and place the username label and entry
username_label = tk.Label(user_box, text="Username")
username_entry = tk.Entry(user_box)

# Create and place the password label and entry
password_label = tk.Label(password_box, text="Password")
password_entry = tk.Entry(password_box, show="*")  # Show asterisks for password

# Create and place the login button
login_button = tk.Button(content, text="Login", command=validate_login)
content.grid(column=1, row=1, padx=content_padx, pady=content_pady)
user_box.grid(column=0, row=0, padx=box_padx, pady=(box_pady, 0),sticky="nwes")
username_label.grid(column=0, row=0, padx=(0, 5), sticky="nwes")
username_entry.grid(column=1, row=0, sticky="nwes")
password_box.grid(column=0, row=1, padx=box_padx, pady=box_pady, sticky="nwes")
password_label.grid(column=0, row=0, padx=(0, 5), sticky="nwes")
password_entry.grid(column=1, row=0, sticky="nwes")
login_button.grid(column=1, row=0, rowspan=2, sticky="nwes", padx=5, pady=5)


# Start the Tkinter event loop
root.mainloop() 
