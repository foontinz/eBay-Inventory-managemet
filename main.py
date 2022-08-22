import csv
import time
import tkinter as tk
import mysql.connector
from tkinter import filedialog
from tkinter import messagebox
from ebay_utils import EbayTokenCreation


def create_window(height, width, title, resizable=False):
    window = tk.Tk()
    window.title(title)
    window.geometry(f"{width}x{height}")
    window.resizable(resizable, resizable)
    return window


class ProductWindow:
    def __init__(self, account_entry, user_id, app: 'App', db: 'DataBaseInterface'):
        self.user_id = user_id
        self.db = db
        self.app = app
        self.account_entry = account_entry
        self.product_entries = []
        self.main_frame = None
        self.second_frame = None
        self.third_frame = None
        self.canvas = None

        self.scrollbar_x = None
        self.scrollbar_y = None

        self.products_window = create_window(720, 1280, f'Products {self.user_id}', resizable=True)
        self.products_window.protocol("WM_DELETE_WINDOW", self.on_closing_event)
        self.build_widgets()

    def on_closing_event(self):
        self.products_window.destroy()
        self.account_entry.products_window = None

    def build_main_frame(self):
        self.main_frame = tk.Frame(self.products_window)
        self.main_frame.pack(fill=tk.BOTH, expand=1)

    def build_second_frame(self):
        self.second_frame = tk.Frame(self.main_frame)
        self.second_frame.pack(fill=tk.X, side=tk.BOTTOM)

    def build_canvas(self):
        self.canvas = tk.Canvas(self.main_frame)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

    def build_scrollbar(self):
        self.scrollbar_x = tk.Scrollbar(self.second_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        self.scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)

        self.scrollbar_y = tk.Scrollbar(self.main_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)

    def configure_canvas(self):
        self.canvas.configure(xscrollcommand=self.scrollbar_x.set)
        self.canvas.configure(yscrollcommand=self.scrollbar_y.set)
        self.canvas.bind('<Configure>', lambda e: self.canvas.configure(scrollregion=self.canvas.bbox(tk.ALL)))

    def build_third_frame(self):
        self.third_frame = tk.Frame(self.canvas)

    def build_canvas_window(self):
        self.canvas.create_window((0, 0), window=self.third_frame, anchor="nw")

    def build_widgets(self):
        self.product_entries = []
        parameters = ['Store Name', 'SKU', 'eBay Item Number', 'EC Site', 'eBayURL', 'purchase price',
                      'Purchase price - Match (1 or 0)', 'Invoicing charges', 'Stock Word', "Stock word-match (1 or 0)",
                      'Watch mode (1 or 0)', 'eBay Shipping', 'Expected profit', 'commission factor',
                      "eBay Price", 'note', 'check-logic', 'eBay automatic linkage function (1 or 0)', "eBay Qty",
                      "search_target", "result"]

        self.build_main_frame()
        self.build_second_frame()
        self.build_canvas()
        self.build_scrollbar()
        self.configure_canvas()
        self.build_third_frame()
        self.build_canvas_window()
        self.app.create_all_labels_entries(self.third_frame, parameters)

        row = 1
        for product in self.db.get_all_products_by_user(self.user_id):
            row += 1
            self.add_entry(product, row)

        self.create_refresh_btn()
        self.create_add_btn()

    def refresh(self):
        for widget in self.products_window.winfo_children():
            widget.destroy()
        self.product_entries = []
        self.build_widgets()

    def add_entry(self, product, row):
        entry = ProductEntry(self, self.app, self.db, self.third_frame, product, row)
        self.product_entries.append(entry)

    def create_add_btn(self):
        product = [[0], [0], [0], [0], [0], [0], [0], [0], [0], [0], [0], [0], [0], [0], [0], [0], [0], [0], [0], [0],
                   [0]]
        add_product_btn = tk.Button(self.third_frame, text='Add product', fg='grey',
                                    command=lambda: self.add_entry(product, (
                                            self.product_entries[-1].row + 1) if self.product_entries else 2),
                                    font=('Arial', 13, 'bold'), width=14)
        add_product_btn.grid(row=1, column=22)

    def create_refresh_btn(self):
        refresh_btn = tk.Button(self.third_frame, text='Refresh', fg='grey',
                                command=self.refresh, font=('Arial', 13, 'bold'), width=14)
        refresh_btn.grid(row=1, column=21)


class Entry:
    def __init__(self, app: "App", db: 'DataBaseInterface', frame, parameters, row):
        self.app = app
        self.frame = frame
        self._parameters = parameters
        self.db = db
        self.row = row

        self.save_button = None

        self.entries_collection = []

        self.create_entries()

    def create_entries(self):
        column = 0
        for parameter in self.parameters:
            self.entries_collection.append(self.create_entry(parameter, column))
            column += 1

    def create_entry(self, value, column, bg_color="White"):
        entry = tk.Entry(
            self.frame,
            width=18,
            font=('Arial', 12, 'bold'),
            justify=tk.LEFT,
            background=bg_color,
            fg='Black',
            relief=tk.RAISED)
        entry.insert(1, value)
        entry.grid(column=column, row=self.row)
        return entry

    def get_all_entries_values(self):
        return [entry.get() for entry in self.entries_collection]

    def create_save_btn(self, column):
        self.save_button = tk.Button(self.frame, text='Save', fg='grey', width=14,
                                     command=self.save, font=('Arial', 13, 'bold'))
        self.save_button.grid(row=self.row, column=column)

    def save(self):
        pass

    def create_delete_btn(self, column):
        delete_button = tk.Button(self.frame, text='Delete', fg='grey', width=14,
                                  command=self.delete, font=('Arial', 13, 'bold'))
        delete_button.grid(row=self.row, column=column)

    def delete(self):
        pass

    @property
    def parameters(self):
        return self._parameters

    @parameters.setter
    def parameters(self, params):
        self._parameters = params


class AccountEntry(Entry):
    def __init__(self, app: "App", db: 'DataBaseInterface', frame, parameters, row, refresh_token):
        parameters = parameters[:-1] + (refresh_token,) if refresh_token != '0' else parameters

        super().__init__(app, db, frame, parameters, row)
        self.products_window = None
        self._id = parameters[0]
        self.create_save_btn(4)
        self.create_delete_btn(5)
        self.create_products_btn()
        self.create_upload_button()

    def save(self):
        self.db.del_account(self._id)
        self.db.add_account(self.get_all_entries_values())

    def delete(self):
        if tk.messagebox.askyesno('Check', 'Delete?'):
            self.db.del_account(self._id)
            self.app.refresh_all_accounts_window()

    def create_products(self):
        if not self.products_window:
            self.products_window = ProductWindow(self, self._id, self.app, self.db)

    def create_products_btn(self):
        tk.Button(self.frame, text='Products', fg='grey', width=14,
                  command=self.create_products, font=('Arial', 13, 'bold')).grid(row=self.row, column=6)

    def create_upload_button(self):
        tk.Button(self.frame, text='Upload', fg='grey', width=14,
                  command=self.app.upload_file, font=('Arial', 13, 'bold'), ).grid(row=self.row, column=7)


class ProductEntry(Entry):
    def __init__(self, product_window, app: "App", db: 'DataBaseInterface', frame, parameters, row):
        super().__init__(app, db, frame, parameters, row)

        self._ebay_id = parameters[2]
        self.state = parameters[19]
        self.product_window = product_window

        self.create_save_btn(21)
        self.create_delete_btn(24)
        self.create_start_btn()
        self.create_stop_btn()

    def save(self):
        self.db.del_product(self._ebay_id)
        self.db.add_product(self.get_all_entries_values())

    def create_start_btn(self):
        start_button = tk.Button(self.frame, text='Start', fg='green', width=14,
                                 command=self.start_product, font=('Arial', 13, 'bold'))
        start_button.grid(row=self.row, column=22)
        if self.parameters[19] == '1':
            start_button.config(state='disabled')

    def start_product(self):
        self.db.start_product_by_id(self._ebay_id)
        self.product_window.refresh()
        self.app.refresh_main_window()

    def create_stop_btn(self):
        stop_button = tk.Button(self.frame, text='Stop', fg='red', width=14,
                                command=self.stop_product, font=('Arial', 13, 'bold'))
        stop_button.grid(row=self.row, column=23)
        if self.parameters[19] != '1':
            stop_button.config(state='disabled')

    def stop_product(self):
        self.db.stop_product_by_id(self._ebay_id)
        self.product_window.refresh()
        self.app.refresh_main_window()

    def delete(self):
        if tk.messagebox.askyesno('Check', 'Delete?'):
            self.db.del_product(self._ebay_id)
            self.product_window.refresh()
            self.app.refresh_main_window()


class App:

    def __init__(self, db: 'DataBaseInterface'):

        self.db = db
        self.login_window = None
        self.main_window = None
        self.all_accounts_window = None

        self.login_input = None
        self.pass_input = None

        self.btn_start = None
        self.btn_stop = None
        self.btn_show_all_accounts = None

        self.all_accounts_window_main_frame = None
        self.all_accounts_window_second_frame = None
        self.all_accounts_window_third_frame = None
        self.all_accounts_window_canvas = None

        self.all_accounts_window_scrollbar_y = None
        self.all_accounts_window_scrollbar_x = None
        self.all_accounts_window_accounts_entries = []

        self.user_ids = None

        self.create_login_window()

    @staticmethod
    def create_all_labels_entries(frame, parameters):
        for parameter in parameters:
            tk.Label(
                frame,
                width=16,
                text=parameter,
                font=('Arial', 12, 'bold'),
                justify=tk.LEFT,
                bg='LightSteelBlue',
                fg='Black',
                relief=tk.RAISED).grid(column=parameters.index(parameter), row=1)

    def start_all(self):
        self.db.start_all()
        self.refresh_all_products_windows()
        self.refresh_main_window()

    def stop_all(self):
        self.db.stop_all()
        self.refresh_all_products_windows()
        self.refresh_main_window()

    def refresh_all_products_windows(self):
        for account in self.all_accounts_window_accounts_entries:
            if account.products_window:
                if account.products_window.products_window.winfo_exists():
                    account.products_window.refresh()

    def create_login_window(self):
        if not self.main_window:
            self.login_window = create_window(360, 300, 'Login')
            self.login_window.iconphoto(False, tk.PhotoImage(file='888848.png'))
            self.build_login_window_widgets()
            self.login_window.protocol("WM_DELETE_WINDOW", lambda: self.login_window.destroy())

    def create_main_window(self):
        if not self.main_window:
            self.main_window = create_window(150, 280, 'eBay Tool')
            self.main_window.iconphoto(False, tk.PhotoImage(file='888848.png'))
            self.build_main_window_widgets()
            self.main_window.protocol("WM_DELETE_WINDOW", lambda: self.main_window.destroy())

    def build_login_window_widgets(self):
        self.create_login_label()
        self.create_login_input()
        self.create_password_label()
        self.create_password_input()
        self.create_login_button()

    def build_main_window_widgets(self):
        self.create_stop_button()
        self.create_start_button()
        self.create_all_accounts_button()

    def create_all_accounts_button(self):
        self.btn_show_all_accounts = tk.Button(self.main_window, text='Show all accounts', fg='grey',
                                               command=self.create_all_accounts_window, font=('Arial', 18, 'bold'), )
        self.btn_show_all_accounts.place(relx=0.07, rely=0.65)

    def create_all_accounts_window(self):
        if not self.all_accounts_window:
            self.all_accounts_window = create_window(720, 1280, 'All Accounts', resizable=True)
            self.build_all_accounts_window_widgets()
            self.all_accounts_window.protocol("WM_DELETE_WINDOW", self.on_all_accounts_window_closing_event)

    def on_all_accounts_window_closing_event(self):
        self.all_accounts_window.destroy()
        self.all_accounts_window = None

    def build_all_accounts_window_main_frame(self):
        self.all_accounts_window_main_frame = tk.Frame(self.all_accounts_window)
        self.all_accounts_window_main_frame.pack(fill=tk.BOTH, expand=1)

    def build_all_accounts_window_second_frame(self):
        self.all_accounts_window_second_frame = tk.Frame(self.all_accounts_window_main_frame)
        self.all_accounts_window_second_frame.pack(fill=tk.X, side=tk.BOTTOM)

    def build_all_accounts_window_canvas(self):
        self.all_accounts_window_canvas = tk.Canvas(self.all_accounts_window_main_frame)
        self.all_accounts_window_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

    def build_all_accounts_window_scrollbar(self):
        self.all_accounts_window_scrollbar_x = tk.Scrollbar(self.all_accounts_window_second_frame, orient=tk.HORIZONTAL,
                                                            command=self.all_accounts_window_canvas.xview)
        self.all_accounts_window_scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)

        self.all_accounts_window_scrollbar_y = tk.Scrollbar(self.all_accounts_window_main_frame, orient=tk.VERTICAL,
                                                            command=self.all_accounts_window_canvas.yview)
        self.all_accounts_window_scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)

    def configure_all_accounts_window_canvas(self):
        self.all_accounts_window_canvas.configure(xscrollcommand=self.all_accounts_window_scrollbar_x.set)
        self.all_accounts_window_canvas.configure(yscrollcommand=self.all_accounts_window_scrollbar_y.set)
        self.all_accounts_window_canvas.bind('<Configure>', lambda e: self.all_accounts_window_canvas.configure(
            scrollregion=self.all_accounts_window_canvas.bbox(tk.ALL)))

    def create_all_accounts_window_third_frame(self):
        self.all_accounts_window_third_frame = tk.Frame(self.all_accounts_window_canvas)

    def create_all_accounts_window_canvas_window(self):
        self.all_accounts_window_canvas.create_window((0, 0), window=self.all_accounts_window_third_frame, anchor="nw")

    def add_entry_to_all_accounts_window(self, account, row, refresh_token='0'):
        entry = AccountEntry(self, self.db, self.all_accounts_window_third_frame, account, row, refresh_token)
        self.all_accounts_window_accounts_entries.append(entry)

    def create_refresh_all_accounts_window_btn(self):
        refresh_btn = tk.Button(self.all_accounts_window_third_frame, text='Refresh', fg='grey',
                                command=self.refresh_all_accounts_window, font=('Arial', 13, 'bold'), width=14)
        refresh_btn.grid(row=1, column=4)

    def refresh_all_accounts_window(self):
        if self.all_accounts_window:
            if self.all_accounts_window.winfo_exists():
                for widget in self.all_accounts_window.winfo_children():
                    widget.destroy()

                del self.all_accounts_window_accounts_entries
                self.all_accounts_window_accounts_entries = []

                self.build_all_accounts_window_widgets()

    def create_add_all_accounts_window_btn(self):
        account = ('0', '0', '0', '0')
        add_account_btn = tk.Button(self.all_accounts_window_third_frame, text='Add account', fg='grey',
                                    command=lambda: self.add_new_entry_to_all_accounts_window(
                                        account, (self.all_accounts_window_accounts_entries[
                                                      -1].row + 1) if self.all_accounts_window_accounts_entries else 2),
                                    font=('Arial', 13, 'bold'), width=14)
        add_account_btn.grid(row=1, column=5)

    def add_new_entry_to_all_accounts_window(self, account, row):
        ebay = EbayTokenCreation()
        self.add_entry_to_all_accounts_window(account, row, refresh_token=ebay.refresh_token)

    def build_all_accounts_window_widgets(self):
        self.all_accounts_window_accounts_entries = []
        parameters = ['ID', 'login', 'password', 'oauth_code']

        self.build_all_accounts_window_main_frame()
        self.build_all_accounts_window_second_frame()
        self.build_all_accounts_window_canvas()
        self.build_all_accounts_window_scrollbar()
        self.configure_all_accounts_window_canvas()
        self.create_all_accounts_window_third_frame()
        self.create_all_accounts_window_canvas_window()
        self.create_all_labels_entries(self.all_accounts_window_third_frame, parameters)

        row = 1
        for account in self.db.get_all_accounts():
            row += 1
            self.add_entry_to_all_accounts_window(account, row)

        self.create_refresh_all_accounts_window_btn()
        self.create_add_all_accounts_window_btn()

    def refresh_main_window(self):
        if self.main_window:
            if self.main_window.winfo_exists():
                for widget in self.main_window.winfo_children():
                    widget.destroy()
                self.build_main_window_widgets()

    def create_start_button(self):
        self.btn_start = tk.Button(self.main_window, text='Start all', fg='Green',
                                   command=self.start_all, font=('Arial', 18, 'bold'))
        self.btn_start.place(relx=0.08, rely=0.5, anchor='sw')

        if not self.db.is_any_state(0):
            self.btn_start.config(state='disabled')

    def create_stop_button(self):
        self.btn_stop = tk.Button(self.main_window, text='Stop all', fg='Red',
                                  command=self.stop_all, font=('Arial', 18, 'bold'))
        self.btn_stop.place(relx=0.5, rely=0.5, anchor='sw')
        if not self.db.is_any_state(1):
            self.btn_stop.config(state='disabled')

    def create_login_label(self):
        tk.Label(self.login_window,
                 text='Login', font=('Arial', 15,), justify=tk.LEFT).place(relx=0.5, rely=0.15, anchor='center')

    def create_login_input(self):
        self.login_input = tk.Entry(self.login_window, font=('Arial', 15,), justify=tk.LEFT)
        self.login_input.place(relx=0.5, rely=0.3, anchor='center')

    def create_password_label(self):
        tk.Label(self.login_window, height=1, width=12, text='Password', font=('Arial', 15,),
                 justify=tk.LEFT).place(relx=0.5, rely=0.45, anchor='center')

    def create_password_input(self):
        self.pass_input = tk.Entry(self.login_window, font=('Arial', 15,), justify=tk.LEFT)
        self.pass_input.place(relx=0.5, rely=0.6, anchor='center')

    def create_login_button(self):
        tk.Button(self.login_window, width=9, text='Log in', bg='#CACDCE', font=('Arial', 15, 'bold'),
                  command=self.successful_login).place(relx=0.5, rely=0.75, anchor='center')

    def successful_login(self):
        if self.db.check_login_password(self.login_input.get().strip(), self.pass_input.get().strip()):
            self.user_ids = self.db.get_user_ids(self.login_input.get().strip(), self.pass_input.get().strip())
            self.login_window.destroy()
            self.create_main_window()

    def upload_file(self):
        filepath = filedialog.askopenfilename()

        if not filepath:
            return

        if filepath[-3:] != "csv":
            messagebox.showwarning("Wrong format", 'You can use only CSV format')
            return

        with open(filepath, 'r', encoding='utf-8') as csvfile:
            datareader = csv.reader(csvfile)
            datareader.__next__()
            try:
                for row in datareader:
                    if len(row) == 17:
                        if not self.db.is_entry_added(row[2]):
                            self.db.add_product(row)
                self.refresh_all_products_windows()
                if self.main_window:
                    self.refresh_main_window()
            except Exception as ex:
                messagebox.showwarning("Error", f'Error: {ex}')
                print(ex)


class DataBaseInterface:
    def __init__(self):
        self.connection = None
        self.cursor = None

    @staticmethod
    def make_query_wrapper(func):
        def wrapper(self, *args):
            try:
                self.open_connection()
                res = func(self, *args)
                self.close_connection()
                return res
            except Exception as ex:
                time.sleep(1)
                print(ex)
                wrapper(self, args)

        return wrapper

    def open_connection(self):
        self.connection = mysql.connector.connect(
            host='162.243.163.205',
            user='user',
            password='akidoDB#12a',
            database='dropship'

        )
        self.cursor = self.connection.cursor()

    def close_connection(self):
        self.connection.commit()
        self.cursor.close()
        self.connection.close()

    @make_query_wrapper
    def check_login_password(self, login, password):
        query_login = f"""SELECT password FROM accounts WHERE login = '{login}'"""
        try:
            self.cursor.execute(query_login)
            db_password = self.cursor.fetchone()
            _ = self.cursor.fetchall()
            if db_password:
                if db_password[0] == password:
                    return True
                messagebox.showwarning("Error", 'Wrong password')
                return False
            messagebox.showwarning("Error", 'Not found login')
            return False
        except Exception as ex:
            print(ex)

    @make_query_wrapper
    def get_all_accounts(self):
        query = """SELECT * FROM accounts"""
        self.cursor.execute(query)
        return self.cursor.fetchall()

    @make_query_wrapper
    def get_user_ids(self, login, password):
        query_id = f"""SELECT ID FROM accounts WHERE login = '{login}' AND password = '{password}'"""
        self.cursor.execute(query_id)
        ids = self.cursor.fetchall()
        return ids

    @make_query_wrapper
    def is_entry_added(self, ebay_id):
        query = f"""SELECT * FROM products WHERE ebay_id = '{ebay_id}'"""
        self.cursor.execute(query)
        return any(self.cursor.fetchall())

    @make_query_wrapper
    def is_any_state(self, state: int):
        query_running = f"""SELECT * FROM products WHERE search_target = {state}"""
        self.cursor.execute(query_running)
        return any(self.cursor.fetchall())

    @make_query_wrapper
    def get_note_by_ebay_id(self, ebay_id):
        query = f"""SELECT note FROM products WHERE ebay_id = '{ebay_id}'"""
        self.cursor.execute(query)
        notes = self.cursor.fetchone()
        _ = self.cursor.fetchall()
        return notes[0]

    @make_query_wrapper
    def get_token_by_user_id(self, user_id):
        query_get_token = f"""SELECT oauth_code FROM accounts WHERE ID = '{user_id}'"""
        self.cursor.execute(query_get_token)
        token = self.cursor.fetchone()
        _ = self.cursor.fetchall()
        return token

    @make_query_wrapper
    def add_check_entry(self, ebay_id, checked_at, ecommerce_price, available):
        query_add_check_entry = f"""
        INSERT INTO products_history VALUES ('{ebay_id}','{available}','{ecommerce_price}',{checked_at})"""

        self.cursor.execute(query_add_check_entry)

    @make_query_wrapper
    def add_product(self, row):
        query_add_entry = f"""
        INSERT INTO products VALUES ('{row[0]}','{row[1]}','{row[2]}','{row[3]}','{row[4]}','{row[5]}','{row[6]}',
        '{row[7]}','{row[8]}','{row[9]}','{row[10]}','{row[11]}','{row[12]}','{row[13]}','{row[14]}','{row[15]}',
        '{row[16]}','{row[17]}','{row[18]}','0','1')"""
        self.cursor.execute(query_add_entry)

    @make_query_wrapper
    def add_account(self, row):
        query_add_entry = f"""
            INSERT INTO accounts VALUES ('{row[0]}','{row[1]}','{row[2]}','{row[3]}')"""
        self.cursor.execute(query_add_entry)

    @make_query_wrapper
    def get_all_products(self):
        query = """SELECT * FROM products"""
        self.cursor.execute(query)
        return self.cursor.fetchall()

    @make_query_wrapper
    def get_all_products_by_user(self, user_id):
        query = f"""SELECT * FROM products WHERE user_id = '{user_id}'"""
        self.cursor.execute(query)
        return self.cursor.fetchall()

    @make_query_wrapper
    def get_availability_by_user_id(self, ebay_id):
        query = f"""
        SELECT avaliable 
        FROM products_history 
        WHERE ebay_id = '{ebay_id}' 
        AND checked_at = (SELECT MAX(checked_at) FROM products_history WHERE ebay_id = '{ebay_id}')"""
        self.cursor.execute(query)
        availability = self.cursor.fetchone()
        _ = self.cursor.fetchall()
        return availability[0]

    @make_query_wrapper
    def edit_availability_by_ebay_id(self, ebay_id, availability):
        availability = 1 if availability else 0
        query = f"""UPDATE products SET result = '{availability}' WHERE ebay_id = '{ebay_id}'"""
        self.cursor.execute(query)

    @make_query_wrapper
    def edit_p_price_by_ebay_id(self, ebay_id, price):
        query = f"""UPDATE products SET p_price = '{price}' WHERE ebay_id = '{ebay_id}'"""
        self.cursor.execute(query)

    @make_query_wrapper
    def del_product(self, ebay_id):
        query = f"""DELETE FROM products WHERE ebay_id = '{ebay_id}' """
        self.cursor.execute(query)

    @make_query_wrapper
    def del_account(self, identification):
        query = f"""DELETE FROM accounts WHERE ID = '{identification}' """
        self.cursor.execute(query)

    @make_query_wrapper
    def start_all(self):
        query_start_all = """UPDATE products SET search_target = 1"""
        self.cursor.execute(query_start_all)

    @make_query_wrapper
    def stop_all(self):
        query_stop_all = """UPDATE products SET search_target = 0"""
        self.cursor.execute(query_stop_all)

    @make_query_wrapper
    def stop_product_by_id(self, ebay_id):
        query = f"""UPDATE products SET search_target = 0 WHERE ebay_id = '{ebay_id}'"""
        self.cursor.execute(query)

    @make_query_wrapper
    def start_product_by_id(self, ebay_id):
        query = f"""UPDATE products SET search_target = 1 WHERE ebay_id = '{ebay_id}'"""
        self.cursor.execute(query)


if __name__ == '__main__':
    dbase = DataBaseInterface()

    log_in = App(dbase)

    log_in.login_window.mainloop()
