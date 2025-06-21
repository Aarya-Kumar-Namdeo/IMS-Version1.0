from tkinter import *
from tkinter import messagebox
from employee_form import connect_database
import os,sys

import subprocess

window = Tk()

window_width = 650
window_height = 750

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS  # PyInstaller's temp path
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

#Window Ka size====================================================================================
# Get screen size
screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()

# Calculate position x, y to center the window
x = (screen_width // 2) - (window_width // 2)
y = (screen_height // 2) - (window_height // 2) - 40 

# Set the geometry using the calculated x and y
window.geometry(f'{window_width}x{window_height}+{x}+{y}')

# Window settings
window.title('Login System')
window.resizable(0, 0)
window.config(bg='#EDE3D2')

# Icon
icon = PhotoImage(file=resource_path('images/available.png'))
window.iconphoto(False, icon)

bg_image = PhotoImage(file=resource_path('images/background.png'))  
bg_label = Label(window, image=bg_image)
bg_label.place(x=0, y=0, relwidth=1, relheight=1)


def login_action(user_entry, password_entry, terms_var):
    username = user_entry.get().strip()
    password = password_entry.get().strip()

    if not username or not password:
        messagebox.showwarning("Input Error", "Please enter both Employee ID and Password.")
        return

    if not terms_var.get():
        messagebox.showwarning("Terms & Conditions", "Please accept the Terms and Conditions to proceed.")
        return

    cursor, connection = connect_database()
    if not cursor or not connection:
        return

    try:
        cursor.execute('USE inventory_data')
        query = "SELECT usertype, name FROM employee_data WHERE empid = %s AND password = %s"
        cursor.execute(query, (username, password))
        result = cursor.fetchone()

        if result:
            usertype = result[0].lower()
            emp_name = result[1]

            messagebox.showinfo("Login Success", f"Welcome, {emp_name}!")
            window.destroy()  # Close login window

            # Determine script path
            if usertype == "admin":
                script_path = resource_path("dashboard.py")
            elif usertype == "employee":
                script_path = resource_path("billing.py")
            else:
                messagebox.showerror("Error", f"Unknown employment type: {usertype}")
                return

            # Launch the script with Python executable and emp_name argument
            subprocess.Popen([sys.executable, script_path, emp_name])
        else:
            messagebox.showerror("Login Failed", "Invalid Employee ID or Password.")

    except Exception as e:
        messagebox.showerror('Error', f'Error occurred: {e}')
    finally:
        try:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
        except:
            pass



#========================================================================================================================
def login_gui():
    global log_icon, bg_login_image, brand_icon_image
    brand_frame = Frame(window, width=450, height=100,bd=5,relief=RIDGE)
    brand_frame.place(x=95, y=10)

    brand_icon_image = PhotoImage(file=resource_path('images/Brand2.png'))  
    brand_icon_label = Label(brand_frame, image=brand_icon_image)
    brand_icon_label.place(x=30, y=10)

    brand_label = Label(brand_frame, text='Akiya Inventory\nSolutions', font=('Elephant', 25, 'bold'), bg="white", fg='#0F4C81')
    brand_label.place(x=125, y=0)

    login_frame = Frame(window, width=500, height=600,bd=5,relief=RIDGE)
    login_frame.place(relx=0.5, rely=0.56, anchor='center')

    bg_login_image = PhotoImage(file=resource_path('images/login ground.png'))  
    bg_login_label = Label(login_frame, image=bg_login_image)
    bg_login_label.place(x=0, y=0, relwidth=1, relheight=1)

    log_icon= PhotoImage(file=resource_path('images/user.png'))
    log_icon_label = Label(login_frame, image=log_icon, bg='#EDE3D2')
    log_icon_label.place(x=175,y=35)

    user_label = Label(login_frame, text='Employee ID', font=('times new roman', 18,'bold'), bg='#EDE3D2', fg='black')
    user_label.place(x=90,y=200)
    user_entry = Entry(login_frame,font=('times new roman',15),bg='lightgray',width=30)
    user_entry.place(x=90,y=240)

    password_label = Label(login_frame, text='Password', font=('times new roman', 18,'bold'), bg='#EDE3D2', fg='black')
    password_label.place(x=90,y=280)
    password_entry = Entry(login_frame,font=('times new roman',15),bg='lightgray',width=30)
    password_entry.place(x=90,y=320)

    terms_var = IntVar()
    terms_checkbox = Checkbutton(login_frame, text="I accept the Terms and Conditions", variable=terms_var,
                                 bg='#EDE3D2', font=('times new roman', 12), fg='black',
                                 activebackground='#EDE3D2', activeforeground='black', cursor='hand2')
    terms_checkbox.place(x=90, y=360)

    login_button = Button(login_frame, text='Log In', font=('Arial Rounded MT Bold',15),bg='#0F4C81',fg='white',
                          activebackground='#0F4C81',activeforeground='white',cursor='hand2',
                          command=lambda:login_action(user_entry,password_entry,terms_var))
    login_button.place(x=90,y=400,height=35,width=300)

    hr_label = Label(login_frame, bg='gray')
    hr_label.place(x=90,y=470,width=300,height=2)

    or_label = Label(login_frame,text='OR',font=('times new roman',15,'bold'),fg='black',bg='#EDE3D2')
    or_label.place(x=220,y=455)

    forget_button = Button(login_frame,text="Forget Password ?",font=('times new roman',13),bg='#EDE3D2',fg="#0F4C81",bd=0,
                           activebackground='#EDE3D2',activeforeground='#0F4C81',cursor='hand2')
    forget_button.place(x=175,y=500)



login_gui()
window.mainloop()