import sys
from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QWidget, QApplication, QDateEdit, QLineEdit,QComboBox,QPushButton,QTableWidget,QVBoxLayout,QHBoxLayout,QLabel,QTableWidgetItem,QMessageBox,QDialog
from PyQt6.QtSql import QSqlDatabase , QSqlQuery
from PyQt6.QtCore import QDate

class ExpenseApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Expense with DB")
        self.resize(550,500)

        # Widgets
        self.date_box = QDateEdit()
        self.date_box.setDate(QDate.currentDate())
        self.dropdown = QComboBox()
        self.amount = QLineEdit()
        self.desc = QLineEdit()

        self.add_btn = QPushButton("Add Expense")
        self.del_btn = QPushButton("Delete Expense")
        self.update_btn = QPushButton("Update Expense")

        self.add_btn.clicked.connect(self.add_expense)
        self.del_btn.clicked.connect(self.del_expense)
        self.update_btn.clicked.connect(self.gotoUpdateWindow)

        # Table layout
        self.table = QTableWidget()
        self.table.setColumnCount(5) # id,date,amt.desc
        self.header_name = ["Id","Date","Category","Amount","Description"]
        self.table.setHorizontalHeaderLabels(self.header_name)

        # Dropdown
        self.dropdown_items = ["Food","Transportation","Rent","Shopping","Entertainment","Bills","Other"]
        self.dropdown.addItems(self.dropdown_items)
        
        # Master layout
        self.master_layout = QVBoxLayout()
        self.row1 = QHBoxLayout()
        self.row2 = QHBoxLayout()
        self.row3 = QHBoxLayout()

        # row 1
        self.row1.addWidget(QLabel("Date :"))
        self.row1.addWidget(self.date_box)
        self.row1.addWidget(QLabel("Category :"))
        self.row1.addWidget(self.dropdown)

        # row 2
        self.row2.addWidget(QLabel("Amount :"))
        self.row2.addWidget(self.amount)
        self.row2.addWidget(QLabel("Description :"))
        self.row2.addWidget(self.desc)

        # row 3
        self.row3.addWidget(self.add_btn)
        self.row3.addWidget(self.del_btn)
        self.row3.addWidget(self.update_btn)

        self.master_layout.addLayout(self.row1)
        self.master_layout.addLayout(self.row2)
        self.master_layout.addLayout(self.row3)

        self.master_layout.addWidget(self.table)

        # adding master layout to main window (ie) ExpenseApp class
        self.setLayout(self.master_layout)

        self.load_table()

    def load_table(self):
        self.table.setRowCount(0)
        query = QSqlQuery("SELECT * FROM expense_t")
        row = 0
        while query.next():
            expense_id = query.value(0)
            date = query.value(1)
            category = query.value(2)
            amount = query.value(3)
            description = query.value(4)

            # Add values to Table in DB
            self.table.insertRow(row)
            self.table.setItem(row,0,QTableWidgetItem(str(expense_id)))
            self.table.setItem(row,1,QTableWidgetItem(date))
            self.table.setItem(row,2,QTableWidgetItem(category))
            self.table.setItem(row,3,QTableWidgetItem(str(amount)))
            self.table.setItem(row,4,QTableWidgetItem(description))

            row += 1
    
    def add_expense(self):
        date = self.date_box.date().toString("dd-MM-yyyy")
        category = self.dropdown.currentText()
        amount = self.amount.text()
        desc = self.desc.text()

        if amount == "" or desc == "" or not amount.isdigit():
            QMessageBox.warning(self,"Empty Fields!","Please enter values in the empty field.")
            return
            
        query = QSqlQuery()
        query.prepare("""
            INSERT INTO expense_t (date, category, amount, description)
            VALUES (?, ?, ?, ?)
        """)
        query.addBindValue(date)
        query.addBindValue(category)
        query.addBindValue(amount)
        query.addBindValue(desc)
        query.exec()

        # if query.exec():
        #     QMessageBox.information(self, "Success", "Expense added successfully.")
        # else:
        #     QMessageBox.critical(self, "Error", "Could not add expense.")

        # Reset the old values
        self.date_box.setDate(QDate.currentDate())
        self.dropdown.setCurrentIndex(0)
        self.amount.clear()
        self.desc.clear()

        self.load_table()

    def del_expense(self):
        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self,"No Expense Chosen!","Please choose an expense to delete.")
            return
        # category = self.table.item(selected_row,2).text()
        expense_id = int(self.table.item(selected_row,0).text())
        confirm = QMessageBox.question(self,"Are you sure?","Do you really want to delete this the Expense ?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if confirm == QMessageBox.StandardButton.No:
            return
        
        query = QSqlQuery()
        query.prepare("DELETE FROM expense_t WHERE id = ?")
        query.addBindValue(expense_id)
        query.exec()

        self.load_table()

    def gotoUpdateWindow(self):
        selected_row = self.table.currentRow()
        
        if selected_row == -1:
            QMessageBox.warning(self, "No Expense Chosen!", "Please choose an expense to update.")
            return
        
        expense_id = int(self.table.item(selected_row,0).text())
        date = self.table.item(selected_row,1).text()
        category = self.table.item(selected_row,2).text()
        amount = self.table.item(selected_row,3).text()
        description = self.table.item(selected_row,4).text()

        updatewindow = UpdateWindow(expense_id,date,category,amount,description)
        # updatewindow.exec()
        # widget.addWidget(updatewindow)
        # widget.setCurrentIndex(widget.currentIndex()+1)
        if updatewindow.exec() == QDialog.accepted:
            self.load_table()

class UpdateWindow(QDialog):
    def __init__(self, expense_id, date, category, amount, description):
        super().__init__()
        self.setWindowTitle("Update Expense")
        # self.resize(550,500)

        # Building Ui component
        self.date = QDateEdit()
        self.category = QComboBox()
        self.amount = QLineEdit()
        self.description = QLineEdit()
        self.update_btn = QPushButton("Update")
        self.cancel_btn = QPushButton("Cancel")
        
        # Adding values to category
        self.dropdown_items = ["Food","Transportation","Rent","Shopping","Entertainment","Bills","Other"]
        self.category.addItems(self.dropdown_items)
        
        # inserting values from prev window to this window
        self.expense_id = expense_id
        self.date.setDate(QDate.fromString(date,"dd-MM-yyyy"))
        self.category.setCurrentText(category)
        self.amount.setText(amount)
        self.description.setText(description)

        # connecting btns
        self.update_btn.clicked.connect(self.update_expense)
        self.cancel_btn.clicked.connect(self.reject)

        self.initUI()

    def initUI(self):
        self.update_layout = QVBoxLayout()
        self.row1 = QHBoxLayout()
        self.row2 = QHBoxLayout()
        self.row3 = QHBoxLayout()

        self.row1.addWidget(QLabel("Date :"))
        self.row1.addWidget(self.date)
        self.row1.addWidget(QLabel("Category :"))
        self.row1.addWidget(self.category)

        self.row2.addWidget(QLabel("Amount :"))
        self.row2.addWidget(self.amount)
        self.row2.addWidget(QLabel("Description :"))
        self.row2.addWidget(self.description)

        self.row3.addWidget(self.update_btn)
        self.row3.addWidget(self.cancel_btn)

        self.update_layout.addLayout(self.row1)
        self.update_layout.addLayout(self.row2)
        self.update_layout.addLayout(self.row3)

        self.setLayout(self.update_layout)

    def update_expense(self):
        date = self.date.date().toString("dd-MM-yyyy")
        category = self.category.currentText()
        amount = float(self.amount.text())
        description = self.description.text()

        if amount == "" or description == "":
            QMessageBox.warning(self, "Empty Fields!", "Please enter values in the empty fields.")
            return
        
        query = QSqlQuery()
        query.prepare("""
                    UPDATE expense_t 
                    SET date = ?, category = ?, amount = ?, description = ?
                    WHERE id = ?
        """)
        query.addBindValue(date)
        query.addBindValue(category)
        query.addBindValue(float(amount))
        query.addBindValue(description)
        query.addBindValue(self.expense_id)
        query.exec()

        if not query.exec():
            QMessageBox.critical(self, "Error", "Could not update expense.")
            return
         
        self.accept() 

    # def gotoExpenseApp(self):
    #     self.accept()
        # expenseapp = ExpenseApp()
        # widget.addWidget(expenseapp)
        # widget.setCurrentIndex(widget.currentIndex()-1)

if __name__ == '__main__':        
    app = QApplication([])

    # Create DB
    db = QSqlDatabase.addDatabase("QSQLITE")
    db.setDatabaseName("expense.db")

    if not db.open():
        QMessageBox.critical(None,"Error","Could not open our DB")
        sys.exit(1)

    query = QSqlQuery()
    query.exec("""
        CREATE TABLE IF NOT EXISTS expense_t (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            category TEXT,
            amount REAL,
            description TEXT
        )
    """)


    widget = QtWidgets.QStackedWidget()
    mainwindow = ExpenseApp()
    # updatewindow = UpdateWindow()
    widget.addWidget(mainwindow)
    # widget.addWidget(updatewindow)
    
    widget.show()
    sys.exit(app.exec())


# def app():
#     app = QApplication(sys.argv)
#     win = ExpenseApp()
#     win.show()
#     sys.exit(app.exec())

# app()
