import csv
import time
import tkinter as tk
import mysql.connector
from tkinter import filedialog
from tkinter import messagebox


def create_window(height, width, title, resizable=False):
    window = tk.Tk()
    window.title(title)
    window.geometry(f"{width}x{height}")
    window.resizable(resizable, resizable)
    return window


class ProductEntry:
    def __init__(self, app: "App", db: 'DataBaseInterface', frame, parameters, row):
        self.app = app
        self.frame = frame
        self._ebay_id = parameters[2]
        self.state = parameters[19]
        print(self.state)
        self.parameters = parameters
        self.db = db
        self.row = row
        self.save_button = None

        self.entries_collection = []

        self.create_product_entries()
        self.create_save_button()

    def create_product_entries(self):
        column = 0
        for parameter in self.parameters:
            self.entries_collection.append(self.create_product_entry(parameter, column))
            column += 1

    def create_product_entry(self, value, column, bg_color="White"):
        entry_temp = tk.Entry(
            self.frame,
            width=18,
            font=('Arial', 12, 'bold'),
            justify=tk.LEFT,
            background=bg_color,
            fg='Black',
            relief=tk.RAISED)
        entry_temp.insert(1, value)
        entry_temp.grid(column=column, row=self.row)
        return entry_temp

    def create_save_button(self):
        self.save_button = tk.Button(self.frame, text='Save', fg='grey', width=14,
                                     command=self.save_product, font=('Arial', 13, 'bold'))
        self.save_button.grid(row=self.row, column=21)

    def save_product(self):
        self.db.del_product(self._ebay_id)
        self.db.add_product(self.get_all_entries_values())

    def create_start_btn(self):
        start_button = tk.Button(self.frame, text='Start', fg='grey', width=14,
                                 command=self.start_product, font=('Arial', 13, 'bold'))
        start_button.grid(row=self.row, column=22)
        if self.parameters[19] == '1':
            print('start disabled')
            start_button.config(state='disabled')

    def start_product(self):
        self.db.start_product_by_id(self._ebay_id)
        self.app.refresh_all_products_window()

    def create_stop_btn(self):
        stop_button = tk.Button(self.frame, text='Stop', fg='grey', width=14,
                                command=self.stop_product, font=('Arial', 13, 'bold'))
        stop_button.grid(row=self.row, column=23)
        if self.parameters[19] != '1':
            print('stop disabled')

            stop_button.config(state='disabled')

    def stop_product(self):
        self.db.stop_product_by_id(self._ebay_id)
        self.app.refresh_all_products_window()

    def create_delete_btn(self):
        delete_button = tk.Button(self.frame, text='Delete', fg='grey', width=14,
                                  command=self.del_product, font=('Arial', 13, 'bold'))
        delete_button.grid(row=self.row, column=24)

    def del_product(self):
        if tk.messagebox.askyesno('Check', 'Delete?'):
            self.db.del_product(self._ebay_id)
            self.app.refresh_all_products_window()
            self.app.refresh_main_window()

    def get_all_entries_values(self):
        return [entry.get() for entry in self.entries_collection]


class App:

    def __init__(self, db: 'DataBaseInterface'):
        self.db = db
        self.login_window = None
        self.main_window = None
        self.all_products_window = None

        self.login_input = None
        self.pass_input = None

        self.btn_start = None
        self.btn_stop = None
        self.btn_upload = None
        self.btn_show_all = None

        self.all_products_window_main_frame = None
        self.all_products_window_second_frame = None
        self.all_products_window_third_frame = None
        self.all_products_window_canvas = None

        self.all_products_window_scrollbar_x = None
        self.all_products_window_scrollbar_y = None
        self.all_products_window_product_entries = []

        self.user_ids = None

        self.create_login_window()

    def start_all(self):
        self.db.start_all()
        self.refresh_all_products_window()
        if not self.db.is_any_state(0):
            self.btn_stop.config(state='normal')
            self.btn_start.config(state='disabled')

    def stop_all(self):
        self.db.stop_all()
        self.refresh_all_products_window()
        if not self.db.is_any_state(1):
            self.btn_stop.config(state='disabled')
            self.btn_start.config(state='normal')

    def on_closing_window(self, identifier):
        if identifier == "login":
            self.login_window.destroy()
            self.login_window = None
        if identifier == "main":
            self.main_window.destroy()
            self.main_window = None
        if identifier == "all_products":
            self.all_products_window.destroy()
            self.all_products_window = None

    def create_login_window(self):
        if not self.main_window:
            self.login_window = create_window(360, 300, 'Login')
            self.login_window.iconphoto(False, tk.PhotoImage(file='888848.png'))
            self.build_login_window_widgets()
            self.login_window.protocol("WM_DELETE_WINDOW", lambda: self.on_closing_window("login"))

    def create_main_window(self):
        if not self.main_window:
            self.main_window = create_window(360, 300, 'eBay Tool')
            self.main_window.iconphoto(False, tk.PhotoImage(file='888848.png'))
            self.build_main_window_widgets()
            self.main_window.protocol("WM_DELETE_WINDOW", lambda: self.on_closing_window("main"))

    def create_all_products_window(self):
        if not self.all_products_window:
            self.all_products_window = create_window(720, 1280, 'All Products', resizable=True)
            self.build_all_products_window_widgets()
            self.all_products_window.protocol("WM_DELETE_WINDOW", lambda: self.on_closing_window("all_products"))

    def build_login_window_widgets(self):
        self.create_login_label()
        self.create_login_input()
        self.create_password_label()
        self.create_password_input()
        self.create_login_button()

    def build_main_window_widgets(self):
        self.create_upload_button()
        self.create_stop_button()
        self.create_start_button()
        self.create_all_products_button()

    def build_all_products_window_main_frame(self):
        self.all_products_window_main_frame = tk.Frame(self.all_products_window)
        self.all_products_window_main_frame.pack(fill=tk.BOTH, expand=1)

    def build_all_products_window_second_frame(self):
        self.all_products_window_second_frame = tk.Frame(self.all_products_window_main_frame)
        self.all_products_window_second_frame.pack(fill=tk.X, side=tk.BOTTOM)

    def build_all_products_window_canvas(self):
        self.all_products_window_canvas = tk.Canvas(self.all_products_window_main_frame)
        self.all_products_window_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

    def build_all_products_window_scrollbar(self):
        self.all_products_window_scrollbar_x = tk.Scrollbar(self.all_products_window_second_frame, orient=tk.HORIZONTAL,
                                                            command=self.all_products_window_canvas.xview)
        self.all_products_window_scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)

        self.all_products_window_scrollbar_y = tk.Scrollbar(self.all_products_window_main_frame, orient=tk.VERTICAL,
                                                            command=self.all_products_window_canvas.yview)
        self.all_products_window_scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)

    def configure_all_product_window_canvas(self):
        self.all_products_window_canvas.configure(xscrollcommand=self.all_products_window_scrollbar_x.set)
        self.all_products_window_canvas.configure(yscrollcommand=self.all_products_window_scrollbar_y.set)
        self.all_products_window_canvas.bind('<Configure>', lambda e: self.all_products_window_canvas.configure(
            scrollregion=self.all_products_window_canvas.bbox(tk.ALL)))

    def create_all_product_window_third_frame(self):
        self.all_products_window_third_frame = tk.Frame(self.all_products_window_canvas)

    def create_all_product_window_canvas_window(self):
        self.all_products_window_canvas.create_window((0, 0), window=self.all_products_window_third_frame, anchor="nw")

    def build_all_products_window_widgets(self):
        self.all_products_window_product_entries = []

        self.build_all_products_window_main_frame()
        self.build_all_products_window_second_frame()
        self.build_all_products_window_canvas()
        self.build_all_products_window_scrollbar()
        self.configure_all_product_window_canvas()
        self.create_all_product_window_third_frame()
        self.create_all_product_window_canvas_window()
        self.create_label_entries()

        row = 1
        for product in self.db.get_all_products():
            row += 1
            self.add_entry_to_all_product_window(product, row)

        self.create_refresh_all_products_window_btn()
        self.create_add_all_product_window_btn()

    def refresh_main_window(self):
        if self.main_window:
            if self.main_window.winfo_exists():
                for widget in self.main_window.winfo_children():
                    widget.destroy()
                self.build_main_window_widgets()

    def refresh_all_products_window(self):
        if self.all_products_window:
            if self.all_products_window.winfo_exists():
                for widget in self.all_products_window.winfo_children():
                    widget.destroy()

                del self.all_products_window_product_entries
                self.all_products_window_product_entries = []

                self.build_all_products_window_widgets()

    def add_entry_to_all_product_window(self, product, row):
        entry = ProductEntry(self, self.db, self.all_products_window_third_frame, product, row)
        entry.create_save_button()
        entry.create_start_btn()
        entry.create_stop_btn()
        entry.create_delete_btn()
        self.all_products_window_product_entries.append(entry)

    def create_add_all_product_window_btn(self):
        product = [[0], [0], [0], [0], [0], [0], [0], [0], [0], [0], [0], [0], [0], [0], [0], [0], [0], [0], [0], [0],
                   [0]]
        add_all_product_window_btn = tk.Button(self.all_products_window_third_frame, text='Add Entry', fg='grey',
                                               command=lambda: self.add_entry_to_all_product_window(product, (
                                                       self.all_products_window_product_entries[
                                                           -1].row + 1) if self.all_products_window_product_entries else 2),
                                               font=('Arial', 13, 'bold'), width=14)
        add_all_product_window_btn.grid(row=1, column=22)

    def create_refresh_all_products_window_btn(self):
        refresh_btn = tk.Button(self.all_products_window_third_frame, text='Refresh', fg='grey',
                                command=self.refresh_all_products_window, font=('Arial', 13, 'bold'), width=14)
        refresh_btn.grid(row=1, column=21)

    def create_label_entries(self):
        parameters = ['Store Name', 'SKU', 'eBay Item Number', 'EC Site', 'eBayURL', 'purchase price',
                      'Purchase price - Match (1 or 0)', 'Invoicing charges', 'Stock Word', "Stock word-match (1 or 0)",
                      'Watch mode (1 or 0)', 'eBay Shipping', 'Expected profit', 'commission factor',
                      "eBay Price", 'note', 'check-logic', 'eBay automatic linkage function (1 or 0)', "eBay Qty",
                      "search_target", "result"]
        for parameter in parameters:
            tk.Label(
                self.all_products_window_third_frame,
                width=16,
                text=parameter,
                font=('Arial', 12, 'bold'),
                justify=tk.LEFT,
                bg='LightSteelBlue',
                fg='Black',
                relief=tk.RAISED).grid(column=parameters.index(parameter), row=1)

    def create_upload_button(self):
        tk.Button(self.main_window, text='Upload', fg='grey',
                  command=self.upload_file, font=('Arial', 18, 'bold'), ).place(relx=0.1, rely=0.3, anchor='sw')

    def create_start_button(self):
        self.btn_start = tk.Button(self.main_window, text='Start all', fg='Green',
                                   command=self.start_all, font=('Arial', 18, 'bold'))
        self.btn_start.place(relx=0.1, rely=0.65, anchor='sw')

        if not self.db.is_any_state(0):
            self.btn_start.config(state='disabled')

    def create_stop_button(self):
        self.btn_stop = tk.Button(self.main_window, text='Stop all', fg='Red',
                                  command=self.stop_all, font=('Arial', 18, 'bold'))
        self.btn_stop.place(relx=0.1, rely=0.8, anchor='sw')
        if not self.db.is_any_state(1):
            self.btn_stop.config(state='disabled')

    def create_all_products_button(self):
        self.btn_show_all = tk.Button(self.main_window, text='Show all products', fg='grey',
                                      command=self.create_all_products_window, font=('Arial', 18, 'bold'), )
        self.btn_show_all.place(relx=0.1, rely=0.5, anchor='sw')

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
                    if len(row) == 19:
                        if not self.db.is_entry_added(row[2]):
                            self.db.add_product(row)
                if self.all_products_window:
                    self.refresh_all_products_window()
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
    def get_user_ids(self, login, password):
        query_id = f"""SELECT ID FROM accounts WHERE login = '{login}' AND password = '{password}'"""
        self.cursor.execute(query_id)
        ids = self.cursor.fetchall()
        return ids

    @make_query_wrapper
    def is_any_state(self, state: int):
        query_running = f"""SELECT * FROM products WHERE search_target = {state}"""
        self.cursor.execute(query_running)
        return any(self.cursor.fetchall())

    @make_query_wrapper
    def is_entry_added(self, ebay_id):
        query = f"""SELECT * FROM products WHERE ebay_id = '{ebay_id}'"""
        self.cursor.execute(query)
        return any(self.cursor.fetchall())

    @make_query_wrapper
    def get_note_by_ebay_id(self, ebay_id):
        query = f"""SELECT note FROM products WHERE ebay_id = '{ebay_id}'"""
        self.cursor.execute(query)
        notes = self.cursor.fetchone()
        _ = self.cursor.fetchall()
        return notes[0]

    # @make_query_wrapper
    # def get_last_price_by_ebay_id(self, ebay_id):
    #     query = f"""
    #     SELECT ecommerce_price
    #     FROM products_history
    #     WHERE ebay_id = '{ebay_id}'
    #     AND checked_at = (SELECT MAX(checked_at) FROM products_history WHERE ebay_id = '{ebay_id}')"""
    #     self.cursor.execute(query)
    #     last_price = self.cursor.fetchone()
    #     _ = self.cursor.fetchall()
    #     return last_price[0]

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

    # @make_query_wrapper
    # def edit_entry(self, row, ebay_id):
    #
    #     query = f"""
    #     UPDATE products SET
    #     user_id = '{row[0]}', sku = '{row[1]}', ebay_id ='{row[2]}', ec_url ='{row[3]}', ebay_url = '{row[4]}',
    #     p_price = '{row[5]}', p_price_match = '{row[6]}', invoicing_charges = '{row[7]}',stock_word = '{row[8]}',
    #     stock_word_match = '{row[9]}', watch_mode = '{row[10]}', ebay_shipping = '{row[11]}',
    #     expected_profit = '{row[12]}', commission_factor = '{row[13]}', ebay_price = '{row[14]}', note = '{row[15]}',
    #     check_logic = '{row[16]}', ebay_linkage ='{row[17]}', ebay_qty = '{row[18]}' WHERE ebay_id = '{row[2]}'
    #     """
    #     self.cursor.execute(query)

    @make_query_wrapper
    def get_all_products(self):
        query = """SELECT * FROM products"""
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
