from tkinter import *
from tkinter import messagebox
import os

sales_frame = None

def back_to_dashboard(current_frame, dashboard_frame):
    current_frame.place_forget()
    dashboard_frame.place(x=0, y=0, relwidth=1, relheight=1)

def show_bill(sales_list):
    sales_list.delete(0, END)
    if not os.path.exists('bills'):
        os.makedirs('bills')
    for i in os.listdir('bills'):
        if i.endswith('.txt'):
            sales_list.insert(END, i) 

def get_data(event, sales_list, sales_text):
    try:
        index_ = sales_list.curselection()
        if not index_:
            return
        file_name = sales_list.get(index_[0])
        
        # Enable text widget and clear it first
        sales_text.config(state='normal')
        sales_text.delete('1.0', END)
        
        with open(f'bills/{file_name}', 'r') as fp:
            sales_text.insert(END, fp.read())

        # Disable text widget after inserting content
        sales_text.config(state='disabled')

    except Exception as e:
        messagebox.showerror("Error", f"Unable to load file: {e}")


def search_invoice(invoice_entry, sales_list, sales_text):
    invoice_no = invoice_entry.get().strip()
    if invoice_no == "":
        messagebox.showwarning("Input Error", "Please enter an invoice number.")
        return

    files = os.listdir('bills')
    match_found = False

    for idx, file in enumerate(files):
        if file.endswith('.txt'):
            file_name_only = file[:-4]  # Remove the '.txt'
            if file_name_only == invoice_no:
                sales_list.selection_clear(0, END)
                sales_list.selection_set(idx)
                sales_list.activate(idx)
                sales_list.see(idx)
                # Load and show the bill in the text area
                try:
                    with open(os.path.join('bills', file), 'r') as fp:
                        sales_text.delete('1.0', END)
                        sales_text.insert(END, fp.read())
                    match_found = True
                    break
                except Exception as e:
                    messagebox.showerror("Error", f"Could not open the file: {e}")
                    return

    if not match_found:
        messagebox.showinfo("Not Found", f"No invoice found with number '{invoice_no}'.")


def clear_search(invoice_entry, sales_list, sales_text):
    invoice_entry.delete(0, END)
    sales_text.config(state='normal')
    sales_text.delete('1.0', END)
    sales_text.config(state='normal')
    show_bill(sales_list)

def sales_form(window, dashboard_frame):
    global sales_frame, back_icon
    if sales_frame is None or not sales_frame.winfo_exists():
        sales_frame = Frame(window, width=1515, height=650, bg='#EDE3D2')
        sales_frame.place(x=0, y=121)

        heading_label_top = Label(sales_frame, text='Manage Sales Details', font=('times new roman', 16),
                                  bg='#0F4C81', fg='white')
        heading_label_top.place(x=0, y=0, relwidth=1)

        back_icon = PhotoImage(file='images/back.png')
        back_button = Button(sales_frame, image=back_icon, bg='#EDE3D2', bd=0, cursor='hand2',
                             command=lambda: back_to_dashboard(sales_frame, dashboard_frame))
        back_button.place(x=10, y=30, width=30, height=30)

        # Left Frame
        left_frame = Frame(sales_frame, bg='white', bd=2, relief=RIDGE)
        left_frame.place(x=80, y=100)

        for i in range(4):
            left_frame.grid_columnconfigure(i, weight=1)

        heading_label_left = Label(left_frame, text='View Customer Bills', font=('times new roman', 16),
                                   bg='#0F4C81', fg='white')
        heading_label_left.grid(row=0, column=0, columnspan=4, sticky='we')

        invoice_label = Label(left_frame, text='Invoice No.', font=('times new roman', 14, 'bold'), bg='white')
        invoice_label.grid(row=1, column=0, padx=(20, 40), sticky='w')
        invoice_entry = Entry(left_frame, font=('times new roman', 14, 'bold'), bg='lightyellow', width=25)
        invoice_entry.grid(row=1, column=1, pady=20)

        search_button = Button(left_frame, text="Search", font=('times new roman', 12), width=10, cursor='hand2',
                       fg='white', bg='#0F4C81',
                       command=lambda: search_invoice(invoice_entry, sales_list, sales_text))
        search_button.grid(row=1, column=2, padx=20, pady=10)

        clear_button = Button(left_frame, text="Clear", font=('times new roman', 12), width=10, cursor='hand2',
                              fg='white', bg='#0F4C81',
                              command=lambda: clear_search(invoice_entry, sales_list, sales_text))
        clear_button.grid(row=1, column=3, padx=20, pady=10)

        # Files Frame
        files_frame = Frame(left_frame, bg='lightgray', width=250, height=250)
        files_frame.grid(row=2, column=1, pady=20, columnspan=2)

        scrollbar_files = Scrollbar(files_frame, orient=VERTICAL)
        sales_list = Listbox(files_frame, font=('times new roman', 15), bg='lightgray',
                             yscrollcommand=scrollbar_files.set)
        scrollbar_files.pack(side=RIGHT, fill=Y)
        scrollbar_files.config(command=sales_list.yview)
        sales_list.pack(fill=BOTH, expand=1)

        # Right Frame
        right_frame = Frame(sales_frame, bg='white', bd=2, relief=RIDGE)
        right_frame.place(x=840, y=100, width=580, height=390)

        heading_label_right = Label(right_frame, text='Customer Bill Area', font=('times new roman', 16),
                                    bg='#0F4C81', fg='white')
        heading_label_right.pack(side=TOP, fill=X)

        scrollbar_text = Scrollbar(right_frame, orient=VERTICAL)
        sales_text = Text(right_frame, font=('times new roman', 16), bg='lightgray',
                          yscrollcommand=scrollbar_text.set,state='disabled')
        scrollbar_text.pack(side=RIGHT, fill=Y)
        scrollbar_text.config(command=sales_text.yview)
        sales_text.pack(fill=BOTH, expand=1)

        # Bind selection to show file
        sales_list.bind('<ButtonRelease-1>', lambda event: get_data(event, sales_list, sales_text))

        show_bill(sales_list)
    else:
        sales_frame.place(x=0, y=121)
