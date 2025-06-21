from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import re
from employee_form import connect_database

product_frame = None


def fetch_supplier_category(category_combobox,supplier_combobox):
    category_option = []
    supplier_option = []
    cursor,connection = connect_database()
    if not cursor or not connection:
        return
    cursor.execute('USE inventory_data')
    cursor.execute('SELECT name from category_data')
    names = cursor.fetchall()
    if len(names) > 0:
        category_combobox.set('Select')
        for name in names:
            category_option.append(name[0])
        category_combobox.config(values=category_option)

    cursor.execute('SELECT name from supplier_data')
    names = cursor.fetchall()
    if len(names) > 0:
        supplier_combobox.set('Select')
        for name in names:
            supplier_option.append(name[0])
        supplier_combobox.config(values=supplier_option)


def back_to_dashboard(current_frame, dashboard_frame):
    current_frame.place_forget()
    dashboard_frame.place(x=0, y=0, relwidth=1, relheight=1)

#Treeview DAta=========================================================================================
def treeview_data(treeview):
    cursor, connection = connect_database()
    if not cursor or not connection:
        return
    try:
        cursor.execute('USE inventory_data')
        cursor.execute('SELECT * from product_data')
        records = cursor.fetchall()
        treeview.delete(*treeview.get_children())
        for record in records:
            treeview.insert('', END, values=record)
        cursor.execute('DELETE FROM product_data WHERE quantity = 0')
        connection.commit()

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
#===============================================================

#Selection of Data from treeview===========================================================================================
def select_data(event,category_combobox,supplier_combobox,name_entry,price_entry,quantity_entry,status_combobox,treeview):
    index = treeview.selection()
    if not index:
        return
    content = treeview.item(index)
    values = content['values']
    clear_fields(category_combobox,supplier_combobox,name_entry,price_entry,quantity_entry,status_combobox,treeview,False)
    category_combobox.set(values[1])
    supplier_combobox.set(values[2])
    name_entry.insert(0, values[3])
    price_entry.insert(0, values[4])
    quantity_entry.insert(0, values[5])
    status_combobox.set(values[6])
#========================================================================================================================================

#Clear fields button function===================================================================================================================================
def clear_fields(category_combobox,supplier_combobox,name_entry,price_entry,quantity_entry,status_combobox,treeview,check):
    name_entry.delete(0, END)
    price_entry.delete(0, END)
    quantity_entry.delete(0, END)
    category_combobox.set('Select')
    supplier_combobox.set('Select')
    status_combobox.set('Select Status')
    
    if check:
        treeview.selection_remove(treeview.selection())
#======================================================================================================================================================

#Add button function================================================================================================
def add_product(category, supplier, name, price, quantity, status, treeview):
    try:
        # === VALIDATIONS ===
        if category == 'Empty':
            messagebox.showerror('Error', "Please add a category.")
            return

        if supplier == 'Empty':
            messagebox.showerror('Error', "Please add a supplier.")
            return

        if category == 'Select' or supplier == 'Select' or not name.strip() or not price.strip() or not quantity.strip() or status == 'Select Status':
            messagebox.showerror('Error', "All fields are required!")
            return


        if not re.fullmatch(r'\d+(\.\d{1,2})?', price.strip()):
            messagebox.showerror('Invalid Price', 'Price must be a valid number')
            return

        if not quantity.strip().isdigit():
            messagebox.showerror('Invalid Quantity', 'Quantity must contain only digits.')
            return

        # === CONNECT TO DATABASE FIRST ===
        cursor, connection = connect_database()
        if not cursor or not connection:
            messagebox.showerror('Database Error', 'Could not connect to the database!')
            return

        cursor.execute('CREATE DATABASE IF NOT EXISTS inventory_data')
        cursor.execute('USE inventory_data')

        # === CREATE TABLE IF NOT EXISTS ===
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS product_data (
                id INT AUTO_INCREMENT PRIMARY KEY,
                category VARCHAR(100),
                supplier VARCHAR(100),
                name VARCHAR(100),
                price DECIMAL(10,2),
                quantity INT,
                status VARCHAR(50)
            )
        ''')

        # === CHECK FOR DUPLICATES ===
        cursor.execute('SELECT * FROM product_data WHERE category=%s AND supplier=%s AND name=%s', (category, supplier, name))
        exists_product = cursor.fetchone()
        if exists_product:
            messagebox.showerror('Duplicate Entry', 'Product already exists!')
            return

        # === INSERT DATA ===
        cursor.execute('INSERT INTO product_data (category,supplier,name,price,quantity,status) VALUES (%s, %s, %s, %s, %s, %s)',
                       (category, supplier, name, price, quantity, status))
        connection.commit()

        treeview_data(treeview)
        messagebox.showinfo('Success', 'Product added successfully!')

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

#Update button functionality==========================================================================================================================
def update_product(category, supplier, name, treeview):
    selected = treeview.selection()
    if not selected:
        messagebox.showerror('Error', 'No selection made!')
        return

    cursor, connection = connect_database()
    if not cursor or not connection:
        return

    try:
        cursor.execute('USE inventory_data')
        item_id = treeview.item(selected[0])['values'][0]
        cursor.execute('SELECT category, supplier, name FROM product_data WHERE id = %s', (item_id,))
        current_data = cursor.fetchone()
        new_data = (category, supplier, name)

        if current_data == new_data:
            messagebox.showinfo('Information', 'No changes detected.')
            return

        cursor.execute('''
            UPDATE product_data
            SET category = %s, supplier = %s, name = %s
            WHERE id = %s
        ''', (category, supplier, name, item_id))
        connection.commit()
        treeview_data(treeview)
        messagebox.showinfo('Success', 'Product updated successfully!')

    except Exception as e:
        messagebox.showerror('Error', f'Error due to: {e}')
    finally:
        cursor.close()
        connection.close()

#========================================================================================================================================================

#=Search button function====================================================================================================
def search_product(search_comobox,search_entry,treeview):
    if search_comobox.get() == 'Search By':
        messagebox.showwarning('Warning','Please select an option')
    elif search_entry.get() == '':
        messagebox.showerror('Error','Enter the Value to Search')

    else:
        cursor,connection = connect_database()
        if not cursor or not connection:
            return
        try:
            cursor.execute('USE inventory_data')
            cursor.execute(f'SELECT * from product_data WHERE {search_comobox.get()}=%s',search_entry.get())
            records = cursor.fetchall()
            if len(records)==0:
                messagebox.showerror('Error','No records found')
            treeview.delete(*treeview.get_children())
            for record in records:
                treeview.insert('',END, value=record)
        except Exception as e:
                messagebox.showerror('Error',f'Error due to {e}')
        finally:
            cursor.close()
            connection.close()
#==================================================================================================================================

def delete_product(treeview):
    selected = treeview.selection()
    if not selected:
        messagebox.showerror('Error', 'Please select a product to delete.')
        return

    confirm = messagebox.askyesno('Confirm Delete', 'Are you sure you want to delete this product?')
    if not confirm:
        return

    cursor, connection = connect_database()
    if not cursor or not connection:
        return

    try:
        cursor.execute('USE inventory_data')
        item_id = treeview.item(selected[0])['values'][0]

        cursor.execute('DELETE FROM product_data WHERE id = %s', (item_id,))
        connection.commit()

        treeview_data(treeview)
        messagebox.showinfo('Success', 'Product deleted successfully!')

    except Exception as e:
        messagebox.showerror('Error', f'Error while deleting: {e}')
    finally:
        cursor.close()
        connection.close()


#Show all button function============================================================
def show_all(search_entry,search_combobox,treeview):
    treeview_data(treeview)
    search_entry.delete(0,END)
    search_combobox.set('Search By')
#==================================================================================

def refresh_fields(category_combobox, supplier_combobox, name_entry, price_entry, quantity_entry, status_combobox, treeview):
    fetch_supplier_category(category_combobox, supplier_combobox)
    clear_fields(category_combobox, supplier_combobox, name_entry, price_entry, quantity_entry, status_combobox, treeview, check=True)
    messagebox.showinfo('Refreshed', 'Data has been refreshed from the database.')


#Gui product===========================================================================================================================
def product_form(window,dashboard_frame):
    global back_icon, product_frame,treeview,logo
    if product_frame is None or not product_frame.winfo_exists():
        product_frame = Frame(window,dashboard_frame,  width=1515, height=650, bg='#EDE3D2')
        product_frame.place(x=0, y=121)

        back_icon = PhotoImage(file='images/back.png')
        back_button = Button(product_frame, image=back_icon, bg='#EDE3D2',bd=0, cursor='hand2',
                             command=lambda:back_to_dashboard(product_frame, dashboard_frame))
        back_button.place(x=20, y=5,width=30,height=30)

        left_frame = Frame(product_frame,bg='white',bd=2, relief=RIDGE)
        left_frame.place(x=60,y=50)

        headingLabel = Label(left_frame, text='Manage Products Details', font=('times new roman', 16), bg='#0F4C81', fg='white')
        headingLabel.grid(row=0,columnspan=2,sticky='we')

        category_label = Label(left_frame, text='Category', font=('times new roman', 15, 'bold'),bg='white')
        category_label.grid(row=1,column=0,padx=20,pady=10,sticky='w')
        category_combobox = ttk.Combobox(left_frame, values=(), font=('times new roman', 12),width=30, state='readonly')
        category_combobox.set('Empty')
        category_combobox.grid(row=1, column=1,padx=30,pady=20)

        supplier_label = Label(left_frame, text='Supplier', font=('times new roman', 15, 'bold'),bg='white')
        supplier_label.grid(row=2,column=0,padx=20,pady=10,sticky='w')
        supplier_combobox = ttk.Combobox(left_frame, values=(), font=('times new roman', 12),width=30, state='readonly')
        supplier_combobox.set('Empty')
        supplier_combobox.grid(row=2, column=1,padx=40)

        name_label = Label(left_frame, text='Name', font=('times new roman', 15, 'bold'),bg='white')
        name_label.grid(row=3,column=0,padx=20,pady=10,sticky='w')
        name_entry = Entry(left_frame,font=('times new roman',14,'bold'),bg='lightyellow',width=25)
        name_entry.grid(row=3,column=1,pady=20)

        price_label = Label(left_frame, text='Price', font=('times new roman', 15, 'bold'),bg='white')
        price_label.grid(row=4,column=0,padx=20,pady=10,sticky='w')
        price_entry = Entry(left_frame,font=('times new roman',14,'bold'),bg='lightyellow',width=25)
        price_entry.grid(row=4,column=1)

        quantity_label = Label(left_frame, text='Quantity', font=('times new roman', 15, 'bold'),bg='white')
        quantity_label.grid(row=6,column=0,padx=20,pady=10,sticky='w')
        quantity_entry = Entry(left_frame,font=('times new roman',14,'bold'),bg='lightyellow',width=25)
        quantity_entry.grid(row=6,column=1)

        status_label = Label(left_frame, text='Status', font=('times new roman', 15, 'bold'),bg='white')
        status_label.grid(row=7,column=0,padx=20,pady=10,sticky='w')
        status_combobox = ttk.Combobox(left_frame, values=('Active','Inactive'), font=('times new roman', 12),width=30, state='readonly')
        status_combobox.set('Select Status')
        status_combobox.grid(row=7, column=1,padx=40)

        button_frame = Frame(left_frame,bg='white')
        button_frame.grid(row=8,columnspan=2,pady=20)

        add_button = Button(button_frame, text="Add",font=('times new roman',12 ),width=10,cursor='hand2',fg='white',bg='#0F4C81',
                            command=lambda:add_product(category_combobox.get(),supplier_combobox.get(),name_entry.get(),
                                                       price_entry.get(),quantity_entry.get(),status_combobox.get(),treeview))
        add_button.grid(row=0, column=0, padx=20)

        update_button = Button(button_frame, text="Update",font=('times new roman',12 ),width=10,cursor='hand2',fg='white',bg='#0F4C81',
                               command=lambda:update_product(category_combobox.get(),supplier_combobox.get(),name_entry.get(),treeview))
        update_button.grid(row=0, column=1, padx=20)

        delete_button = Button(button_frame, text="Delete",font=('times new roman',12 ),width=10,cursor='hand2',fg='white',bg='#0F4C81',
                                command=lambda: delete_product(treeview))
        delete_button.grid(row=0, column=2, padx=20)

        clear_button = Button(button_frame, text="Clear",font=('times new roman',12 ),width=10,cursor='hand2',fg='white',bg='#0F4C81',
                              command=lambda: clear_fields(category_combobox,supplier_combobox,name_entry,price_entry,quantity_entry,
                                                           status_combobox,treeview,True))
        clear_button.grid(row=0, column=3, padx=20)

        refresh_button = Button(button_frame, text="Refresh", font=('times new roman', 12), width=10, cursor='hand2',
                        fg='white', bg='#0F4C81',
                        command=lambda: refresh_fields(category_combobox, supplier_combobox,
                                                       name_entry, price_entry, quantity_entry, status_combobox, treeview))
        refresh_button.grid(row=0, column=4, padx=20)

        search_frame = LabelFrame(product_frame,text='Search Product',font=('times new roman',15,'bold'), bg='white')
        search_frame.place(x=780,y=50)

        search_combobox = ttk.Combobox(search_frame, values=('Category','Supplier','Name','Status'), font=('times new roman', 12),width=16, state='readonly')
        search_combobox.set('Search By')
        search_combobox.grid(row=0, column=0,padx=30)

        search_entry = Entry(search_frame,font=('times new roman',14,'bold'),bg='lightyellow',width=15,)
        search_entry.grid(row=0,column=1)

        search_button = Button(search_frame, text="Search",font=('times new roman',12 ),width=10,cursor='hand2',fg='white',bg='#0F4C81',
                               command=lambda:search_product(search_combobox,search_entry,treeview))
        search_button.grid(row=0, column=2, padx=20,pady=10)

        show_button = Button(search_frame, text="Show All",font=('times new roman',12 ),width=10,cursor='hand2',fg='white',bg='#0F4C81',
                             command=lambda:show_all(search_entry,search_combobox,treeview))
        show_button.grid(row=0, column=3, padx=20)

        treeview_frame = Frame(product_frame,bg='#EDE3D2')
        treeview_frame.place(x=780,y=130,height=450,width=650)

        horizontal_scrollbar = Scrollbar(treeview_frame, orient=HORIZONTAL)
        vertical_scrollbar = Scrollbar(treeview_frame, orient=VERTICAL)

        treeview = ttk.Treeview(treeview_frame,columns=('id','category','supplier','name','price','quantity','status'), 
                                show='headings',yscrollcommand=vertical_scrollbar.set, xscrollcommand=horizontal_scrollbar.set)
        
        horizontal_scrollbar.pack(side=BOTTOM,fill=X)
        vertical_scrollbar.pack(side=RIGHT,fill=Y)
        horizontal_scrollbar.config(command=treeview.xview)
        vertical_scrollbar.config(command=treeview.yview)
        
        treeview.pack(fill=BOTH,expand=1)

        treeview.heading('id',text='ID')
        treeview.heading('category',text='Category')
        treeview.heading('supplier',text='Supplier')
        treeview.heading('name',text='Product Name')
        treeview.heading('price',text='Price')
        treeview.heading('quantity',text='Quantity')
        treeview.heading('status',text='Status')

        treeview.column('id', width=50, anchor='center')
        treeview.column('category', width=120)
        treeview.column('supplier', width=120)
        treeview.column('name', width=150)
        treeview.column('price', width=80, anchor='e')      
        treeview.column('quantity', width=80, anchor='e')  
        treeview.column('status', width=100, anchor='center')
        treeview_data(treeview)

        fetch_supplier_category(category_combobox,supplier_combobox)

        treeview.bind('<ButtonRelease-1>',lambda event:select_data(event,category_combobox,supplier_combobox,name_entry,price_entry,quantity_entry,
                                                                   status_combobox,treeview))


    else:
        product_frame.place(x=0, y=121)
