from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import re
from employee_form import connect_database

category_frame = None

def back_to_dashboard(current_frame, dashboard_frame):
    current_frame.place_forget()
    dashboard_frame.place(x=0, y=0, relwidth=1, relheight=1)

#Clear fields button function===================================================================================================================================
def clear_fields(id_entry,category_name_entry,description_text,treeview,check):
    id_entry.delete(0,END)
    category_name_entry.delete(0,END)
    description_text.delete(1.0,END)
    if check:
        treeview.selection_remove(treeview.selection())
#======================================================================================================================================================

#Selection of Data from treeview===========================================================================================
def select_data(event,id_entry,category_name_entry,description_text,treeview):
    index = treeview.selection()
    content = treeview.item(index)
    row = content['values']
    clear_fields(id_entry,category_name_entry,description_text,treeview,False)
    id_entry.insert(0,row[0])
    category_name_entry.insert(0,row[1])
    description_text.insert(1.0,row[2])
#========================================================================================================================================

#Treeview DAta=========================================================================================
def treeview_data(treeview):
    cursor, connection = connect_database()
    if not cursor or not connection:
        return
    try:
        cursor.execute('USE inventory_data')
        cursor.execute('SELECT * from category_data')
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
def add_category(id, name, description, treeview):
    try:
        try:
            id = int(id)
        except ValueError:
            messagebox.showerror('Invalid Input', 'Category ID must be a number!')
            return

        if not name.strip() or not re.fullmatch(r"[A-Za-z\s\.\'\-]+", name.strip()):
            messagebox.showerror('Invalid Name', 'Name must contain only letters, spaces, dots, apostrophes, or hyphens!')
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
            CREATE TABLE IF NOT EXISTS category_data (
                id INT PRIMARY KEY,
                name VARCHAR(100),
                description TEXT
            )
        ''')

        # === CHECK FOR DUPLICATES ===
        cursor.execute('SELECT * FROM category_data WHERE id=%s', (id))
        if cursor.fetchone():
            messagebox.showerror('Duplicate Entry', 'Category with same ID already exists!')
            return

        # === INSERT DATA ===
        cursor.execute('INSERT INTO category_data VALUES (%s, %s, %s)',
                       (id, name.strip(), description.strip()))
        connection.commit()

        # === REFRESH TREEVIEW ===
        treeview_data(treeview)
        messagebox.showinfo('Success', 'Category added successfully!')

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
def update_category(id,name,description,treeview):
    selected = treeview.selection()
    if not selected:
        messagebox.showerror('Error','No Selection Done!')
    else:
        cursor, connection = connect_database()
        if not cursor or not connection:
            return
        try:
            cursor.execute('USE inventory_data')
            cursor.execute('SELECT * from category_data WHERE id=%s',(id,))
            current_data = cursor.fetchone()
            current_data = current_data[1:4]
            new_data = (name,description)

            if current_data==new_data:
                messagebox.showinfo('Information','No changes Detected')
                return
            cursor.execute('''UPDATE category_data SET name=%s, description=%s WHERE id=%s''', 
                            (name,description,id))
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
def delete_supplier(id,id_entry, category_name_entry, description_text, treeview):
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
            cursor.execute('DELETE FROM category_data WHERE id=%s', (id,))
            connection.commit()
            treeview_data(treeview)
            clear_fields(id_entry, category_name_entry,description_text, treeview, True)
            messagebox.showinfo('Success', 'Data deleted successfully!')
        except Exception as e:
            messagebox.showerror('Error', f'Error due to {e}')
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
#===============================================================================================================

#Gui category===========================================================================================================================
def category_form(window,dashboard_frame):
    global back_icon, category_frame,treeview,logo
    if category_frame is None or not category_frame.winfo_exists():
        category_frame = Frame(window,dashboard_frame,  width=1515, height=650, bg='#EDE3D2')
        category_frame.place(x=0, y=121)

        headingLabel = Label(category_frame, text='Manage Category Details', font=('times new roman', 16), bg='#0F4C81', fg='white')
        headingLabel.place(x=0, y=0, relwidth=1)

        back_icon = PhotoImage(file='images/back.png')
        back_button = Button(category_frame, image=back_icon, bg='#EDE3D2',bd=0, cursor='hand2',
                             command=lambda:back_to_dashboard(category_frame, dashboard_frame))
        back_button.place(x=10, y=30,width=30,height=30)

        logo = PhotoImage(file='images/shop.png')
        label = Label(category_frame,image=logo,padx=30,bg='#EDE3D2')
        label.place(x=30,y=100,width=600)

        detail_frame = Frame(category_frame,bg='#EDE3D2')
        detail_frame.place(x=850,y=100)

        id_label = Label(detail_frame,text='Category ID',font=('times new roman',14,'bold'),bg='#EDE3D2')
        id_label.grid(row=0,column=0,padx=(20,40),sticky='w')
        id_entry = Entry(detail_frame,font=('times new roman',14,'bold'),bg='white',width=25)
        id_entry.grid(row=0,column=1)

        category_name_label = Label(detail_frame,text='Category Name',font=('times new roman',14,'bold'),bg='#EDE3D2')
        category_name_label.grid(row=1,column=0,padx=(20,40),sticky='w')
        category_name_entry = Entry(detail_frame,font=('times new roman',14,'bold'),bg='white',width=25)
        category_name_entry.grid(row=1,column=1,pady=20)

        description_label = Label(detail_frame,text='Description',font=('times new roman',14,'bold'),bg='#EDE3D2')
        description_label.grid(row=2,column=0,padx=(20,40),sticky='nw')
        description_text = Text(detail_frame,width=30,height=6,bd=2)
        description_text.grid(row=2,column=1)

        button_frame = Frame(category_frame,bg='#EDE3D2')
        button_frame.place(x=850,y=330)

        add_button = Button(button_frame, text="Add",font=('times new roman',12 ),width=10,cursor='hand2',fg='white',bg='#0F4C81',
                            command=lambda:add_category(id_entry.get(),category_name_entry.get(),
                                                        description_text.get(1.0,END).strip(),treeview))
        add_button.grid(row=0, column=0, padx=20)

        update_button = Button(button_frame, text="Update",font=('times new roman',12 ),width=10,cursor='hand2',fg='white',bg='#0F4C81',
                               command=lambda:update_category(id_entry.get(),category_name_entry.get()
                                                              ,description_text.get(1.0,END).strip(),treeview))
        update_button.grid(row=0, column=1,padx=20)

        delete_button = Button(button_frame, text="Delete",font=('times new roman',12 ),width=10,cursor='hand2',fg='white',bg='#0F4C81',
                               command=lambda: delete_supplier(id_entry.get(), id_entry, category_name_entry,description_text,treeview))
        delete_button.grid(row=0, column=2, padx=20)

        clear_button = Button(button_frame, text="Clear",font=('times new roman',12 ),width=10,cursor='hand2',fg='white',bg='#0F4C81',
                              command=lambda: clear_fields(id_entry, category_name_entry, description_text,treeview,True))
        clear_button.grid(row=0, column=3,padx=20)

        treeview_frame = Frame(category_frame,bg='#EDE3D2')
        treeview_frame.place(x=820,y=400,height=200,width=580)

        horizontal_scrollbar = Scrollbar(treeview_frame, orient=HORIZONTAL)
        vertical_scrollbar = Scrollbar(treeview_frame, orient=VERTICAL)

        treeview = ttk.Treeview(treeview_frame,columns=('id','name','description'), show='headings',yscrollcommand=vertical_scrollbar.set,
                                                            xscrollcommand=horizontal_scrollbar.set)
        
        horizontal_scrollbar.pack(side=BOTTOM,fill=X)
        vertical_scrollbar.pack(side=RIGHT,fill=Y)
        horizontal_scrollbar.config(command=treeview.xview)
        vertical_scrollbar.config(command=treeview.yview)
        
        treeview.pack(fill=BOTH,expand=1)

        treeview.heading('id',text='Category ID')
        treeview.heading('name',text='Category Name')
        treeview.heading('description',text='Category Description')

        treeview.column('id',width=80)
        treeview.column('name',width=160)
        treeview.column('description',width=300)

        treeview_data(treeview)
    
        treeview.bind('<ButtonRelease-1>',lambda event:select_data(event,id_entry,category_name_entry,description_text,treeview))


    else:
        category_frame.place(x=0, y=121)