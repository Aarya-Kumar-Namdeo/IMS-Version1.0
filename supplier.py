from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import re
from employee_form import connect_database

supplier_frame = None 

def back_to_dashboard(current_frame, dashboard_frame):
    current_frame.place_forget()
    dashboard_frame.place(x=0, y=0, relwidth=1, relheight=1)

#Clear fields button function===================================================================================================================================
def clear_fields(invoice_entry,name_entry,contact_entry,description_text,treeview,check):
    invoice_entry.delete(0,END)
    name_entry.delete(0,END)
    contact_entry.delete(0,END)
    description_text.delete(1.0,END)
    if check:
        treeview.selection_remove(treeview.selection())
#======================================================================================================================================================

#Selection of Data from treeview===========================================================================================
def select_data(event,invoice_entry,name_entry,contact_entry,description_text,treeview):
    index = treeview.selection()
    content = treeview.item(index)
    row = content['values']
    clear_fields(invoice_entry,name_entry,contact_entry,description_text,treeview,False)
    invoice_entry.insert(0,row[0])
    name_entry.insert(0,row[1])
    contact_entry.insert(0,row[2])
    description_text.insert(1.0,row[3])
#========================================================================================================================================

#Update button functionality==========================================================================================================================
def update_supplier(invoice,name,contact,description,treeview):
    selected = treeview.selection()
    if not selected:
        messagebox.showerror('Error','No Selection Done!')
    else:
        cursor, connection = connect_database()
        if not cursor or not connection:
            return
        try:
            cursor.execute('USE inventory_data')
            cursor.execute('SELECT * from supplier_data WHERE invoice=%s',(invoice,))
            current_data = cursor.fetchone()
            current_data = current_data[1:4]
            new_data = (name,contact,description)

            if current_data==new_data:
                messagebox.showinfo('Information','No changes Detected')
                return
            cursor.execute('''UPDATE supplier_data SET name=%s, contact=%s, description=%s WHERE invoice=%s''', 
                            (name,contact,description,invoice))
            connection.commit()
            treeview_data(treeview)
            messagebox.showinfo('Success','Data Updated Successfully!')
        except Exception as e:
            messagebox.showerror('Error',f'Error due to {e}')
        finally:
            cursor.close()
            connection.close()
#========================================================================================================================================================

#Delete button function==============================================================================================================
def delete_supplier(invoice,invoice_entry, name_entry, contact_entry, description_text, treeview):
    selected = treeview.selection()
    if not selected:
        messagebox.showerror('Error', 'No Selection Done!')
        return

    result = messagebox.askyesno('Confirm', 'Do you really want to delete the record?')
    if result:
        try:
            cursor, connection = connect_database()
            if not cursor or not connection:
                return
            cursor.execute('USE inventory_data')
            cursor.execute('DELETE FROM supplier_data WHERE invoice=%s', (invoice,))
            connection.commit()
            treeview_data(treeview)
            clear_fields(invoice_entry, name_entry, contact_entry, description_text, treeview, True)
            messagebox.showinfo('Success', 'Data deleted successfully!')
        except Exception as e:
            messagebox.showerror('Error', f'Error due to {e}')
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
#===================================================================================================================================================

#Treeview DAta=========================================================================================
def treeview_data(treeview):
    cursor, connection = connect_database()
    if not cursor or not connection:
        return
    try:
        cursor.execute('USE inventory_data')
        cursor.execute('SELECT * from supplier_data')
        records = cursor.fetchall()
        treeview.delete(*treeview.get_children())
        for record in records:
            treeview.insert('', END, values=record)

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
#=============================================================================================================================

#Add button function================================================================================================
def add_supplier(invoice, name, contact, description, treeview):
    try:
        try:
            invoice = int(invoice)
        except ValueError:
            messagebox.showerror('Invalid Input', 'Invoice number must be an integer!')
            return

        if not name.strip() or not re.fullmatch(r"[A-Za-z\s\.\'\-]+", name.strip()):
            messagebox.showerror('Invalid Name', 'Name must contain only letters, spaces, dots, apostrophes, or hyphens!')
            return

        if not re.fullmatch(r'\d{10}', contact.strip()):
            messagebox.showerror('Invalid Contact', 'Contact number must be exactly 10 digits!')
            return

        if not description.strip():
            messagebox.showerror('Invalid Description', 'Description cannot be empty!')
            return

        # === CONNECT TO DATABASE ===
        cursor, connection = connect_database()
        if not cursor or not connection:
            messagebox.showerror('Database Error', 'Could not connect to the database!')
            return

        cursor.execute('CREATE DATABASE IF NOT EXISTS inventory_data')
        cursor.execute('USE inventory_data')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS supplier_data (
                invoice INT PRIMARY KEY,
                name VARCHAR(100),
                contact VARCHAR(15),
                description TEXT
            )
        ''')

        # === CHECK FOR DUPLICATES ===
        cursor.execute('SELECT * FROM supplier_data WHERE invoice=%s OR contact=%s', (invoice, contact))
        if cursor.fetchone():
            messagebox.showerror('Duplicate Entry', 'Supplier with same Invoice or Contact already exists!')
            return

        # === INSERT DATA ===
        cursor.execute('INSERT INTO supplier_data VALUES (%s, %s, %s, %s)',
                       (invoice, name.strip(), contact.strip(), description.strip()))
        connection.commit()

        # === REFRESH TREEVIEW ===
        treeview_data(treeview)
        messagebox.showinfo('Success', 'Supplier added successfully!')

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
#================================================================================================================================

#=Search button function====================================================================================================
def search_supplier(search_value, treeview):
    if search_value == '':
        messagebox.showerror('Error', 'Enter the Invoice No. to Search')
        return

    cursor, connection = connect_database()
    if not cursor or not connection:
        return

    try:
        cursor.execute('USE inventory_data')
        cursor.execute('SELECT * FROM supplier_data WHERE invoice = %s', (search_value,))
        record = cursor.fetchone()

        if not record:
            messagebox.showerror('Error', 'No Record Found!')
        else:
            treeview.delete(*treeview.get_children())
            treeview.insert('', END, values=record)

    except Exception as e:
        messagebox.showerror('Error', f'Error due to {e}')
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

#=======================================================================================================================

#Show all button function============================================================
def show_all(search_entry,treeview):
    treeview_data(treeview)
    search_entry.delete(0,END)
#==================================================================================


#Gui supplier===========================================================================================================================
def supplier_form(window,dashboard_frame):
    global back_icon, supplier_frame,treeview
    if supplier_frame is None or not supplier_frame.winfo_exists():
        supplier_frame = Frame(window,dashboard_frame,  width=1515, height=650, bg='#EDE3D2')
        supplier_frame.place(x=0, y=121)

        headingLabel = Label(supplier_frame, text='Manage Supplier Details', font=('times new roman', 16), bg='#0F4C81', fg='white')
        headingLabel.place(x=0, y=0, relwidth=1)

        back_icon = PhotoImage(file='images/back.png')
        back_button = Button(supplier_frame, image=back_icon, bg='#EDE3D2',bd=0, cursor='hand2',
                             command=lambda:back_to_dashboard(supplier_frame, dashboard_frame))
        back_button.place(x=10, y=30,width=30,height=30)
    

        left_frame = Frame(supplier_frame,bg='#EDE3D2')
        left_frame.place(x=200,y=110)

        invoice_label = Label(left_frame,text='Invoice No.',font=('times new roman',14,'bold'),bg='#EDE3D2')
        invoice_label.grid(row=0,column=0,padx=(20,40),sticky='w')
        invoice_entry = Entry(left_frame,font=('times new roman',14,'bold'),bg='white')
        invoice_entry.grid(row=0,column=1)

        name_label = Label(left_frame,text='Supplier Name',font=('times new roman',14,'bold'),bg='#EDE3D2')
        name_label.grid(row=1,column=0,padx=(20,40),pady=25,sticky='w')
        name_entry = Entry(left_frame,font=('times new roman',14,'bold'),bg='white')
        name_entry.grid(row=1,column=1)

        contact_label = Label(left_frame,text='Supplier Contact',font=('times new roman',14,'bold'),bg='#EDE3D2')
        contact_label.grid(row=2,column=0,padx=(20,40),sticky='w'),
        contact_entry = Entry(left_frame,font=('times new roman',14,'bold'),bg='white')
        contact_entry.grid(row=2,column=1)

        description_label = Label(left_frame,text='Description',font=('times new roman',14,'bold'),bg='#EDE3D2')
        description_label.grid(row=3,column=0,padx=(20,40),sticky='nw',pady=25)
        description_text = Text(left_frame,width=25,height=6,bd=2)
        description_text.grid(row=3,column=1,pady=25)

        button_frame= Frame(left_frame,bg='#EDE3D2')
        button_frame.grid(row=4,columnspan=2,pady=30)

        add_button = Button(button_frame, text="Add",font=('times new roman',12 ),width=10,cursor='hand2',fg='white',bg='#0F4C81',
                            command=lambda:add_supplier(invoice_entry.get(),name_entry.get(),contact_entry.get(),
                                                        description_text.get(1.0,END),treeview))
        add_button.grid(row=0, column=1, padx=20)

        update_button = Button(button_frame, text="Update",font=('times new roman',12 ),width=10,cursor='hand2',fg='white',bg='#0F4C81',
                               command=lambda:update_supplier(invoice_entry.get(),name_entry.get(),contact_entry.get()
                                                              ,description_text.get(1.0,END).strip(),treeview))
        update_button.grid(row=0, column=2)

        delete_button = Button(button_frame, text="Delete", font=('times new roman', 12), width=10, cursor='hand2', fg='white', bg='#0F4C81',
                       command=lambda: delete_supplier(invoice_entry.get(), invoice_entry, name_entry, contact_entry, description_text,treeview))

        delete_button.grid(row=0, column=3,padx=20)

        clear_button = Button(button_frame, text="Clear",font=('times new roman',12 ),width=10,cursor='hand2',fg='white',bg='#0F4C81',
                              command=lambda: clear_fields(invoice_entry, name_entry, contact_entry, description_text,treeview,True))
        clear_button.grid(row=0, column=4)

        right_frame = Frame(supplier_frame,bg='#EDE3D2')
        right_frame.place(x=800,y=95,width=580,height=390)

        search_frame =Frame(right_frame,bg='#EDE3D2')
        search_frame.pack(pady=(0,10))

        num_label = Label(search_frame,text='Invoice No.',font=('times new roman',14,'bold'),bg='#EDE3D2')
        num_label.grid(row=0,column=0,padx=10,sticky='w')
        search_entry = Entry(search_frame,font=('times new roman',14,'bold'),bg='white',width=15)
        search_entry.grid(row=0,column=1)

        search_button = Button(search_frame, text="Search",font=('times new roman',12 ),width=10,cursor='hand2',fg='white',bg='#0F4C81',
                               command=lambda:search_supplier(search_entry.get(),treeview))
        search_button.grid(row=0, column=2,padx=20)

        show_button = Button(search_frame, text="Show All",font=('times new roman',12 ),width=10,cursor='hand2',fg='white',bg='#0F4C81',
                             command=lambda:show_all(search_entry,treeview))
        show_button.grid(row=0, column=3)

        horizontal_scrollbar = Scrollbar(right_frame, orient=HORIZONTAL)
        vertical_scrollbar = Scrollbar(right_frame, orient=VERTICAL)

        treeview = ttk.Treeview(right_frame,columns=('invoice','name','contact','description'), show='headings',yscrollcommand=vertical_scrollbar.set,
                                                            xscrollcommand=horizontal_scrollbar.set)
        
        horizontal_scrollbar.pack(side=BOTTOM,fill=X)
        vertical_scrollbar.pack(side=RIGHT,fill=Y)
        horizontal_scrollbar.config(command=treeview.xview)
        vertical_scrollbar.config(command=treeview.yview)
        
        treeview.pack(fill=BOTH,expand=1)

        treeview.heading('invoice',text='Invoice ID')
        treeview.heading('name',text='Supplier Name')
        treeview.heading('contact',text='Supplier Contact')
        treeview.heading('description',text='Description')

        treeview.column('invoice',width=80)
        treeview.column('name',width=160)
        treeview.column('contact',width=120)
        treeview.column('description',width=300)

        treeview_data(treeview)
    
        treeview.bind('<ButtonRelease-1>',lambda event:select_data(event,invoice_entry,name_entry,contact_entry
                                                                   ,description_text,treeview))
    else:
        supplier_frame.place(x=0, y=121)


    