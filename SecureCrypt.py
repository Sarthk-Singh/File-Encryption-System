import tkinter as tk #for building GUI
from tkinter import messagebox, simpledialog, filedialog # for pop-up window, file selection, and taking inputs
import imageEncDec # importing module for image encryption/decryption
import TextEncDec # importign module for image encryption/decryption
import requests # send HTTP request for connection to flask servers
import os # for handling files in the directory

def encrypt_image(): # call module for encryption of image
    try:
        imageEncDec.encrypt_image()
    except Exception as e:
        messagebox.showerror("Error", f"Encryption failed: {e}")

def decrypt_image(): # call module for decryption of image
    try:
        imageEncDec.decrypt_image()
    except Exception as e:
        messagebox.showerror("Error", f"Decryption failed: {e}")

def encrypt_text(): # call module for encryption of text file
    method = messagebox.askquestion("Encryption Type", "Use pseudo-random key?\nClick 'Yes' for pseudo-random, 'No' for random.")
    if method == "yes":
        TextEncDec.encrypt_file("pseudo")
    else:
        TextEncDec.encrypt_file("random")   

def decrypt_text(): # call module for decryption of text file
    try:
        TextEncDec.decrypt_file()
    except Exception as e:
        messagebox.showerror("Error", f"Decryption failed: {e}")

def compare_encryption(): # comparing security of both keys
    file_path = filedialog.askopenfilename(title="Select file to compare encryption") # opens a dialog ox for user to select file
    if not file_path or not os.path.exists(file_path): # if file is not selected, stops
        messagebox.showerror("Error", "File not selected or not found.")
        return

    # ask user for seed value for pseudo-random encryption (default:- pseudo123)
    seed = simpledialog.askstring("Enter Seed", "Enter seed value for pseudo-random encryption:", initialvalue="pseudo123")
    if not seed: # if key is not provided, stop
        messagebox.showwarning("Warning", "Seed value not provided.")
        return

    try:
        with open(file_path, "rb") as f: # open file in binary mode since data is sent in raw form in a POST request
            files = {'file': (os.path.basename(file_path), f)} # sents the name of the file to the server
            data = {'seed': seed}
            # sends file with seed to local flask server via POST request
            response = requests.post("http://127.0.0.1:5000/compare", files=files, data=data)
            if response.status_code == 200: # responcse code 200 indicates the request is sent successfully
                result = response.json() # parses the server's JSON response into a dictionary
                # print approprite message in the dialog box after comparison (from compare_encryption module)
                info = (
                    f"Random Key:\n"
                    f"• Entropy: {result['random']['entropy']}\n"
                    f"• Time: {result['random']['encryption_time']}s\n\n"
                    f"Pseudo-random Key:\n"
                    f"• Entropy: {result['pseudo_random']['entropy']}\n"
                    f"• Time: {result['pseudo_random']['encryption_time']}s\n\n"
                    f"{result['recommended']}"
                )
                messagebox.showinfo("Comparison Result", info)
            else:
                messagebox.showerror("Error", f"Server Error: {response.text}")
    except Exception as e:
        messagebox.showerror("Error", f"Comparison failed: {str(e)}")

def create_button(frame, text, command, color, row, col):
    btn = tk.Button(
        frame, # main frame window
        text=text, # text to display on the button
        command=command, # the function to be executed when the button is pressed
        width=25, # size of the button
        height=2,
        font=("Segoe UI", 16), 
        bg=color,
        fg="white",
        activebackground="#444", # bg colour when the button is pressed
        relief=tk.RAISED, # 3D effect when button is presssed
        bd=3 # border width
    )
    btn.grid(row=row, column=col, padx=20, pady=15) # place the at the given position in the main window in a grid layout, spaceing b/w uttona dn edges

def main():
    window = tk.Tk() # create main window of the application
    window.title("File Encryption & Analysis System")
    window.state('zoomed')  # make window in full screen mode

    window.configure(bg="#1e1e2f") # set background colour

    header = tk.Label( # create a lable as heading the GUI window
        window,
        text="File Encryption & Analysis Dashboard",
        font=("Segoe UI", 20, "bold"),
        bg="#1e1e2f",
        fg="#ffffff", # white
        pady=20
    )
    header.pack() # place the header onto the window

    # a container frame to hold different componentes like buttons, sections, etc
    content = tk.Frame(window, bg="#2e2e3f")
    # making them spaced out to avoid clustering of compenents, and allow them to grow and skrink with window size
    content.pack(pady=10, fill="both", expand=True)

    # arrange the container in a grid setup
    content.columnconfigure((0, 1), weight=1)
    content.rowconfigure((0, 1, 2), weight=1)

    # Image Section
    image_frame = tk.LabelFrame(content, text="Image Operations", bg="#2e2e3f", fg="white", font=("Segoe UI", 14, "bold"))
    image_frame.grid(row=0, column=0, padx=30, pady=20, sticky="nsew")
    # two buttons (for encryption and decryption)
    create_button(image_frame, "Encrypt Image", encrypt_image, "#4CAF50", 0, 0) # green
    create_button(image_frame, "Decrypt Image", decrypt_image, "#f44336", 0, 1) # red

    # Text Section
    text_frame = tk.LabelFrame(content, text="Text File Operations", bg="#2e2e3f", fg="white", font=("Segoe UI", 14, "bold"))
    text_frame.grid(row=1, column=0, padx=30, pady=20, sticky="nsew")
    # two buttons (for encryption and decryption)
    create_button(text_frame, "Encrypt Text File", encrypt_text, "#4CAF50", 0, 0) # green
    create_button(text_frame, "Decrypt Text File", decrypt_text, "#f44336", 0, 1) # red

    # Comparison Section
    compare_frame = tk.LabelFrame(content, text="Compare Random vs Pseudo Encryption", bg="#2e2e3f", fg="white", font=("Segoe UI", 14, "bold"))
    compare_frame.grid(row=0, column=1, rowspan=2, padx=30, pady=20, sticky="nsew")

    create_button(compare_frame, "Compare Encryption Methods", compare_encryption, "#2196F3", 0, 0) # blue

    window.mainloop() # keep the window active until user manually closes it

# only execute the this file is run directly, not when used as a module
if __name__ == "__main__":
    main()