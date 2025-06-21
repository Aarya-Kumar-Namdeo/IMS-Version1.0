from tkinter import *
from billing_gui import billing_form
from tkcalendar import DateEntry
from datetime import datetime
from tkinter import messagebox
import os,sys

window = Tk()

user_name = sys.argv[1] if len(sys.argv) > 1 else 'User'

#window icon ka code hai ------------------------
icon = PhotoImage(file='images/available.png')
window.iconphoto(False, icon)
#------------------------------------------------

#yeh title aur length hai ---------------------------
window.title('Billing Application')
window.geometry('1515x768+0+0')
window.resizable(0,0)
window.config(bg='#EDE3D2')
#----------------------------------------------------

#Inventory wala title area--------------------------------------------------------------------------------------------------------------------------------------------------------
bg_image= PhotoImage(file='images/inventory.png')
titleLabel = Label(window, image=bg_image, compound=LEFT, text='Inventory Management System',font=('times new roman', 50, 'bold'), bg='#51354A', fg='white', anchor='w', padx=15)
titleLabel.place(x=0, y=0, relwidth=1)
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

#logout Wali buttton ------------------------------------------------------------------
def on_logout_enter(e):
    logoutButton.config(bg="#e74c3c", fg="white")  # Red hover

def on_logout_leave(e):
    logoutButton.config(bg="#EFE3DF", fg="black")  # Default color

def logout():
    if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
        window.destroy()
        os.system("python login.py") 

logoutButton = Button(
    window,
    text='Logout',
    font=('times new roman', 18, 'bold'),
    bg='#f0f0f0',
    fg='black',
    activebackground='#c0392b',
    activeforeground='white',
    relief='ridge',
    bd=4,
    padx=10,
    pady=5,
    cursor='hand2',command=logout
)
logoutButton.place(x=1350, y=15)

# Hover effect
logoutButton.bind("<Enter>", on_logout_enter)
logoutButton.bind("<Leave>", on_logout_leave)
#------------------------------------------------------------------------------------------------------------------------------------

# Marquee wali line----------------------------------------------------------------------------------------------------------------
def update_datetime():
    now = datetime.now()
    current_date = now.strftime("%d-%m-%Y")
    current_time = now.strftime("%I:%M:%S %p")
    subtitleLabel.config(
        text=f'\t\t\t\t\t\t\tWelcome Admin\t\t Date: {current_date}\t\t Time: {current_time}')
    window.after(1000, update_datetime)  # Update every second

subtitleLabel = Label(
    window,
    text='',  # Initial text will be set by update_datetime()
    font=('Times New Roman', 12, 'bold'),
    bg='#F5DF4D',
    fg='black',
    bd=4,
    relief='ridge',
    anchor='w',
    padx=10,
    pady=5
)
subtitleLabel.place(x=0, y=81.5, relwidth=1)
#---------------------------------------------------------------------------------------------------------------------------------------------------------

#Profile Logout ke side wali-----------------------------------------------------------------------------------------------
accountImage=PhotoImage(file='images/profile.png')
accountLabel=Label(window,image=accountImage,bg='#51354A', bd=0)
accountLabel.place(x=1250, y=10)

userLabel = Label(window, text=user_name, font=('Arial', 9, 'bold'), bg='#51354A', fg='white')
userLabel.place(x=1262, y=61)
#----------------------------------------------------------------------------------------------------------------------------

billing_form(window)
update_datetime()
window.mainloop()