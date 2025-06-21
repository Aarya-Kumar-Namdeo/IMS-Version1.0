from tkinter import *
from tkinter import ttk
from tkcalendar import DateEntry
import pymysql
import re
import openpyxl
from tkinter import messagebox,filedialog

Employee_frame = None 

def back_to_dashboard(current_frame, dashboard_frame):
    current_frame.place_forget()
    dashboard_frame.place(x=0, y=0, relwidth=1, relheight=1)

#========Database se connection===========================================================
def connect_database():
    try:
        connection = pymysql.connect(host='localhost',user='root',password='Your Password') #HERE YOU HAVE TO ENTER YOUR PASSWORD OF SQL COMMAND LINE
        cursor = connection.cursor()
    except:
        messagebox.showerror('Error','Database connectivity issue Try Again!')
        return None,None
    
    return cursor, connection
#============================================================================================

#=======SQL table creation=========================================================================================================================        
def create_database_table():
    cursor,connection = connect_database()
    cursor.execute('CREATE DATABASE IF NOT EXISTS inventory_data')
    cursor.execute('USE inventory_data')
    cursor.execute('CREATE TABLE IF NOT EXISTS employee_data (empid INT PRIMARY KEY, name VARCHAR(100), email VARCHAR(100), gender VARCHAR(50),' \
                    ' contact VARCHAR(30), dob VARCHAR(30), emptype VARCHAR(50), education VARCHAR(30), workshift VARCHAR(50), salary VARCHAR(50), ' \
                    'usertype VARCHAR(50), doj VARCHAR(30), address VARCHAR(100), password VARCHAR(50))')
#======================================================================================================================================================

#=====View of data=====================================================================
def treeview():
    cursor, connection =connect_database()
    if not cursor or not connection:
            return
    cursor.execute('USE inventory_data')
    try:
        cursor.execute('SELECT * from employee_data')
        employee_records = cursor.fetchall()
        employee_treeview.delete(*employee_treeview.get_children())
        for record in employee_records:
            employee_treeview.insert('',END,values=record)
    except Exception as e:
        messagebox.showerror('Error',f'Error due to {e}')
    finally:
        cursor.close()
        connection.close()
#===========================================================================================

#Selection of Data from treeview===========================================================================================
def select_data(event, empid_entry, name_entry, email_entry, dob_date_entry, gender_combobox, contact_entry, emp_type_combobox,
                education_combobox, work_shift_combobox, address_text, doj_date_entry, salary_entry, usertype_combobox, password_entry):
    
    selected_item = employee_treeview.selection()
    if not selected_item:
        return
    
    content = employee_treeview.item(selected_item[0])
    values = content['values']
    if not values:
        return

    clear_fields(empid_entry, name_entry, email_entry, dob_date_entry, gender_combobox, contact_entry,
                 emp_type_combobox, education_combobox, work_shift_combobox, address_text, doj_date_entry,
                 salary_entry, usertype_combobox, password_entry, False)
    
    empid_entry.insert(0, values[0])
    name_entry.insert(0, values[1])
    email_entry.insert(0, values[2])
    gender_combobox.set(values[3])
    contact_entry.insert(0, values[4])
    dob_date_entry.set_date(values[5])
    emp_type_combobox.set(values[6])
    education_combobox.set(values[7])
    work_shift_combobox.set(values[8])
    salary_entry.insert(0, values[9])
    usertype_combobox.set(values[10])
    doj_date_entry.set_date(values[11])
    address_text.insert(1.0, values[12])
    password_entry.insert(0, values[13])
#========================================================================================================================================

#Adding employee Details====================================================================================================================
def add_employee(empid, name, email, gender, dob, emptype, education, workshift, address, doj, salary, usertype, password,contact):
    try:
        try:
            empid = int(empid)
        except ValueError:
            messagebox.showerror('Invalid Input', 'Employee ID must be an integer!')
            return
        
        if not re.fullmatch(r'[A-Za-z\s]+', name.strip()):
            messagebox.showerror('Invalid Name', 'Name should only contain letters and spaces!')
            return
        
        if not re.fullmatch(r'[A-Za-z0-9._%+-]+@gmail\.com', email.strip()):
            messagebox.showerror('Invalid Email', 'Email must be a valid address ending with @gmail.com')
            return
        
        if not re.fullmatch(r'\d{10}', contact.strip()):
            messagebox.showerror('Invalid Contact', 'Contact number must be exactly 10 digits!')
            return
        
        try:
            salary = int(salary)
        except ValueError:
            messagebox.showerror('Invalid Salary', 'Salary must be in Numbers!')
            return
        
        if not (password.isdigit() and len(password) >= 4):
            messagebox.showerror('Invalid Password', 'Password must be numeric and at least 4 digits!')
            return
        
        cursor, connection = connect_database()
        if not cursor or not connection:
            return

        # === CHECK FOR DUPLICATES ===
        cursor.execute('USE inventory_data')
        cursor.execute("SELECT * FROM employee_data WHERE empid=%s OR email=%s OR contact=%s", (empid, email, contact))
        existing = cursor.fetchone()
        if existing:
            messagebox.showerror('Duplicate Entry', 'Employee with same ID, Email or Contact already exists!')
            return
        
        address = address.strip()
        # === INSERT DATA ===
        cursor.execute('USE inventory_data')
        cursor.execute('INSERT INTO employee_data VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',
                    (empid, name, email, gender, contact, dob, emptype, education, workshift,
                        salary, usertype, doj, address, password))
        connection.commit()
        treeview()
        messagebox.showinfo('Success', 'Data Entered Successfully!') 
    except Exception as e:
            messagebox.showerror('Error',f'Error due to {e}')
    finally:
        cursor, connection = connect_database()
        if not cursor or not connection:
            return
        cursor.close()
        connection.close()
#==============================================================================================================================================

#Clear fields button function===================================================================================================================================
def clear_fields(empid_entry,name_entry,email_entry,dob_date_entry,gender_combobox,contact_entry,emp_type_combobox,education_combobox,
                 work_shift_combobox,address_text,doj_date_entry,salary_entry,usertype_combobox,password_entry,check):
    empid_entry.delete(0,END)
    name_entry.delete(0,END)
    email_entry.delete(0,END)
    from datetime import date
    dob_date_entry.set_date(date.today())
    gender_combobox.set('Select Gender')
    contact_entry.delete(0,END)
    emp_type_combobox.set('Select Type')
    education_combobox.set('Select Education')
    work_shift_combobox.set('Select Shift')
    address_text.delete(1.0,END)
    doj_date_entry.set_date(date.today())
    salary_entry.delete(0,END)
    usertype_combobox.set('Select Type')
    password_entry.delete(0,END)
    if check:
        employee_treeview.selection_remove(employee_treeview.selection())
#======================================================================================================================================================

#Update button functionality==========================================================================================================================
def update_employee(empid, name, email, gender, dob, emptype, education, workshift, address, doj, salary, usertype, password,contact):
    selected = employee_treeview.selection()
    if not selected:
        messagebox.showerror('Error','No Selection Done!')
    else:
        cursor, connection = connect_database()
        if not cursor or not connection:
            return
        try:
            cursor.execute('USE inventory_data')
            cursor.execute('SELECT * from employee_data WHERE empid=%s',(empid,))
            current_data = cursor.fetchone()
            current_data = current_data[1:0]
            address.strip()
            new_data = (name, email, gender, dob, emptype, education, workshift, address, doj, salary, usertype, password,contact)

            if current_data==new_data:
                messagebox.showinfo('Information','No changes Detected')
                return

            cursor.execute('''UPDATE employee_data SET name=%s, email=%s, gender=%s, dob=%s, contact=%s,emptype=%s, education=%s, workshift=%s,
                            address=%s, doj=%s,salary=%s, usertype=%s, password=%s WHERE empid=%s''', 
                            (name, email, gender, dob, contact, emptype, education, workshift, address, doj, salary, usertype,password, empid))
            connection.commit()
            treeview()
            messagebox.showinfo('Success','Data Updated Successfully!')
        except Exception as e:
            messagebox.showerror('Error',f'Error due to {e}')
        finally:
            cursor.close()
            connection.close()
#========================================================================================================================================================

#Delete button function==============================================================================================================
def delete_employee(empid):
    selected = employee_treeview.selection()
    if not selected:
        messagebox.showerror('Error','No Selection Done!')
    else:
        result = messagebox.askyesno('Confirm','Do you really want to delete the record')
        if result:
            cursor, connection = connect_database()
            if not cursor or not connection:
                return
            try:
                cursor.execute('USE inventory_data')
                cursor.execute('DELETE FROM employee_data WHERE empid=%s',(empid,))
                connection.commit()
                treeview()
                messagebox.showinfo('Success','Data is delete Successfully!')
            except Exception as e:
                messagebox.showerror('Error',f'Error due to {e}')
            finally:
                cursor.close()
                connection.close()
#===================================================================================================================================================

#=Search button function====================================================================================================
def search_employee(search_option,value):
    if search_option =='Search By':
        messagebox.showerror('Error','No option is Selected')
    elif value == '':
        messagebox.showerror('Error','Enter the Value to Search')
    else:
        cursor,connection = connect_database()
        if not cursor or not connection:
            return
        try:
            cursor.execute('USE inventory_data')
            cursor.execute(f'SELECT * from employee_data WHERE {search_option} LIKE %s',f'%{value}%')
            records = cursor.fetchall()
            employee_treeview.delete(*employee_treeview.get_children())
            for record in records:
                employee_treeview.insert('',END, value=record)
        except Exception as e:
                messagebox.showerror('Error',f'Error due to {e}')
        finally:
            cursor.close()
            connection.close()
#==================================================================================================================================

#Show all button function============================================================
def show_all(search_entry,search_combobox):
    treeview()
    search_entry.delete(0,END)
    search_combobox.set('Search By')
#==================================================================================

#Excel export=========================================================================================================
def export_to_excel():
    cursor, connection = connect_database()
    if not cursor or not connection:
        return

    try:
        cursor.execute('USE inventory_data')
        cursor.execute("SELECT * FROM employee_data")
        data = cursor.fetchall()

        # Ask user where to save file
        file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
        if not file_path:
            return  # User cancelled

        # Create workbook and sheet
        workbook = openpyxl.Workbook()
        sheet = workbook.active
        sheet.title = "Employees"

        # Write headers
        headers = [desc[0] for desc in cursor.description]
        sheet.append(headers)

        for row in data:
            sheet.append(row)

        workbook.save(file_path)
        messagebox.showinfo("Success", "Employee data exported successfully!")

    except Exception as e:
        messagebox.showerror("Error", f"Failed to export data\n{str(e)}")
#================================================================================================================================

#Employee form GUI========================================================================================================================================================
#----------Background frame of employee form----------------------------------------------------------------------------------------------------
def emp_form(window,dashboard_frame):
    global back_icon, Employee_frame, employee_treeview
    if Employee_frame is None or not Employee_frame.winfo_exists():
        Employee_frame = Frame(window,dashboard_frame, width=1515, height=650, bg='#EDE3D2')
        Employee_frame.place(x=0, y=121)

        headingLabel = Label(Employee_frame, text='Manage Employees Details', font=('times new roman', 16), bg='#0F4C81', fg='white')
        headingLabel.place(x=0, y=0, relwidth=1)

        back_icon = PhotoImage(file='images/back.png')
        back_button = Button(Employee_frame, image=back_icon, bg='#EDE3D2',bd=0, cursor='hand2',
                             command=lambda:back_to_dashboard(Employee_frame, dashboard_frame))
        back_button.place(x=10, y=30,width=30,height=30)
#--------------------------------------------------------------------------------------------------------------------------------------------------

#----------Top frame--------------------------------------------------------------------------------------------------------------------------------
        topframe = Frame(Employee_frame, bg='#EDE3D2')
        topframe.place(x=0,y=60, relwidth=1, height=235)
        search_frame = Frame(topframe, bg='#EDE3D2')
        search_frame.pack()
        search_comboBox = ttk.Combobox(search_frame,values=('Empid', 'Name', 'Email' ), font=('times new roman', 12), state='readonly', justify='center')
        search_comboBox.set("Search By")
        search_comboBox.grid(row=0, column=0, padx=20)
        search_entry = Entry(search_frame,font=('times new roman', 12),bg='white')
        search_entry.grid(row=0,column=1)
        search_button = Button(search_frame, text="Search",font=('times new roman',12 ),width=10,cursor='hand2',fg='white',bg='#0F4C81',command=lambda:search_employee(search_comboBox.get(),search_entry.get()))
        search_button.grid(row=0, column=2, padx=20)
        show_button = Button(search_frame, text='Show All', font=('times new roman', 12),width=10,cursor='hand2',fg='white',bg='#0F4C81',command=lambda:show_all(search_entry,search_comboBox))
        show_button.grid(row=0,column=3)
        
    #-------------------------------------------------------------------------------------------------------------------------------------------------------

    #treeview GUI---------------------------------------------------------------------------------------------------------------------------------------------------
        horizontal_scrollbar = Scrollbar(topframe, orient=HORIZONTAL)
        vertical_scrollbar = Scrollbar(topframe, orient=VERTICAL)

        employee_treeview = ttk.Treeview(topframe, columns=('empid', 'name', 'email', 'gender', 'contact', 'dob', 'emptype', 'education', 'workshift','salary',
                                                            'usertype','doj','address'), show='headings',yscrollcommand=vertical_scrollbar.set,
                                                            xscrollcommand=horizontal_scrollbar.set)
        
        horizontal_scrollbar.pack(side=BOTTOM,fill=X,padx=(40,40))
        vertical_scrollbar.pack(side=RIGHT,fill=Y,pady=(10.0),padx=(0,40))
        horizontal_scrollbar.config(command=employee_treeview.xview)
        vertical_scrollbar.config(command=employee_treeview.yview)

        employee_treeview.pack(pady=(10,0),padx=(50,0))
        employee_treeview.heading('empid',text='EmpId')
        employee_treeview.heading('name',text='Name')
        employee_treeview.heading('email',text='Email')
        employee_treeview.heading('gender',text='Gender')
        employee_treeview.heading('contact',text='Contact')
        employee_treeview.heading('dob',text='Date of Birth')
        employee_treeview.heading('emptype',text='Employee Type')
        employee_treeview.heading('education',text='Education')
        employee_treeview.heading('workshift',text='Workshift')
        employee_treeview.heading('salary',text='Salary')
        employee_treeview.heading('usertype',text='Usertype')
        employee_treeview.heading('doj',text='Data of Joining')
        employee_treeview.heading('address',text='Address')

        employee_treeview.column('empid',width=60)
        employee_treeview.column('name',width=140)
        employee_treeview.column('email',width=180)
        employee_treeview.column('gender',width=80)
        employee_treeview.column('contact',width=100)
        employee_treeview.column('dob',width=100)
        employee_treeview.column('emptype',width=80)
        employee_treeview.column('education',width=120)
        employee_treeview.column('workshift',width=100)
        employee_treeview.column('salary',width=100)
        employee_treeview.column('usertype',width=80)
        employee_treeview.column('doj',width=100)
        employee_treeview.column('address',width=200)

        treeview()
    #------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    #Details to enter-------------------------------------------------------------------------------------------------------------------------------------------------------    
        detail_frame = Frame(Employee_frame, bg='#EDE3D2')
        detail_frame.place(x=250,y=320)

        empid_label = Label(detail_frame, text='EmpID', font=('times new roman', 12), bg='#EDE3D2')
        empid_label.grid(row=0,column=0,padx=20,pady=10,sticky='w')
        empid_entry = Entry(detail_frame, font=('times new roman', 12))
        empid_entry.grid(row=0,column=1,padx=20,pady=10)

        name_label = Label(detail_frame, text='Name', font=('times new roman', 12),bg='#EDE3D2')
        name_label.grid(row=0,column=2,padx=20,pady=10,sticky='w')
        name_entry = Entry(detail_frame, font=('times new roman', 12))
        name_entry.grid(row=0,column=3,padx=20,pady=10)

        email_label = Label(detail_frame, text='Email', font=('times new roman', 12),bg='#EDE3D2')
        email_label.grid(row=0,column=4,padx=20,pady=10,sticky='w')
        email_entry = Entry(detail_frame, font=('times new roman', 12))
        email_entry.grid(row=0,column=5,padx=20,pady=10)

        gender_label = Label(detail_frame, text='Gender', font=('times new roman', 12),bg='#EDE3D2')
        gender_label.grid(row=1,column=0,padx=20,pady=10,sticky='w')
        gender_combobox = ttk.Combobox(detail_frame, values=('Male','Female'), font=('times new roman', 12),width=18, state='readonly')
        gender_combobox.set('Select Gender')
        gender_combobox.grid(row=1, column=1)

        dob_label = Label(detail_frame, text='Date of Birth', font=('times new roman', 12),bg='#EDE3D2')
        dob_label.grid(row=1,column=2,padx=20,pady=10,sticky='w')
        dob_date_entry = DateEntry(detail_frame,font=('times new roman',12), width= 18, state='normal', date_pattern='dd/mm/yyyy')
        dob_date_entry.grid(row=1,column=3)

        contact_label = Label(detail_frame, text='Contact', font=('times new roman', 12),bg='#EDE3D2')
        contact_label.grid(row=1,column=4,padx=20,pady=10,sticky='w')
        contact_entry = Entry(detail_frame, font=('times new roman', 12))
        contact_entry.grid(row=1,column=5,padx=20,pady=10)

        emp_type_label = Label(detail_frame, text='Employment Type', font=('times new roman', 12),bg='#EDE3D2')
        emp_type_label.grid(row=2,column=0,padx=20,pady=10,sticky='w')
        emp_type_combobox = ttk.Combobox(detail_frame, values=('Full Time', 'Part Time','Casual','Contract','Remote','Intern'), font=('times new roman', 12),width=18, state='readonly')
        emp_type_combobox.set('Select Type')
        emp_type_combobox.grid(row=2, column=1)

        education_label = Label(detail_frame, text='Education', font=('times new roman', 12),bg='#EDE3D2')
        education_label.grid(row=2,column=2,padx=20,pady=10,sticky='w')
        education_options = ['B.Tech','B.Com','M.Tech','M.Com','B.Sc','BBA','MBA','B.ED','BCA','MCA','PGDCA']
        education_combobox = ttk.Combobox(detail_frame, values=education_options, font=('times new roman', 12),width=18, state='readonly')
        education_combobox.set('Select')
        education_combobox.grid(row=2, column=3)

        work_shift_label = Label(detail_frame, text='Work Shift', font=('times new roman', 12),bg='#EDE3D2')
        work_shift_label.grid(row=2,column=4,padx=20,pady=10,sticky='w')
        work_shift_combobox = ttk.Combobox(detail_frame, values=('Morning','Evening','Night'), font=('times new roman', 12),width=18, state='readonly')
        work_shift_combobox.set('Select Shift')
        work_shift_combobox.grid(row=2, column=5)

        address_label = Label(detail_frame, text='Address', font=('times new roman', 12),bg='#EDE3D2')
        address_label.grid(row=3,column=0,padx=20,pady=10,sticky='w')
        address_text = Text(detail_frame,width=20,height=4)
        address_text.grid(row=3,column=1,rowspan=2)

        doj_label = Label(detail_frame, text='Date of Joining', font=('times new roman', 12),bg='#EDE3D2')
        doj_label.grid(row=3,column=2,padx=20,pady=10,sticky='w')
        doj_date_entry = DateEntry(detail_frame,font=('times new roman',12), width= 18, state='normal', date_pattern='dd/mm/yyyy')
        doj_date_entry.grid(row=3,column=3)

        salary_label = Label(detail_frame, text='Salary', font=('times new roman', 12),bg='#EDE3D2')
        salary_label.grid(row=3,column=4,padx=20,pady=10,sticky='w')
        salary_entry = Entry(detail_frame, font=('times new roman', 12))
        salary_entry.grid(row=3,column=5,padx=20,pady=10)

        usertype_label = Label(detail_frame, text='User Type', font=('times new roman', 12),bg='#EDE3D2')
        usertype_label.grid(row=4,column=2,padx=20,pady=10,sticky='w')
        usertype_combobox = ttk.Combobox(detail_frame, values=('Admin', 'Employee'), font=('times new roman', 12),width=18, state='readonly')
        usertype_combobox.set('Select Type')
        usertype_combobox.grid(row=4, column=3)

        password_label = Label(detail_frame, text='Password', font=('times new roman', 12),bg='#EDE3D2')
        password_label.grid(row=4,column=4,padx=20,pady=10,sticky='w')
        password_entry = Entry(detail_frame, font=('times new roman', 12))
        password_entry.grid(row=4,column=5,padx=20,pady=10)
    #-----------------------------------------------------------------------------------------------------------------------------------------------------------------------

    #---------add, update, delete and clear button---------------------------------------------------------------------------------------------------------------------------
        button_frame = Frame(Employee_frame,bg='#EDE3D2')
        button_frame.place(x=300,y=580)

        add_button = Button(button_frame, text="Add",font=('times new roman',12 ),width=10,cursor='hand2',fg='white',bg='#0F4C81',
                            command=lambda:add_employee(empid_entry.get(),name_entry.get(),email_entry.get(),gender_combobox.get(),dob_date_entry.get(),
                                                        emp_type_combobox.get(),education_combobox.get(),work_shift_combobox.get(),address_text.get(1.0,END),
                                                        doj_date_entry.get(),salary_entry.get(),usertype_combobox.get(),password_entry.get(),contact_entry.get()))
        add_button.grid(row=0, column=0, padx=30)
        
        update_button = Button(button_frame, text="Update",font=('times new roman',12 ),width=10,cursor='hand2',fg='white',bg='#0F4C81',
                            command=lambda:update_employee(empid_entry.get(),name_entry.get(),email_entry.get(),gender_combobox.get(),dob_date_entry.get()
                                                            ,emp_type_combobox.get(),education_combobox.get(),work_shift_combobox.get(),address_text.get(1.0,END),
                                                            doj_date_entry.get(),salary_entry.get(),usertype_combobox.get(),password_entry.get(),contact_entry.get()))
        update_button.grid(row=0, column=1, padx=30)
        
        delete_button = Button(button_frame, text="Delete",font=('times new roman',12 ),width=10,cursor='hand2',fg='white',bg='#0F4C81',command=lambda:delete_employee(empid_entry.get(),))
        delete_button.grid(row=0, column=3, padx=30)
        
        clear_button = Button(button_frame, text="Clear",font=('times new roman',12 ),width=10,cursor='hand2',fg='white',bg='#0F4C81',
                            command=lambda:clear_fields(empid_entry,name_entry,email_entry,dob_date_entry,gender_combobox,contact_entry,emp_type_combobox,
                                                        education_combobox,work_shift_combobox,address_text,doj_date_entry,salary_entry,usertype_combobox,
                                                        password_entry,True))
        clear_button.grid(row=0, column=4, padx=30)

        export_button = Button(detail_frame, text="Export to Excel", font=('times new roman', 12), bg="#0F4C81", fg="white", command=export_to_excel)
        export_button.grid(row=5, column=5, pady=20)
    #-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

        employee_treeview.bind('<ButtonRelease-1>',lambda event:select_data(event,empid_entry,name_entry,email_entry,dob_date_entry,gender_combobox,contact_entry,
                                                                            emp_type_combobox,education_combobox,work_shift_combobox,address_text,doj_date_entry,
                                                                            salary_entry,usertype_combobox,password_entry))
    else:
        Employee_frame.place(x=0, y=121)


    create_database_table()
    