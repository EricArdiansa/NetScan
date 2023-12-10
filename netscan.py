import socket
import tkinter as tk
from tkinter import messagebox, scrolledtext
from well_known_ports import get_well_known_ports
from PIL import Image, ImageTk
import logging


logging.basicConfig(filename='port_checker.log', level=logging.INFO, format='%(asctime)s [%(levelname)s]: %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')


def banner_grabbing(host, port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)

        sock.connect((host, port))
        sock.send(b"GET / HTTP/1.1\r\n\r\n")

        banner = sock.recv(1024).decode()
        sock.close()

        return banner
    except socket.error:
        logging.error(f"Error while grabbing banner for port {port}")
        return "Unable to grab banner"


def check_port_range(host, start_port, end_port, progress_text, open_ports_text, banner_text, well_known_ports):
    open_ports = []
    closed_ports = []

    for port in range(start_port, end_port + 1):
        progress_text.insert(tk.END, f"Checking port {port} ({well_known_ports.get(port, 'Unknown')})... ")
        progress_text.see(tk.END)
        progress_text.update()

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)

        try:
            sock.connect((host, port))
            open_ports.append(port)
            progress_text.insert(tk.END, "Open\n")
            banner = banner_grabbing(host, port)
            open_ports_text.insert(tk.END, f"Port {port} ({well_known_ports.get(port, 'Unknown')})\n")
            banner_text.insert(tk.END, f"Banner: {banner}\n")
            logging.info(f"Port {port} is open.")
        except socket.error:
            closed_ports.append(port)
            progress_text.insert(tk.END, "Closed\n")
            logging.warning(f"Port {port} is closed.")
        finally:
            sock.close()

    if open_ports:
        open_ports_text.insert(tk.END, f"\nOpen ports on {host}:\n")
        banner_text.insert(tk.END, "\nBanners:\n")
        for port in open_ports:
            service_name = well_known_ports.get(port, 'Unknown')
            open_ports_text.insert(tk.END, f"Port {port} ({service_name})\n")
    else:
        open_ports_text.insert(tk.END, "No open ports found.")
        banner_text.insert(tk.END, "No banners available.")
        logging.info("No open ports found.")


def on_check_button_click():
    host = entry_host.get()
    start_port = int(entry_start_port.get())
    end_port = int(entry_end_port.get())

    if start_port > end_port:
        messagebox.showerror("Error", "Start port must be less than or equal to end port.")
        return

    well_known_ports = get_well_known_ports()

    progress_text.delete(1.0, tk.END)
    open_ports_text.delete(1.0, tk.END)
    banner_text.delete(1.0, tk.END)

    logging.info(f"Scanning ports on host {host} from {start_port} to {end_port}")
    check_port_range(host, start_port, end_port, progress_text, open_ports_text, banner_text, well_known_ports)


app = tk.Tk()
app.title("Port Checker")
app.geometry("1270x320")

bg_color = "#191919"
app.configure(bg=bg_color)


soft_bg_color = "#F3EEEA"
entry_bg_color = "#F3EEEA"
soft_button_color = "#F3EEEA"
soft_text_color = "#191919"
hard_bg_color = "#303030"
hard_text_color = "#191919"


label_host = tk.Label(app, text="Host:", font=("Helvetica", 12), bg=soft_bg_color, fg=soft_text_color)
label_host.grid(row=0, column=0, padx=10, pady=10)

entry_host = tk.Entry(app, font=("Helvetica", 12), bg=entry_bg_color, fg=soft_text_color)
entry_host.grid(row=0, column=1, padx=10, pady=10)

label_start_port = tk.Label(app, text="Start Port:", font=("Helvetica", 12), bg=soft_bg_color, fg=soft_text_color)
label_start_port.grid(row=1, column=0, padx=10, pady=10)

entry_start_port = tk.Entry(app, font=("Helvetica", 12), bg=entry_bg_color, fg=soft_text_color)
entry_start_port.grid(row=1, column=1, padx=10, pady=10)

label_end_port = tk.Label(app, text="End Port:", font=("Helvetica", 12), bg=soft_bg_color, fg=soft_text_color)
label_end_port.grid(row=2, column=0, padx=10, pady=10)

entry_end_port = tk.Entry(app, font=("Helvetica", 12), bg=entry_bg_color, fg=soft_text_color)
entry_end_port.grid(row=2, column=1, padx=10, pady=10)

check_button = tk.Button(app, text="Check Port Range", command=on_check_button_click, font=("Helvetica", 12), bg=soft_button_color, fg=soft_text_color)
check_button.grid(row=3, column=0, columnspan=2, pady=10)

progress_text = scrolledtext.ScrolledText(app, wrap=tk.WORD, width=40, height=10, font=("Helvetica", 10), bg=entry_bg_color, fg=hard_text_color)
progress_text.grid(row=0, column=2, rowspan=4, padx=10, pady=10)

open_ports_text = scrolledtext.ScrolledText(app, wrap=tk.WORD, width=40, height=10, font=("Helvetica", 10), bg=entry_bg_color, fg=hard_text_color)
open_ports_text.grid(row=0, column=3, rowspan=4, padx=10, pady=10)

banner_text = scrolledtext.ScrolledText(app, wrap=tk.WORD, width=40, height=10, font=("Helvetica", 10), bg=entry_bg_color, fg=hard_text_color)
banner_text.grid(row=0, column=4, rowspan=4, padx=10, pady=10)


app.mainloop()