import tkinter as tk
import re

# creates a window to display an error
def error_window(title, content):
    r = tk.Tk()
    r.resizable(0, 0)
    r.configure(bg='white', highlightbackground='black', highlightthickness=5)
    r.title('Error')
    r.geometry('400x250')
    r.overrideredirect(1)
    r.eval('tk::PlaceWindow . center')
    r.focus_force()

    # title
    tk.Label(r, text=title, font=('Century', 16), fg='red', bg='white').pack(fill=tk.X, side=tk.TOP)

    # content
    tk.Label(r, text=content, font=('Century', 12), fg='#000', bg='white').pack(fill=tk.X)

    # ok button
    tk.Button(r, text='OK', font=('Century', 12), command=lambda: r.destroy()).pack(side=tk.BOTTOM)

    r.mainloop()

# email validate using regex
def validate_email(email):
    email_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    return re.match(email_regex, email)

# password validate using regex
def validate_password(password):
    password_regex = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{8,18}$"
    return re.match(re.compile(password_regex), password)
