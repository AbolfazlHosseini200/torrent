import subprocess

import requests
import socket
import threading
from tkinter import Tk, Label, Button, Entry, messagebox, filedialog, LabelFrame
from PIL import Image
import numpy as np
from tkinter.font import Font


def check(port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        sock.bind(("localhost", port))
        sock.close()
        return False
    except socket.error:
        return True

def file_receiver(my_ip, target_ip, filename):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    port_and_ip = (target_ip, 9000)
    sock.connect(port_and_ip)
    empty_port = 1
    for i in range(20001, 20006):
        if not check(i):
            empty_port = i
            break
    if empty_port == 1:
        messagebox.showerror("Error", "You don't have any free legal port!")
        return
    subprocess.run('cp ./files/' + filename + ' ./received_files', shell=True, capture_output=True, text=True)
    message = my_ip + ':' + str(empty_port) + ':' + filename
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.bind((my_ip, empty_port))
    sock.sendall(message.encode())
    message = sock.recv(1024).decode()
    messagebox.showinfo("Response", message)
    chunks = []
    dimensions_message, addr = udp_socket.recvfrom(1024)
    dimensions = dimensions_message.decode().split(':')
    rows = int(dimensions[0])
    columns = int(dimensions[1])
    udp_socket.settimeout(5.0)
    try:
        while True:
            chunk, addr = udp_socket.recvfrom(1024)
            chunks.append(chunk)
    except socket.timeout:
        data = b''.join(chunks)
        print(len(data))
        image_array = np.frombuffer(data, dtype=np.uint8).reshape((rows, columns, -1))
        image = Image.fromarray(image_array)
        image.save('./received_files/' + filename)
        print("test print")
        messagebox.showinfo("progress", "Received Completely")
        udp_socket.close()
        sock.close()


def file_sender(dest_ip, dest_port, dest_filename):
    HOST = dest_ip
    PORT = int(dest_port)
    BUFFER_SIZE = 1024
    if dest_filename.endswith('png') or dest_filename.endswith('jpg') or dest_filename.endswith(
            'jpeg')or dest_filename.endswith('JPG'):
        data = Image.open('./files/' + dest_filename)
    else:
        with open('./files/' + dest_filename, 'rb') as file:
            data = file.read()
    rows, columns, channels = np.asarray(data).shape
    data = data.tobytes()
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(f"{rows}:{columns}".encode(),(HOST,PORT))
    # print(rows, columns)
    # print(len(data))
    for i in range(0, len(data), BUFFER_SIZE):
        print(i)
        if BUFFER_SIZE+i > len(data):
            chunk = data[i:]
            sock.sendto(chunk, (HOST, PORT))
            break
        chunk = data[i:i + BUFFER_SIZE]
        sock.sendto(chunk, (HOST, PORT))
    messagebox.showinfo("progress", "Sent Completely")
    sock.close()


def listener(ip_address, tcp_handshake_port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    local_address = (ip_address, tcp_handshake_port)
    sock.bind(local_address)
    while True:
        sock.listen()
        client_sock, client_address = sock.accept()
        data = client_sock.recv(1024).decode('utf-8')
        data = data.split(':')
        print(data)
        dest_ip = data[0]
        dest_port = data[1]
        dest_filename = data[2]

        acceptance = messagebox.askyesno(
            'Connection Request',
            'A system with IP ' + client_address[
                0] + ' wants to connect and receive "' + dest_filename + '".\nDo you want to accept?'
        )

        if acceptance:
            client_sock.sendall("Done".encode())
            threading.Thread(target=file_sender, args=(dest_ip, dest_port, dest_filename)).start()
        else:
            client_sock.sendall("None".encode())
        # sock.close()
        client_sock.close()


def init_action():
    username = username_entry.get()
    data = {
        "username": username,
        "ip": ip_address
    }
    response = requests.post(init_url, json=data)
    messagebox.showinfo("HTTP Server Response", response.text)


def get_usernames_action():
    response = requests.get(get_usernames)
    messagebox.showinfo("HTTP Server Response", response.text)


def get_specific_ip_action():
    target_ip = specific_ip_entry.get()
    response = requests.get(get_ip + target_ip)
    messagebox.showinfo("HTTP Server Response", response.text)


def request_connection_action():
    target_ip = target_ip_entry.get()
    filename = filename_entry.get()
    threading.Thread(target=file_receiver, args=(ip_address, target_ip, filename)).start()


# Create the main window
root = Tk()
root.title("P2P App")

# Set a purple theme
root.configure(bg="#FFC0CB")
welcome_label = Label(root, text="Welcome", font=("Arial", 20), pady=20)
welcome_label.configure(bg="#FFC0CB", fg="green")
welcome_label.pack()

# Create the initialization frame
init_frame = LabelFrame(root, text="Initialization", font=("Arial", 16), padx=20, pady=20)
init_frame.configure(bg="#FFC0CB", fg="green")
init_frame.pack()

# Add the username input field and button
username_label = Label(init_frame, text="Username:", font=Font(family="Helvetica", size=12))
username_label.configure(bg="#FFC0CB", fg="green")
username_label.grid(row=1, column=0, padx=10, pady=10)
username_entry = Entry(init_frame, font=Font(family="Helvetica", size=12))
username_entry.grid(row=1, column=1, padx=10, pady=10)
init_button = Button(init_frame, text="Initialize", font=Font(family="Helvetica", size=12), command=init_action)
init_button.grid(row=2, column=0, columnspan=2, padx=10, pady=10)

# Create the "Get Usernames" frame
get_usernames_frame = LabelFrame(root, text="Get Usernames", font=("Arial", 16), padx=20, pady=20)
get_usernames_frame.configure(bg="#FFC0CB", fg="green")
get_usernames_frame.pack()

# Add the "Get Usernames" button
get_usernames_button = Button(get_usernames_frame, text="Get Usernames", font=Font(family="Helvetica", size=12), command=get_usernames_action)
get_usernames_button.pack(padx=10, pady=10)

# Create the "Get Specific IP" frame
get_specific_ip_frame = LabelFrame(root, text="Get IP by Username", font=("Arial", 16), padx=20, pady=20)
get_specific_ip_frame.configure(bg="#FFC0CB", fg="green")
get_specific_ip_frame.pack()

# Add the input field and button for getting IP by username
specific_ip_label = Label(get_specific_ip_frame, text="Username:", font=Font(family="Helvetica", size=12))
specific_ip_label.configure(bg="#FFC0CB", fg="green")
specific_ip_label.grid(row=1, column=0, padx=10, pady=10)
specific_ip_entry = Entry(get_specific_ip_frame, font=Font(family="Helvetica", size=12))
specific_ip_entry.grid(row=1, column=1, padx=10, pady=10)
get_specific_ip_button = Button(get_specific_ip_frame, text="Get IP", font=Font(family="Helvetica", size=12), command=get_specific_ip_action)
get_specific_ip_button.grid(row=2, column=0, columnspan=2, padx=10, pady=10)

# Create the "Request Connection" frame
request_connection_frame = LabelFrame(root, text="Request Connection", font=("Arial", 16), padx=20, pady=20)
request_connection_frame.configure(bg="#FFC0CB", fg="green")
request_connection_frame.pack()

# Add the input fields and button for requesting a file transfer
target_ip_label = Label(request_connection_frame, text="Target IP:", font=Font(family="Helvetica", size=12))
target_ip_label.configure(bg="#FFC0CB", fg="green")
target_ip_label.grid(row=1, column=0, padx=10, pady=10)
target_ip_entry = Entry(request_connection_frame, font=Font(family="Helvetica", size=12))
target_ip_entry.grid(row=1, column=1, padx=10, pady=10)
filename_label = Label(request_connection_frame, text="Filename:", font=Font(family="Helvetica", size=12))
filename_label.configure(bg="#FFC0CB", fg="green")
filename_label.grid(row=2, column=0, padx=10, pady=10)
filename_entry = Entry(request_connection_frame, font=Font(family="Helvetica", size=12))
filename_entry.grid(row=2, column=1, padx=10, pady=10)
request_connection_button = Button(request_connection_frame, text="Request Connection", font=Font(family="Helvetica", size=12),
                                    command=request_connection_action)
request_connection_button.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

# Start the listener thread
# Initialize variables
tcp_handshake_port = 10000
hostname = socket.gethostname()
ip_address = socket.gethostbyname(hostname)
init_url = 'http://127.1.1.2:8080/init'
get_usernames = 'http://127.1.1.2:8080/getAll'
get_ip = 'http://127.1.1.2:8080/getIp?username='
# ip_address = socket.gethostbyname(socket.gethostname())
# tcp_handshake_port = 12345
listen_thread = threading.Thread(target=listener, args=(ip_address, tcp_handshake_port))
listen_thread.start()

# Run the main loop
root.mainloop()