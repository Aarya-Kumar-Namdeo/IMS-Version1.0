from tkinter import *
from tkinter import ttk
from tkinter import messagebox,filedialog
import re
import os
from datetime import datetime
import time
import platform
import subprocess
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from employee_form import connect_database

selected_product_id = None
cart_list = []
billamnt = 0
net_pay = 0
discount = 0

# Treeview Data=========================================================================================
def treeview_data(treeview):
    cursor, connection = connect_database()
    if not cursor or not connection:
        return
    try:
        cursor.execute('USE inventory_data')
        cursor.execute("SELECT id, name, price, quantity, status FROM product_data WHERE status = 'Active'")
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
# ===============================================================

# Search button function====================================================================================================
def search_product(search_entry, treeview):
    search_value = search_entry.get().strip()
    if search_value == '':
        messagebox.showerror('Error', 'Enter a name to search.')
        return

    cursor, connection = connect_database()
    if not cursor or not connection:
        messagebox.showerror('Error', 'Database connection failed.')
        return

    try:
        cursor.execute('USE inventory_data')
        query = "SELECT id, name, price, quantity, status FROM product_data WHERE name = %s AND status = 'Active'"
        cursor.execute(query, (search_value,))
        records = cursor.fetchall()

        # Clear old results from the treeview
        treeview.delete(*treeview.get_children())

        if not records:
            messagebox.showinfo('Info', 'No matching records found. Displaying all products.')
            cursor.execute("SELECT id, name, price, quantity, status FROM product_data")
            all_records = cursor.fetchall()
            for record in all_records:
                treeview.insert('', END, values=record)
        else:
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
# ==================================================================================================================================
#Selection of Data from treeview===========================================================================================
def select_data(event, product_entry, product_price_entry, stock_label, product_qty_entry, treeview):
    selected = treeview.selection()
    if not selected:
        return

    item = treeview.item(selected[0])
    values = item['values']

    if not values or len(values) < 4:
        return  # Safeguard in case of unexpected data

    global selected_product_id
    selected_product_id = values[0]
    
    # Set product name (readonly)
    product_entry.config(state='normal')
    product_entry.delete(0, END)
    product_entry.insert(0, values[1])
    product_entry.config(state='readonly')

    # Set price (readonly)
    product_price_entry.config(state='normal')
    product_price_entry.delete(0, END)
    product_price_entry.insert(0, values[2])
    product_price_entry.config(state='readonly')

    # Set stock label
    stock_qty = values[3]
    stock_label.config(text=f"In stock [{stock_qty}]")

    # Set quantity spinbox or entry
    product_qty_entry.delete(0, END)
    product_qty_entry.insert(0, '1')
#========================================================================================================================================

#Selection of Data from treeview to cart===========================================================================================
def select_data_cart(event, product_entry, product_price_entry, stock_label, product_qty_entry, cart_treeview):
    selected = cart_treeview.selection()
    if not selected:
        return

    item = cart_treeview.item(selected[0])
    values = item['values']

    if not values or len(values) < 4:
        return

    global selected_product_id
    selected_product_id = values[0]

    name = values[1]
    qty = values[2]
    price = values[3]

    # Set product name
    product_entry.config(state='normal')
    product_entry.delete(0, END)
    product_entry.insert(0, name)
    product_entry.config(state='readonly')

    # Set price
    product_price_entry.config(state='normal')
    product_price_entry.delete(0, END)
    product_price_entry.insert(0, price)
    product_price_entry.config(state='readonly')

    # Set quantity
    product_qty_entry.delete(0, END)
    product_qty_entry.insert(0, qty)

    # 🔄 Fetch stock from DB using selected_product_id
    cursor, connection = connect_database()
    if not cursor or not connection:
        messagebox.showerror("Error", "Failed to connect to database.")
        return

    try:
        cursor.execute("USE inventory_data")
        cursor.execute("SELECT quantity FROM product_data WHERE id = %s", (selected_product_id,))
        result = cursor.fetchone()
        if result:
            stock_qty = result[0]
            stock_label.config(text=f"In stock [{stock_qty}]")
        else:
            stock_label.config(text="In stock [N/A]")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to retrieve stock: {e}")
    finally:
        try:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
        except:
            pass
#========================================================================================================================================

# Show all button function============================================================
def show_all(search_entry, treeview):
    treeview_data(treeview)
    search_entry.delete(0, END)
# ==================================================================================

#add button function=============================================================================================
def add_cart(selected_product_id,product_entry, product_qty_entry, product_price_entry,cart_treeview,amountLabel,net_pay_Label,cart_headingLabel,stock_label):
    global cart_list

    name = product_entry.get()
    qty = product_qty_entry.get()
    price = product_price_entry.get()
    # Extract stock from label
    stock_text = stock_label.cget("text")  # e.g., "In stock [15]"
    stock_match = re.search(r'\[(\d+)\]', stock_text)
    stock = int(stock_match.group(1)) if stock_match else 0

    if name == '':
        messagebox.showerror('Error', "Please select a product.")
        return

    if price == '':
        messagebox.showerror('Error', "Product price not found.")
        return

    if qty == '':
        messagebox.showerror('Error', "Please enter quantity.")
        return

    try:
        qty = int(qty)
        price = float(price)
        if qty < 0:
            messagebox.showerror("Error", "Quantity cannot be negative.")
            return
        if qty > stock:
            messagebox.showerror("Error", f"Requested quantity ({qty}) exceeds stock ({stock}).")
            return
        price_cal = price  # per unit price
        cart_data = [selected_product_id, name, qty, price_cal,stock]
    except ValueError:
            messagebox.showerror('Error', "Invalid quantity or price format.")
            return

    # Check if product already exists in cart
    present = 'no'
    index_ = 0
    for row in cart_list:
        if selected_product_id == row[0]:
            present = 'yes'
            break
        index_ += 1

    if present == 'yes':
        choice = messagebox.askyesno('Confirm', 'Product already present.\nDo you want to update or remove it from the cart?')
        if choice:
            if qty == 0:
                cart_list.pop(index_)
            else:
                cart_list[index_][2] = qty
                # cart_list[index_][3] = price_cal
    else:
        cart_list.append(cart_data)

    show_cart(cart_list, cart_treeview)
    bill_updates(amountLabel,net_pay_Label,cart_headingLabel)

#Show cart=============================================================================
def show_cart(cart_list,cart_treeview):
    try:
        cart_treeview.delete(*cart_treeview.get_children())  
        for record in cart_list:
            cart_treeview.insert('', END, values=record)
    except Exception as e:
            messagebox.showerror('Error', f'Error occurred: {e}')
            return
#====================================================================================

#label updates==================================================================================
def bill_updates(amountLabel, net_pay_Label, cart_headingLabel):
    global billamnt, net_pay, discount  # <-- Add this line

    billamnt = 0
    net_pay = 0
    discount = 0

    for row in cart_list:
        billamnt += float(row[3]) * int(row[2])

    discount = (billamnt * 5) / 100
    net_pay = billamnt - discount

    amountLabel.config(text=f'Bill Amount\nRs. {billamnt:.2f}')
    net_pay_Label.config(text=f'Net Pay(Rs.)\nRs. {net_pay:.2f}')
    cart_headingLabel.config(text=f'Cart \t Total Product: {len(cart_list)}')

    return billamnt, net_pay
#=======================================================================================

#====================Generate bill===========================================================
def generate_bill(cus_name_entry, cus_contact_entry, billing_text,treeview):
    name = cus_name_entry.get().strip()
    contact = cus_contact_entry.get().strip()

    if name == '' or contact == '':
        messagebox.showerror('Error', 'Customer details are required')
        return

    if not contact.isdigit() or len(contact) != 10:
        messagebox.showerror('Error', 'Contact number must be 10 digits only.')
        return

    if len(cart_list) == 0:
        messagebox.showerror('Error', 'Please add products to cart.')
        return

    # ===== Bill Sections =====
    invoice = bill_top(name, contact, billing_text)
    bill_middle(billing_text,treeview)
    bill_bottom(billing_text)

    # ===== Save Bill to File =====
    with open(f'bills/{str(invoice)}.txt', 'w') as fp:
        fp.write(billing_text.get('1.0', END))

    messagebox.showinfo('Saved', 'Bill has been generated successfully.')
#--------------Bill top-----------------------------------------------------------
def bill_top(cus_name_entry,cus_contact_entry, billing_text):
    invoice = int(time.strftime('%H%M%S')) + int(time.strftime('%d%m%Y'))
    bill_top_temp =f'''
\t\tAkiya Inventory Pvt. Limited
\t Phone No. 9981xxxxxx , Jabalpur-482005
{str("="*46)}
 Customer Name: {cus_name_entry}
 Ph no. : {cus_contact_entry}
 Bill No. {str(invoice)}\t\t\t\tDate: {str(time.strftime("%d/%m/%Y"))}
{str("="*46)}
 Product Name\t\t\t\tQTY\tPrice
{str("="*46)}
    '''
    billing_text.config(state='normal')  
    billing_text.delete('1.0', END)
    billing_text.insert('1.0', bill_top_temp)
    billing_text.config(state='disabled')
    return invoice
#---------------------------------------------------------------------------------------------
#--------------Middle top-----------------------------------------------------------
def bill_middle(billing_text, treeview):
    cursor, connection = connect_database()
    if not cursor or not connection:
        messagebox.showerror("Error", "Failed to connect to database.")
        return

    try:
        cursor.execute('USE inventory_data')  # Use once

        billing_text.config(state='normal')  # Make it editable

        for row in cart_list:
            id = row[0]
            name = row[1]
            qty = int(row[2])             # Quantity being purchased
            available_qty = int(row[4])   # Stock in DB

            new_quantity = available_qty - qty
            status = 'Inactive' if new_quantity == 0 else 'Active'

            price = float(row[3]) * qty
            line = f"{name}\t\t\t\t{qty}\tRs.{price:.2f}"
            billing_text.insert(END, "\n" + line)

            cursor.execute('''
                UPDATE product_data
                SET quantity = %s, status = %s
                WHERE id = %s
            ''', (new_quantity, status, id))

        connection.commit()
        connection.close()
        treeview_data(treeview)
        billing_text.config(state='disabled') 

    except Exception as e:
        messagebox.showerror('Error', f'Error occurred: {e}')
#--------------Bottom top-----------------------------------------------------------
def bill_bottom(billing_text):
    bill_bottom_temp = f'''
{str("="*46)}
 Bill Amount\t\t\t\tRs. {billamnt:.2f}
 Discount\t\t\t\tRs. {discount:.2f}
 Net Pay\t\t\t\tRs. {net_pay:.2f}
{str("="*46)}\n
    '''
    billing_text.config(state='normal')  
    billing_text.insert(END, bill_bottom_temp)  # <-- Insert at END
    billing_text.config(state='disabled')
#---------------------------------------------------------------------------------------------
#================================================================================================================

#=======Clear Cart=======================================================================================
def clear_cart(product_entry, product_price_entry, stock_label, product_qty_entry,cus_name_entry,cus_contact_entry,treeview):
    # Clear customer details
    cus_name_entry.delete(0, END)
    cus_contact_entry.delete(0, END)

    # Clear product entry fields
    product_entry.config(state=NORMAL)
    product_entry.delete(0, END)
    product_entry.config(state='readonly')

    product_price_entry.config(state=NORMAL)
    product_price_entry.delete(0, END)
    product_price_entry.config(state='readonly')

    product_qty_entry.delete(0, END)

    stock_label.config(text=f"In stock [0]")

    # Deselect any selected row in the product treeview
    selected_item = treeview.focus()
    if selected_item:
        treeview.selection_remove(selected_item)
#=======================================================================================================================================

#=====Clear All =================================================================================================
def clear_all(cus_name_entry,cus_contact_entry,product_entry,product_price_entry,product_qty_entry,stock_label,treeview,cart_treeview,billing_text,
              amountLabel,discountLabel,net_pay_Label,cart_headingLabel,search_entry):
    # Clear customer details
    cus_name_entry.delete(0, END)
    cus_contact_entry.delete(0, END)

    # Clear product entry fields
    product_entry.config(state=NORMAL)
    product_entry.delete(0, END)
    product_entry.config(state='readonly')

    product_price_entry.config(state=NORMAL)
    product_price_entry.delete(0, END)
    product_price_entry.config(state='readonly')

    product_qty_entry.delete(0, END)

    search_entry.delete(0,END)

    stock_label.config(text=f"In stock [0]")

    # Deselect product table selection
    selected_product = treeview.focus()
    if selected_product:
        treeview.selection_remove(selected_product)

    # Deselect cart table selection (optional)
    selected_cart_item = cart_treeview.focus()
    if selected_cart_item:
        cart_treeview.selection_remove(selected_cart_item)

    # Clear cart list and cart table (if needed)
    cart_list.clear()
    cart_treeview.delete(*cart_treeview.get_children())  # comment this line if you want to preserve cart

    # Clear billing area (if you use a Text widget)
    billing_text.config(state='normal')  
    billing_text.delete('1.0', END)
    billing_text.config(state='disabled')

    cart_headingLabel.config(text='Cart \t Total Product: [0]')

    # Clear totals (if using labels or vars)
    amountLabel.config(text="Bill Amount\n[0]")
    discountLabel.config(text="Discount\n5%")
    net_pay_Label.config(text="Net Pay\n[0]")
#========================================================================================================================

#Print bill===================================================================================================
def print_bill(billing_text):
    content = billing_text.get('1.0', 'end').strip()
    if not content:
        messagebox.showwarning("Empty", "No bill content to print.")
        return

    # === Extract Invoice Number ===
    lines = content.split('\n')
    invoice_number = "invoice"
    for line in lines:
        if "Invoice No" in line:
            invoice_number = line.split(':')[-1].strip().replace(" ", "_")
            break

    # === Generate default file path with invoice number ===
    default_filename = f"{invoice_number}.pdf"

    file_path = filedialog.asksaveasfilename(
        defaultextension=".pdf",
        initialfile=default_filename,
        filetypes=[("PDF files", "*.pdf")],
        title="Save Bill as PDF"
    )

    if not file_path:
        return  # User cancelled

    try:
        c = canvas.Canvas(file_path, pagesize=A4)
        width, height = A4

        # === Header ===
        c.setFont("Helvetica-Bold", 16)
        c.drawCentredString(width / 2, height - 40, "INVENTORY BILL RECEIPT")
        c.setFont("Helvetica", 10)
        c.drawCentredString(width / 2, height - 60, f"Generated on {datetime.now().strftime('%d-%m-%Y %I:%M:%S %p')}")
        c.line(40, height - 70, width - 40, height - 70)

        y = height - 90
        c.setFont("Helvetica", 10)

        for line in lines:
            if y <= 60:
                c.showPage()
                y = height - 50
            c.drawString(50, y, line)
            y -= 15

        # === Footer ===
        c.setFont("Helvetica-Oblique", 9)
        c.line(40, 50, width - 40, 50)
        c.drawString(50, 35, "Thank you for your business!")
        c.drawRightString(width - 50, 35, "Inventory Management System")

        c.save()

        messagebox.showinfo("Success", f"Bill saved as PDF:\n{file_path}")

        # === Auto-open PDF ===
        try:
            if platform.system() == 'Windows':
                os.startfile(file_path)
            elif platform.system() == 'Darwin':  # macOS
                subprocess.call(['open', file_path])
            else:  # Linux
                subprocess.call(['xdg-open', file_path])
        except Exception as open_error:
            messagebox.showwarning("Notice", f"PDF saved, but failed to auto-open:\n{open_error}")

    except Exception as e:
        messagebox.showerror("Error", f"Failed to generate PDF:\n{e}")
#========================================================================================================================================

#GUI billing=============================================================================================
def billing_form(window):
    #Main billing frame====================================================================================================================
    billing_frame = Frame(window ,width=1515, height=690, bg='#EDE3D2')
    billing_frame.place(x=0, y=121)
    #======================================================================================================================================

    #left product frame===============================================================================================================
    product_frame = Frame(billing_frame,bg='white',bd=2, relief=RIDGE)
    product_frame.place(x=5,y=5,width=500,height=600)
    headingLabel = Label(product_frame, text='All products', font=('times new roman', 16), bg='#0F4C81', fg='white')
    headingLabel.pack(side=TOP,fill=X)
    #===============================================================================================================================

    #Search fraame with search and show button=============================================================================================
    search_frame = Frame(product_frame,bg='lightgray',bd=2, relief=RIDGE,width=494,height=85)
    search_frame.place(x=1,y=30)

    search_label = Label(search_frame, text='Search Product | By Name', font=('times new roman', 15, 'bold'),bg='lightgray',fg='green')
    search_label.place(x=1,y=1)

    name_label = Label(search_frame, text='Product Name', font=('times new roman', 15, 'bold'),bg='lightgray')
    name_label.place(x=5,y=40)

    search_entry = Entry(search_frame,font=('times new roman', 15, 'bold'),bg='lightyellow')
    search_entry.place(x=135,y=42)
    search_button = Button(search_frame, text="Search",font=('times new roman',12),width=10,cursor='hand2',fg='white',bg='#0F4C81',
                            command=lambda:search_product(search_entry,treeview))
    search_button.place(x=355,y=40)

    show_all_button = Button(search_frame, text="Show All",font=('times new roman',12),width=10,cursor='hand2',fg='white',bg='#0F4C81',
                             command=lambda:show_all(search_entry,treeview))
    show_all_button.place(x=355,y=3) 
    #========================================================================================================================================

    #Product frame treeview=============================================================================================================
    treeview_frame = Frame(product_frame,bg='lightgray',bd=2, relief=RIDGE,width=494,height=85)
    treeview_frame.place(x=1,y=115,width=494,height=450)

    horizontal_scrollbar = Scrollbar(treeview_frame, orient=HORIZONTAL)
    vertical_scrollbar = Scrollbar(treeview_frame, orient=VERTICAL)

    treeview = ttk.Treeview(treeview_frame,columns=('product_id','name','price','qty','status'), show='headings',
                            yscrollcommand=vertical_scrollbar.set,xscrollcommand=horizontal_scrollbar.set)
    
    horizontal_scrollbar.pack(side=BOTTOM,fill=X)
    vertical_scrollbar.pack(side=RIGHT,fill=Y)
    horizontal_scrollbar.config(command=treeview.xview)
    vertical_scrollbar.config(command=treeview.yview)
    
    treeview.pack(fill=BOTH,expand=1)

    treeview.heading('product_id',text='PID')
    treeview.heading('name',text='Product Name')
    treeview.heading('price',text='Price')
    treeview.heading('qty',text='Qty')
    treeview.heading('status',text='Status')

    treeview.column('product_id',width=50)
    treeview.column('name',width=160)
    treeview.column('price',width=100,anchor='w')
    treeview.column('qty',width=50,anchor='w')
    treeview.column('status',width=80,anchor='w')
    treeview_data(treeview)
    treeview.bind('<ButtonRelease-1>',lambda event:select_data(event,product_entry,product_price_entry,stock_label,product_qty_entry,treeview))
    note_label = Label(product_frame,text="Note : Enter 0 quantity to remove product from Cart", font=('goudy old style',12),fg='red',anchor='w')
    note_label.pack(side=BOTTOM,fill=X)

    #Center Customer frame=====================================================================================================
    customer_frame = Frame(billing_frame,bg='lightgray',bd=2, relief=RIDGE)
    customer_frame.place(x=510,y=5,width=550,height=70)
    headingLabel = Label(customer_frame, text='Customer Details', font=('times new roman', 16), bg='#0F4C81', fg='white')
    headingLabel.pack(side=TOP,fill=X)

    cus_name_label = Label(customer_frame, text='Name', font=('times new roman', 15, 'bold'),bg='lightgray')
    cus_name_label.place(x=5,y=35)

    cus_name_entry = Entry(customer_frame,font=('times new roman', 15, 'bold'),bg='lightyellow',width=18)
    cus_name_entry.place(x=65,y=35)

    cus_contact_label = Label(customer_frame, text='Contact No.', font=('times new roman', 15, 'bold'),bg='lightgray')
    cus_contact_label.place(x=245,y=35)

    cus_contact_entry = Entry(customer_frame,font=('times new roman', 15, 'bold'),bg='lightyellow',width=18)
    cus_contact_entry.place(x=360,y=35)
    #=============================================================================================================================

#=====Functionality========================================================================
    def get_input(value):
        text_cal_input.config(state='normal')
        current = text_cal_input.get("1.0", END).strip()
        text_cal_input.delete("1.0", END)
        text_cal_input.insert("1.0", current + str(value))
        text_cal_input.tag_add('right', "1.0", END)  # Apply the alignment tag
        text_cal_input.config(state='disabled')
    
    def clear_input():
        text_cal_input.config(state='normal')
        text_cal_input.delete("1.0", END)
        text_cal_input.tag_add('right', "1.0", END)  # Re-apply right alignment tag
        text_cal_input.config(state='disabled')

    def evaluate_expression():
        try:
            expression = text_cal_input.get("1.0", END).strip()
            result = str(eval(expression))
            text_cal_input.config(state='normal')
            text_cal_input.delete("1.0", END)
            text_cal_input.insert("1.0", result)
            text_cal_input.tag_add('right', "1.0", END)  # Apply right-alignment
            text_cal_input.config(state='disabled')
        except:
            text_cal_input.config(state='normal')
            text_cal_input.delete("1.0", END)
            text_cal_input.insert("1.0", "Error")
            text_cal_input.tag_add('right', "1.0", END)  # Apply alignment even for error
            text_cal_input.config(state='disabled')
    
    def restart_calculator():
        text_cal_input.config(state='normal')
        text_cal_input.delete("1.0", END)
        text_cal_input.config(state='disabled')
        messagebox.showinfo("Restart", "Calculator restarted successfully!")

    #Cart, calucalation and treeview in customer frame==========================================================================================
    cart_cal_frame = Frame(billing_frame, bg='lightgray', bd=2, relief=RIDGE)
    cart_cal_frame.place(x=510, y=78, width=550, height=410)

    # Calculation Frame (Left side of cart_cal_frame)
    calculation_frame = Frame(cart_cal_frame, bg='white', bd=8, relief=RIDGE)
    calculation_frame.place(x=0, y=0, width=265, height=406)

    # Create the Text widget (no justify here!)
    text_cal_input = Text(calculation_frame, font=('arial', 15, 'bold'), width=22, height=3,
                        bd=5, relief=GROOVE, state='disabled')
    text_cal_input.grid(row=0, columnspan=4)

    # Configure a text tag with right alignment
    text_cal_input.tag_configure('right', justify='right')

    b7 = Button(calculation_frame, text='7',font=('arial',15,'bold'),command=lambda:get_input(7),bd=5,width=4,pady=10,cursor='hand2')
    b7.grid(row=1,column=0)

    b8 = Button(calculation_frame, text='8',font=('arial',15,'bold'),command=lambda:get_input(8),bd=5,width=4,pady=10,cursor='hand2')
    b8.grid(row=1,column=1)

    b9 = Button(calculation_frame, text='9',font=('arial',15,'bold'),command=lambda:get_input(9),bd=5,width=4,pady=10,cursor='hand2')
    b9.grid(row=1,column=2)

    b_sum = Button(calculation_frame, text='+',font=('arial',15,'bold'),command=lambda:get_input('+'),bd=5,width=4,pady=10,cursor='hand2')
    b_sum.grid(row=1,column=3)

    b4 = Button(calculation_frame, text='4',font=('arial',15,'bold'),command=lambda:get_input(4),bd=5,width=4,pady=10,cursor='hand2')
    b4.grid(row=2,column=0)

    b5 = Button(calculation_frame, text='5',font=('arial',15,'bold'),command=lambda:get_input(5),bd=5,width=4,pady=10,cursor='hand2')
    b5.grid(row=2,column=1)

    b6 = Button(calculation_frame, text='6',font=('arial',15,'bold'),command=lambda:get_input(6),bd=5,width=4,pady=10,cursor='hand2')
    b6.grid(row=2,column=2)

    b_sub = Button(calculation_frame, text='-',font=('arial',15,'bold'),command=lambda:get_input('-'),bd=5,width=4,pady=10,cursor='hand2')
    b_sub.grid(row=2,column=3)

    b1 = Button(calculation_frame, text='1',font=('arial',15,'bold'),command=lambda:get_input(1),bd=5,width=4,pady=10,cursor='hand2')
    b1.grid(row=3,column=0)

    b2 = Button(calculation_frame, text='2',font=('arial',15,'bold'),command=lambda:get_input(2),bd=5,width=4,pady=10,cursor='hand2')
    b2.grid(row=3,column=1)

    b3 = Button(calculation_frame, text='3',font=('arial',15,'bold'),command=lambda:get_input(3),bd=5,width=4,pady=10,cursor='hand2')
    b3.grid(row=3,column=2)

    b_mux = Button(calculation_frame, text='*',font=('arial',15,'bold'),command=lambda:get_input('*'),bd=5,width=4,pady=10,cursor='hand2')
    b_mux.grid(row=3,column=3)

    b0 = Button(calculation_frame, text='0',font=('arial',15,'bold'),command=lambda:get_input(0),bd=5,width=4,pady=10,cursor='hand2')
    b0.grid(row=4,column=0)

    bCE = Button(calculation_frame, text='CE',font=('arial',15,'bold'), command=clear_input,bd=5,width=4,pady=10,cursor='hand2')
    bCE.grid(row=4,column=1)

    b_equal = Button(calculation_frame, text='=',font=('arial',15,'bold'),command=evaluate_expression,bd=5,width=4,pady=10,cursor='hand2')
    b_equal.grid(row=4,column=2)

    b_slash = Button(calculation_frame, text='/',font=('arial',15,'bold'),command=lambda:get_input('/'),bd=5,width=4,pady=10,cursor='hand2')
    b_slash.grid(row=4,column=3)

    b_restart = Button(calculation_frame, text='Restart Calculator',font=('arial',15,'bold'), command=restart_calculator,bd=0,width=20,pady=10,cursor='hand2')
    b_restart.grid(row=5,column=0,columnspan=4)

    # Cart Frame (Right side of cart_cal_frame)
    cart_frame = Frame(cart_cal_frame, bg='lightgray', bd=2, relief=RIDGE)
    cart_frame.place(x=266, y=0, width=280, height=406)

    cart_headingLabel = Label(cart_frame, text='Cart \t Total Product: [0]',
                         font=('times new roman', 16), bg='#0F4C81', fg='white')
    cart_headingLabel.pack(side=TOP, fill=X)

    cart_treeview_frame = Frame(cart_frame, bg='lightgray', bd=2, relief=RIDGE)
    cart_treeview_frame.pack(fill=BOTH, expand=True)

    horizontal_scrollbar = Scrollbar(cart_treeview_frame, orient=HORIZONTAL)
    vertical_scrollbar = Scrollbar(cart_treeview_frame, orient=VERTICAL)

    cart_treeview = ttk.Treeview(cart_treeview_frame,
                                 columns=('product_id', 'name', 'qty', 'price'),
                                 show='headings',
                                 yscrollcommand=vertical_scrollbar.set,
                                 xscrollcommand=horizontal_scrollbar.set)

    horizontal_scrollbar.pack(side=BOTTOM, fill=X)
    vertical_scrollbar.pack(side=RIGHT, fill=Y)
    horizontal_scrollbar.config(command=cart_treeview.xview)
    vertical_scrollbar.config(command=cart_treeview.yview)

    cart_treeview.pack(fill=BOTH, expand=1)

    cart_treeview.heading('product_id', text='PID')
    cart_treeview.heading('name', text='Supplier Name')
    cart_treeview.heading('qty', text='Qty')
    cart_treeview.heading('price', text='Price')

    cart_treeview.column('product_id', width=30,anchor='w')
    cart_treeview.column('name', width=100,anchor='w')
    cart_treeview.column('qty', width=50, anchor='w')
    cart_treeview.column('price', width=100, anchor='w')
    cart_treeview.bind('<ButtonRelease-1>',lambda event:select_data_cart(event,product_entry,product_price_entry,stock_label,
                                                                         product_qty_entry,cart_treeview))

    #=======================================================================================================================================

    #Add cart widgets frame========================================================================================================================
    add_cart_frame = Frame(billing_frame, bg='lightgray', bd=2, relief=RIDGE)
    add_cart_frame.place(x=510, y=490, width=550, height=115)

    product_name = Label(add_cart_frame, text='Product Name', font=('times new roman', 15, 'bold'),bg='lightgray')
    product_name.place(x=5,y=5)
    product_entry = Entry(add_cart_frame,font=('times new roman', 15, 'bold'),bg='lightyellow',state='readonly')
    product_entry.place(x=5,y=35,width=210, height=22)

    product_price = Label(add_cart_frame, text='Price Per Qty', font=('times new roman', 15, 'bold'),bg='lightgray')
    product_price.place(x=230,y=5)
    product_price_entry = Entry(add_cart_frame,font=('times new roman', 15, 'bold'),bg='lightyellow',state='readonly')
    product_price_entry.place(x=230,y=35,width=150, height=22)

    product_qty = Label(add_cart_frame, text='Quantity', font=('times new roman', 15, 'bold'),bg='lightgray')
    product_qty.place(x=390,y=5)
    product_qty_entry = Entry(add_cart_frame,font=('times new roman', 15, 'bold'),bg='lightyellow')
    product_qty_entry.place(x=395,y=35,width=125, height=22)

    stock_label = Label(add_cart_frame, text='In stock', font=('times new roman', 15, 'bold'),bg='lightgray')
    stock_label.place(x=5,y=70)

    clear_button = Button(add_cart_frame, text="Clear",font=('times new roman',12 ),width=10,cursor='hand2',fg='white',bg='#0F4C81',
                           command=lambda:clear_cart(product_entry, product_price_entry, stock_label, product_qty_entry,
                                                     cus_name_entry,cus_contact_entry,treeview))
    clear_button.place(x=150,y=70,width=125, height=30)

    add_button = Button(add_cart_frame, text="Add | Update",font=('times new roman',12 ),width=10,cursor='hand2',fg='white',bg='#0F4C81',
                        command=lambda:add_cart(selected_product_id,product_entry,product_qty_entry,product_price_entry,cart_treeview,
                                                amountLabel,net_pay_Label,cart_headingLabel,stock_label))
    add_button.place(x=295,y=70,width=200, height=30)

#====================================================================================================================
    
    #Right billing area  frame=====================================================================================================
    billing_area_frame = Frame(billing_frame,bg='lightgray',bd=2, relief=RIDGE)
    billing_area_frame.place(x=1065,y=5,width=443,height=460)
    headingLabel = Label(billing_area_frame, text='Customer Billing Area', font=('times new roman', 16), bg='#0F4C81', fg='white')
    headingLabel.pack(side=TOP,fill=X)
    scrollbar_text = Scrollbar(billing_area_frame, orient=VERTICAL)
    billing_text = Text(billing_area_frame, font=('times new roman', 12), bg='lightgray',
                          yscrollcommand=scrollbar_text.set)
    scrollbar_text.pack(side=RIGHT, fill=Y)
    scrollbar_text.config(command=billing_text.yview)
    billing_text.pack(fill=BOTH, expand=1)

    billing_detail_frame = Frame(billing_frame,bg='lightgray',bd=2, relief=RIDGE)
    billing_detail_frame.place(x=1065,y=470,width=443,height=135)
    
    amountLabel = Label(billing_detail_frame, text='Bill Amount\n[0]', font=('times new roman', 16), bg='#51354A', fg='white')
    amountLabel.place(x=2,y=5,width=140,height=70)

    discountLabel = Label(billing_detail_frame, text='Discount\n5%', font=('times new roman', 16), bg='#51354A', fg='white')
    discountLabel.place(x=144,y=5,width=140,height=70)

    net_pay_Label = Label(billing_detail_frame, text='Net Pay\n[0]', font=('times new roman', 16), bg='#51354A', fg='white')
    net_pay_Label.place(x=286,y=5,width=150,height=70)

    print_button = Button(billing_detail_frame, text="Print",font=('times new roman',12 ),width=10,cursor='hand2',fg='white',bg='#0F4C81',
                          command=lambda:print_bill(billing_text))
    print_button.place(x=10,y=82,width=125, height=40)

    clear2_button = Button(billing_detail_frame, text="Clear All",font=('times new roman',12 ),width=10,cursor='hand2',fg='white',bg='#0F4C81',
                           command=lambda:clear_all(cus_name_entry,cus_contact_entry,product_entry,product_price_entry,product_qty_entry,
                                                    stock_label,treeview,cart_treeview,billing_text,amountLabel,discountLabel,net_pay_Label,
                                                    cart_headingLabel,search_entry))
    clear2_button.place(x=155,y=82,width=125, height=40)

    generate_button = Button(billing_detail_frame, text="Generate Bill",font=('times new roman',12 ),
                             width=10,cursor='hand2',fg='white',bg='#0F4C81'
                             ,command=lambda:generate_bill(cus_name_entry, cus_contact_entry, billing_text,treeview))
    generate_button.place(x=300,y=82,width=125, height=40)

    footer = Label(window, text='Inventory Management System | Developed By Aarya Kumar Namdeo\nFor any technical issues +91xxxxxxxx37',
                   font=('times new roman',11),bg='#4d636d',fg='white')
    footer.pack(side=BOTTOM,fill=X)



