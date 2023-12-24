import sys
from datetime import datetime
from PyQt5 import uic
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QWidget, QMessageBox, QTableWidgetItem, QTableWidget, QHeaderView
import sqlite3

# База данных приложения
database = 'database/VirtualWallet.sqlite'

# Название окна приложения
window_name = 'Виртуальный кошелёк'

# Размеры окна
SIZE = WIDTH, HEIGHT = 800, 600

# Координаты окна
CORDS = None

# Соединение с базой данных
connection = sqlite3.connect(database)
cur = connection.cursor()

# Список пользователей
USERS_DATA = cur.execute('SELECT * from users').fetchall()
USERS = [i[1] for i in USERS_DATA]

# Список валют
CURR_DATA = cur.execute('SELECT * from currencies').fetchall()

# Словарь для записи месяцев в базу данных
months = {"January": 'Января', "February": "Февраля", "March": "Марта", "April": "Апреля",
          "May": "Мая", "June": "Июня", "July": "Июля", "August": "Августа",
          "September": "Сентября", "October": "Октября", "November": "Ноября", "December": "Декабря"}

# Словарь для валют и их символов
CURRENCIES = {}
for i in CURR_DATA:
    CURRENCIES[i[0]] = i[2]
    CURRENCIES[i[1]] = i[0]


def set_window_cords(window, cords):  # Функция для установки окна на заданные координаты
    global CORDS
    if not cords:

        desktop = QApplication.desktop()
        x = (desktop.width() - window.width()) // 2
        y = (desktop.height() - window.height()) // 2

        window.move(x, y)
        CORDS = window.geometry().x(), window.geometry().y()
    else:
        window.move(*cords)


def set_cords(window):  # Функция установки координат
    global CORDS
    CORDS = window.geometry().x() - 1, window.geometry().y() - 31


def is_correct(pw):  # Функция для проверки пароля
    possible_chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_'
    for password in pw:
        if password.lower() not in possible_chars.lower():
            return False
    return True


class MainPage(QWidget):  # Основное окно программы

    def __init__(self, user_index, curr_acc_index=None):

        self.userIndex = user_index
        self.currAccIndex = curr_acc_index
        self.currAccIndexToHistory = None
        super().__init__()
        uic.loadUi('qt_files/MainForm.ui', self)
        self.initUI()

    def initUI(self):  # Инициализация окна
        self.setWindowIcon(QIcon('../images/icon.png'))
        self.setWindowTitle(window_name)
        set_window_cords(self, CORDS)
        con = sqlite3.connect(database)
        cursor = con.cursor()
        self.username = cursor.execute(f"SELECT username from users where id = {self.userIndex}").fetchall()[0][0]
        self.accounts = cursor.execute(f'SELECT * from accounts where userID = {self.userIndex}').fetchall()
        self.userLabel.setText(f'Пользователь: {self.username}')

        self.is_accounts_none = False  # Флажок наличия счетов

        # Установка счетов в ComboBox
        if self.accounts:
            acc_index = self.currAccIndex

            if acc_index:
                for val in self.accounts:
                    if val[0] == acc_index:
                        self.accountComboBox.addItem(val[1])
                        break

            for value in self.accounts:
                if value[0] == acc_index:
                    continue
                if self.is_accounts_none:
                    self.accountComboBox.removeItem(0)
                    self.is_accounts_none = False
                else:
                    self.accountComboBox.addItem(value[1])
        else:
            self.accountComboBox.addItem('Нет')

        # Подключение кнопок к методам
        self.AccountButton.clicked.connect(self.manipulate_accounts)
        self.changeUserButton.clicked.connect(self.change_user)
        self.addMoneyButton.clicked.connect(self.add_money)
        self.takeMoneyButton.clicked.connect(self.add_money)
        self.historyViewButton.clicked.connect(self.history_show)
        self.accountComboBox.currentTextChanged.connect(self.account_change)

        if self.accounts:
            self.account_change(self.accounts[0][1])
    def manipulate_accounts(self):
        self.close()

        self.map = ManipulateAccountsPage(self.userIndex, self.currAccIndexToHistory)
        self.map.show()

    def history_show(self):  # Метод отображения окна истории
        if self.accounts:
            self.close()
            self.hs = HistoryShowPage(self.currAccIndexToHistory, self.userIndex, self.accountName)
            self.hs.show()

        else:
            self.is_accounts_none = True
            # Всплывающее окно создания первого счёта
            self.addAccountMsgBox = QMessageBox(self)
            self.addAccountMsgBox.addButton("Да", QMessageBox.AcceptRole)
            self.addAccountMsgBox.addButton("Нет", QMessageBox.AcceptRole)
            self.addAccountMsgBox.setWindowTitle(window_name)
            self.addAccountMsgBox.setInformativeText("У вас пока нет счетов, хотите создать счёт?")
            self.addAccountMsgBox.exec()
            if self.addAccountMsgBox.clickedButton().text() == "Да":
                self.addAccountMsgBox.close()
                self.add_account()
            elif self.addAccountMsgBox.clickedButton().text() == "Нет":
                self.addAccountMsgBox.close()

    def add_money(self):  # Метод добавления или снятия денег со счёта
        if self.accounts:
            self.close()
            sign = self.sender().text()
            self.am = AddMoneyPage(self.accounts[self.currAccId], sign)
            self.am.show()
        else:
            self.is_accounts_none = True
            # Всплывающее окно создания первого счёта
            self.addAccountMsgBox = QMessageBox(self)
            self.addAccountMsgBox.addButton("Да", QMessageBox.AcceptRole)
            self.addAccountMsgBox.addButton("Нет", QMessageBox.AcceptRole)
            self.addAccountMsgBox.setWindowTitle(window_name)
            self.addAccountMsgBox.setInformativeText("У вас пока нет счетов, хотите создать счёт?")
            self.addAccountMsgBox.exec()
            if self.addAccountMsgBox.clickedButton().text() == "Да":
                self.addAccountMsgBox.close()
                self.add_account()
            elif self.addAccountMsgBox.clickedButton().text() == "Нет":
                self.addAccountMsgBox.close()

    def change_user(self):  # Метод возвращающий к окну входа
        self.close()
        self.lp = LoginPage()
        self.lp.show()

    def add_account(self):  # Метод отображения окна добавления счёта
        self.close()
        self.ac = AddAccountPage(self.userIndex)
        self.ac.show()

    def account_change(self, account_name):  # метод отвечающий за смену счетов
        if self.accounts:
            if not self.currAccIndex:
                for i, val in enumerate(self.accounts):
                    if val[1] == account_name:
                        self.currAccId = i
                        break
                self.currAccIndex = self.accounts[self.currAccId][0]
            elif self.currAccIndex:
                for i, val in enumerate(self.accounts):
                    if val[0] == self.currAccIndex:
                        self.currAccId = i
                        break
            self.accountName = self.accounts[self.currAccId][1]
            self.amountCount = self.accounts[self.currAccId][2]
            self.comment = self.accounts[self.currAccId][3]
            self.currencyId = self.accounts[self.currAccId][5]
            self.accountAmount.setText(f'{self.accountName}: {self.amountCount}{CURRENCIES[self.currencyId]}')
            self.accountComment.setText(self.comment)
            self.currAccIndexToHistory = self.currAccIndex
            self.currAccIndex = None

    def closeEvent(self, event):  # переопределённый метод закрытия окна
        sender = self.sender()
        if sender is None:
            self.closeMsgBox = QMessageBox(self)
            self.closeMsgBox.addButton("Да", QMessageBox.AcceptRole)
            self.closeMsgBox.addButton("Нет", QMessageBox.AcceptRole)
            self.closeMsgBox.setWindowTitle(window_name)
            self.closeMsgBox.setInformativeText("Вы уверены что хотите закрыть приложение?")
            self.closeMsgBox.exec()
            if self.closeMsgBox.clickedButton().text() == "Да":
                self.closeMsgBox.close()
                event.accept()
            elif self.closeMsgBox.clickedButton().text() == "Нет":
                self.closeMsgBox.close()
                event.ignore()
        set_cords(self)


class LoginPage(QWidget):

    def __init__(self):
        super().__init__()
        uic.loadUi('qt_files/LoginForm.ui', self)
        self.initUI()

    def initUI(self):  # Инициализация окна
        self.setWindowIcon(QIcon('../images/icon.png'))
        set_window_cords(self, CORDS)
        self.setWindowTitle(window_name)
        # Подключение кнопок к методам
        self.AddUserButton.clicked.connect(self.add_user)
        self.LoginButton.clicked.connect(self.log_in)

    def log_in(self):  # Метод входа в аккаунт
        con = sqlite3.connect(database)
        cursor = con.cursor()
        users = cursor.execute('select * from users').fetchall()
        if users:
            for item in users:
                if self.LoginEdit.text() == item[1] and self.PwEdit.text() == item[2]:
                    self.close()
                    self.mp = MainPage(item[0])
                    self.mp.show()
                else:
                    self.ErrorLabel.setText('Неверный логин или пароль!  попробуйте еще раз.')
        else:
            self.ErrorLabel.setText('Неверный логин или пароль!  попробуйте еще раз.')

    def add_user(self):  # Метод добавления пользователя
        name, password = self.LoginEdit_2.text(), self.PwEdit_2.text()
        if name not in USERS:
            if password and name:
                if is_correct(password) and is_correct(name):
                    if len(password) >= 7:
                        self.ErrorLabel_2.setText('')
                        # Всплывающее окно добавления пользователя
                        self.addUserMsgBox = QMessageBox(self)
                        self.addUserMsgBox.addButton("Да", QMessageBox.AcceptRole)
                        self.addUserMsgBox.addButton("Нет", QMessageBox.AcceptRole)
                        self.addUserMsgBox.setWindowTitle(window_name)
                        self.addUserMsgBox.setInformativeText(f"Добавить пользователя {name}?")
                        self.addUserMsgBox.exec()
                        if self.addUserMsgBox.clickedButton().text() == "Да":
                            self.addUserMsgBox.close()
                            self.add_user_to_db()
                        elif self.addUserMsgBox.clickedButton().text() == "Нет":
                            self.addUserMsgBox.close()
                            self.LoginEdit_2.setText('')
                            self.PwEdit_2.setText('')
                    else:
                        self.ErrorLabel_2.setText('Длина пароля должна быть не меньше 7 символов!')
                else:
                    self.ErrorLabel_2.setText('В логине и пароле могут присутствовать только заглавные и строчные '
                                              'буквы латинского алфавита, цифры, и нижнее подчеркивание!')
            else:
                self.ErrorLabel_2.setText('Логин или пароль не должен быть пустым!')
        else:
            self.ErrorLabel_2.setText(f'Имя пользователя {name} уже занято! Введите другое.')

    def add_user_to_db(self):  # Метод добавления пользователя в базу данных
        con = sqlite3.connect(database)
        cursor = con.cursor()
        cursor.execute(f'INSERT INTO users (username, password) '
                       f'VALUES ("{self.LoginEdit_2.text()}", "{self.PwEdit_2.text()}")')
        con.commit()
        USERS.append(self.LoginEdit_2.text())
        self.ErrorLabel_2.setText(f'Пользователь {self.LoginEdit_2.text()} добавлен успешно!')
        self.LoginEdit_2.setText('')
        self.PwEdit_2.setText('')
        self.LoginEdit.setText('')
        self.PwEdit.setText('')
        self.ErrorLabel.setText('')

    def closeEvent(self, event):  # переопределённый метод закрытия окна
        sender = self.sender()
        if sender is None:
            # Всплывающее окно закрытия приложения
            self.closeMsgBox = QMessageBox(self)
            self.closeMsgBox.addButton("Да", QMessageBox.AcceptRole)
            self.closeMsgBox.addButton("Нет", QMessageBox.AcceptRole)
            self.closeMsgBox.setWindowTitle(window_name)
            self.closeMsgBox.setInformativeText("Вы уверены что хотите закрыть приложение?")
            self.closeMsgBox.exec()
            if self.closeMsgBox.clickedButton().text() == "Да":
                self.closeMsgBox.close()
                event.accept()
            elif self.closeMsgBox.clickedButton().text() == "Нет":
                self.closeMsgBox.close()
                event.ignore()
        set_cords(self)


class ManipulateAccountsPage(QWidget):  # Окно управления счетами
    def __init__(self, user_index, curr_acc_id):
        self.userIndex = user_index
        self.accSelected = None
        self.username = None
        self.currAccId = curr_acc_id
        super().__init__()
        uic.loadUi('qt_files/AccountForm.ui', self)
        self.initUI()

    def initUI(self):  # Инициализация окна
        self.setWindowIcon(QIcon('../images/icon.png'))
        self.setWindowTitle(window_name)
        set_window_cords(self, CORDS)
        self.list_update()

        # Подключение кнопок к методам
        self.returnButton.clicked.connect(self.close)
        self.addButton.clicked.connect(self.add_account)
        self.deleteButton.clicked.connect(self.delete_account)
        self.changeButton.clicked.connect(self.change_account_data)
        self.listWidget.currentItemChanged.connect(self.set_curr_account)

        con = sqlite3.connect(database)
        cursor = con.cursor()
        self.acc_ids = cursor.execute(f'SELECT accountId from accounts where userID = {self.userIndex}').fetchall()
        if self.acc_ids:
            if self.currAccId is None:
                self.currAccId = self.acc_ids[0][0]

    def list_update(self):  # Метод обновления списка счетов
        con = sqlite3.connect(database)
        cursor = con.cursor()

        if not self.username:
            self.username = cursor.execute(f"SELECT username from users where id = {self.userIndex}").fetchall()[0][0]
            self.label.setText(f'Счета пользователя: {self.username}')
        self.accounts = cursor.execute(f'SELECT * from accounts where userID = {self.userIndex}').fetchall()

        self.listWidget.clear()
        for item in self.accounts:
            self.listWidget.addItem(item[1])
        if self.accounts:
            self.accSelected = self.accounts[0][1]

    def set_curr_account(self):  # Метод выбора текущего элемента списка счетов
        if self.listWidget.currentItem():
            self.accSelected = self.listWidget.currentItem().text()

    def add_account(self):  # Метод отображения окна добавления счёта
        self.close()
        self.ac = AddAccountPage(self.userIndex)
        self.ac.show()

    def change_account_data(self):  # Метод отображения окна изменения данных счёта
        if self.accounts:
            self.close()
            self.cad = ChangeAccountDataPage(self.accSelected, self.userIndex)
            self.cad.show()
        else:
            self.DelAccountMsgBox = QMessageBox(self)
            self.DelAccountMsgBox.addButton("ОК", QMessageBox.AcceptRole)
            self.DelAccountMsgBox.setWindowTitle(window_name)
            self.DelAccountMsgBox.setInformativeText(f'У вас ещё нет счетов, изменять нечего!')
            self.DelAccountMsgBox.exec()
            if self.DelAccountMsgBox.clickedButton().text() == "ОК":
                self.DelAccountMsgBox.close()

    def delete_account(self):  # Метод удаления счёта
        if self.accounts:
            self.deleteAccMsgBox = QMessageBox(self)
            self.deleteAccMsgBox.addButton("Да", QMessageBox.AcceptRole)
            self.deleteAccMsgBox.addButton("Нет", QMessageBox.AcceptRole)
            self.deleteAccMsgBox.setWindowTitle(window_name)
            self.deleteAccMsgBox.setInformativeText(f"Вы точно хотите удалить {self.accSelected}?")
            self.deleteAccMsgBox.exec()
            if self.deleteAccMsgBox.clickedButton().text() == "Да":
                self.deleteAccMsgBox.close()
                self.delete_acc_from_bd()
            elif self.deleteAccMsgBox.clickedButton().text() == "Нет":
                self.deleteAccMsgBox.close()
        else:
            self.DelAccountMsgBox = QMessageBox(self)
            self.DelAccountMsgBox.addButton("ОК", QMessageBox.AcceptRole)
            self.DelAccountMsgBox.setWindowTitle(window_name)
            self.DelAccountMsgBox.setInformativeText(f'У вас ещё нет счетов, удалять нечего!')
            self.DelAccountMsgBox.exec()
            if self.DelAccountMsgBox.clickedButton().text() == "ОК":
                self.DelAccountMsgBox.close()

    def delete_acc_from_bd(self):  # Метод удаления счёта из базы данных
        con = sqlite3.connect(database)
        cursor = con.cursor()
        cursor.execute(f'DELETE from accounts WHERE userId = "{self.userIndex}" AND name = "{self.accSelected}"')
        con.commit()
        # Всплывающее окно об успешном удалении счёта из базы данных
        self.DelAccountMsgBox = QMessageBox(self)
        self.DelAccountMsgBox.addButton("ОК", QMessageBox.AcceptRole)
        self.DelAccountMsgBox.setWindowTitle(window_name)
        self.DelAccountMsgBox.setInformativeText(f'Счёт {self.accSelected} Успешно удалён!')
        self.DelAccountMsgBox.exec()
        if self.DelAccountMsgBox.clickedButton().text() == "ОК":
            self.DelAccountMsgBox.close()
        self.list_update()
        self.currAccId = None

    def closeEvent(self, event):  # переопределённый метод закрытия окна
        set_cords(self)
        if self.sender():
            if self.sender().text() == 'Вернуться':
                event.accept()
                self.mp = MainPage(self.userIndex, self.currAccId)
                self.mp.show()
            else:
                event.accept()
        else:
            event.accept()
            self.mp = MainPage(self.userIndex, self.currAccId)
            self.mp.show()


class AddAccountPage(QWidget):
    def __init__(self, user_index):
        super().__init__()
        self.userIndex = user_index
        self.acc_id = None
        uic.loadUi('qt_files/AddAccount.ui', self)
        self.initUI()

    def initUI(self):  # Инициализация окна
        self.setWindowIcon(QIcon('../images/icon.png'))
        self.setWindowTitle(window_name)
        set_window_cords(self, CORDS)
        self.addButton.clicked.connect(self.add_account_to_db)
        self.returnButton.clicked.connect(self.close)
        for item in CURR_DATA:
            self.currencyComboBox.addItem(item[1])

    def add_account_to_db(self):  # Метод добавления счёта в базу данных
        nameNotUsed = True
        name = self.NameEdit.text()
        comment = self.CommentEdit.text()
        con = sqlite3.connect(database)
        cursor = con.cursor()
        for item in cursor.execute(f'SELECT name FROM accounts WHERE userId = "{self.userIndex}"').fetchall():
            if item[0] == name:
                nameNotUsed = False
        if name:
            if nameNotUsed:
                if comment:
                    if len(name) >= 4:
                        if len(comment) >= 4:
                            currency_id = CURRENCIES[self.currencyComboBox.currentText()]
                            con = sqlite3.connect(database)
                            cursor = con.cursor()
                            cursor.execute('INSERT INTO accounts (name, amount, comment, userId, currencyId) '
                                           f'VALUES ("{name.capitalize()}", 0, "{comment.capitalize()}", '
                                           f'{self.userIndex}, {currency_id})')
                            con.commit()
                            self.acc_id = cursor.execute('SELECT accountId from accounts').fetchall()[-1][0]

                            # Всплывающее окно об успешном добавлении записи в базу данных
                            self.addAccountMsgBox = QMessageBox(self)
                            self.addAccountMsgBox.addButton("ОК", QMessageBox.AcceptRole)
                            self.addAccountMsgBox.setWindowTitle(window_name)
                            self.addAccountMsgBox.setInformativeText(f'{name} добавлен успешно!')
                            self.addAccountMsgBox.exec()
                            if self.addAccountMsgBox.clickedButton().text() == "ОК":
                                self.addAccountMsgBox.close()
                                self.close()
                        else:
                            self.errorLabel.setText('Длина комментария должна быть не меньше 4 символов!')
                    elif len(comment) >= 6:
                        self.errorLabel.setText('Длина названия должна быть не меньше 4 символов!')
                    else:
                        self.errorLabel.setText('Длина названия и комментария должна быть не меньше 4 символов!')
                else:
                    self.errorLabel.setText('Комментарий не должен быть пустым!')
            else:
                self.errorLabel.setText(f'Название {name} уже занято!')
        elif comment:
            self.errorLabel.setText('Название не должно быть пустым!')
        else:
            self.errorLabel.setText('Название и комментарий не должны быть пустыми!')

    def closeEvent(self, event):  # переопределённый метод закрытия окна
        set_cords(self)
        event.accept()
        self.map = ManipulateAccountsPage(self.userIndex, self.acc_id)
        self.map.show()


class ChangeAccountDataPage(QWidget):  # окно изменения данных счёта
    def __init__(self, account_name, user_index):
        super().__init__()
        self.accountName = account_name
        self.userId = user_index
        self.acc_id = None
        self.currencyChanged = False
        uic.loadUi('qt_files/ChangeAccountData.ui', self)
        self.initUI()

    def initUI(self):  # Инициализация окна
        self.setWindowIcon(QIcon('../images/icon.png'))
        self.setWindowTitle(window_name)
        self.label_4.setText(f'Счёт: {self.accountName}')
        set_window_cords(self, CORDS)

        self.data = cur.execute(f'SELECT accountId, comment, currencyId '
                                f'FROM accounts '
                                f'WHERE userId = {self.userId} AND name = "{self.accountName}"').fetchall()
        self.NameEdit.setPlaceholderText(self.accountName)
        self.CommentEdit.setPlaceholderText(self.data[0][1])
        # Подключение кнопок к методам
        self.changeButton.clicked.connect(self.change_account_data)
        self.returnButton.clicked.connect(self.close)
        self.currencyComboBox.currentTextChanged.connect(self.currency_change)

        for i in range(len(CURR_DATA)):
            if CURR_DATA[i][0] == self.data[0][2]:
                self.currencyComboBox.addItem(CURR_DATA[i][1])
        for item in CURR_DATA:
            if item[0] != self.data[0][2]:
                self.currencyComboBox.addItem(item[1])

    def currency_change(self):  # Метод изменения валюты
        if CURRENCIES[self.currencyComboBox.currentText()] == self.data[0][2]:
            self.currencyChanged = False
        else:
            self.currencyMsgBox = QMessageBox(self)
            self.currencyMsgBox.addButton("Да", QMessageBox.AcceptRole)
            self.currencyMsgBox.addButton("Нет", QMessageBox.AcceptRole)
            self.currencyMsgBox.setWindowTitle(window_name)
            self.currencyMsgBox.setInformativeText("Вы точно хотите изменить валюту?")
            self.currencyMsgBox.exec()
            if self.currencyMsgBox.clickedButton().text() == "Да":
                self.currencyMsgBox.close()
                self.currencyChanged = True
            elif self.currencyMsgBox.clickedButton().text() == "Нет":
                self.currencyMsgBox.close()

    def change_account_data(self):  # Метод изменения счёта
        nameNotUsed = True
        if self.NameEdit.text():
            name = self.NameEdit.text()
        else:
            name = self.accountName
        if self.CommentEdit.text():
            comment = self.CommentEdit.text()
        else:
            comment = self.data[0][1]
        con = sqlite3.connect(database)
        cursor = con.cursor()
        for item in cursor.execute(f'SELECT name FROM accounts WHERE userId = "{self.userId}"').fetchall():
            if item[0] == name:
                nameNotUsed = False
        if name == self.accountName:
            nameNotUsed = True

        if nameNotUsed:
            if self.accountName != name or self.data[0][1] != comment or self.currencyChanged:
                if len(name) >= 4:
                    if len(comment) >= 4:
                        comment = comment.capitalize()
                        if self.currencyChanged:
                            currency_id = CURRENCIES[self.currencyComboBox.currentText()]
                        else:
                            currency_id = self.data[0][2]
                        con = sqlite3.connect(database)
                        cursor = con.cursor()
                        cursor.execute(f'UPDATE accounts '
                                       f'SET name = "{name}", comment = "{comment}", currencyId = {currency_id} '
                                       f'WHERE accountId = {self.data[0][0]}')
                        con.commit()
                        self.acc_id = cursor.execute(f'SELECT accountId FROM accounts '
                                                     f'WHERE name = "{name}" '
                                                     f'AND accountId = {self.data[0][0]}').fetchall()[0][0]
                        # Всплывающее окно об успешном изменении записи базы данных
                        self.addAccountMsgBox = QMessageBox(self)
                        self.addAccountMsgBox.addButton("ОК", QMessageBox.AcceptRole)
                        self.addAccountMsgBox.setWindowTitle("Мой Кошелёк")
                        self.addAccountMsgBox.setInformativeText(f'{self.accountName} изменён успешно!')
                        self.addAccountMsgBox.exec()
                        if self.addAccountMsgBox.clickedButton().text() == "ОК":
                            self.addAccountMsgBox.close()
                            self.close()
                    else:
                        self.errorLabel.setText('Длина комментария должна быть не меньше 4 символов!')
                elif len(comment) >= 6:
                    self.errorLabel.setText('Длина названия должна быть не меньше 4 символов!')
                else:
                    self.errorLabel.setText('Длина названия и комментария должна быть не меньше 4 символов!')

            else:
                self.errorLabel.setText(f'Вы ничего не поменяли!')
        else:
            self.errorLabel.setText(f'Название {name} уже занято!')

    def closeEvent(self, event):  # переопределённый метод закрытия окна
        set_cords(self)
        event.accept()
        self.map = ManipulateAccountsPage(self.userId, self.acc_id)
        self.map.show()


class AddMoneyPage(QWidget):
    def __init__(self, account, sign):
        self.account = account
        self.sign = sign
        super().__init__()
        uic.loadUi('qt_files/Manipulate.ui', self)
        self.initUI()

    def initUI(self):  # Инициализация окна
        self.setWindowIcon(QIcon('../images/icon.png'))
        self.setWindowTitle(window_name)
        set_window_cords(self, CORDS)
        self.amount = self.account[2]
        self.amount = self.account[2]
        self.name = self.account[1]
        self.accId = self.account[0]
        self.currency = CURRENCIES[self.account[5]]
        if self.sign == '-':
            self.sumLabel.setText('Сумма снятия:')
            self.acceptButton.setText('Снять')
            self.sourceLabel.setText('Цель снятия:')
        self.accountLabel.setText(f'{self.name}: {self.amount}{self.currency}')
        self.currLabel.setText(self.currency)
        # Подключение кнопок к методам
        self.returnButton.clicked.connect(self.close)
        self.acceptButton.clicked.connect(self.add_money_to_db)

    def add_money_to_db(self):  # Метод добавления данных о пополнении или снятии денег в базу данных
        addValue = self.sumSpinBox.value()
        source = self.sourceEdit.text()

        time = datetime.now()

        if not source:
            source = 'Не указан'
        addValue = str(addValue)
        addValue.replace(',', '.')
        addValue = float(addValue)

        add_sum = round(eval(f'{self.amount} {self.sign} {addValue}'), 2)
        if addValue != 0:
            if len(source) >= 4 or len(source) == 0:
                if add_sum < 0:
                    self.errorLabel.setText(f"Не достаточно средств! ({abs(add_sum)}{self.currency})")
                else:
                    con = sqlite3.connect(database)
                    cursor = con.cursor()
                    cursor.execute(f"UPDATE accounts "
                                   f"SET amount = {add_sum} "
                                   f"WHERE accountId = {self.accId}")
                    cursor.execute("INSERT INTO earnings (sum, source, time, currAmount, accountId) "
                                   f'VALUES ("{self.sign}{addValue}{self.currency}", "{source.capitalize()}", '
                                   f'"{str(time)[:19]}", {add_sum}, {self.accId})')
                    con.commit()

                    if self.sign == '-':
                        info = f'{addValue}{self.currency} сняты со счёта успешно!'
                    else:
                        info = f'{self.name} пополнен(a) на {addValue}{self.currency} успешно!'
                    # Всплывающее окно об успешном добавлении записи в базу данных
                    self.addMoneyMsgBox = QMessageBox(self)
                    self.addMoneyMsgBox.addButton("ОК", QMessageBox.AcceptRole)
                    self.addMoneyMsgBox.setWindowTitle(window_name)
                    self.addMoneyMsgBox.setInformativeText(info)
                    self.addMoneyMsgBox.exec()
                    if self.addMoneyMsgBox.clickedButton().text() == "ОК":
                        self.addMoneyMsgBox.close()
                        self.close()
            elif len(source) < 6:
                if self.sign == '-':
                    self.errorLabel.setText(f"Цель снятия должна быть не меньше 4 символов!")
                elif self.sign == '+':
                    self.errorLabel.setText(f"Источник дохода должен быть не меньше 4 символов!")
        else:
            if self.sign == '-':
                self.errorLabel.setText(f"Сумма снятия не должна быть равной нулю!")
            elif self.sign == '+':
                self.errorLabel.setText(f"Сумма пополнения не должна быть равной нулю!")

    def closeEvent(self, event):  # переопределённый метод закрытия окна
        set_cords(self)
        self.mp = MainPage(self.account[4], curr_acc_index=self.accId)
        self.mp.show()
        event.accept()


class HistoryShowPage(QWidget):
    def __init__(self, id, userid, name):
        super().__init__()
        self.name = name
        self.userId = userid
        self.accId = id
        uic.loadUi('qt_files/HistoryView.ui', self)
        self.initUI()

    def initUI(self):  # Инициализация окна
        self.setWindowIcon(QIcon('../images/icon.png'))
        self.setWindowTitle(window_name)
        set_window_cords(self, CORDS)
        con = sqlite3.connect(database)
        cursor = con.cursor()
        accData = cursor.execute(f"SELECT amount, currencyId "
                                 f"FROM accounts "
                                 f"WHERE accountId = {self.accId}").fetchall()[0]
        currencySymbol = cursor.execute(f"SELECT symbol "
                                        f"FROM currencies "
                                        f"WHERE currencyId = {accData[1]}").fetchall()[0][0]
        res = cursor.execute(f"SELECT source, sum, time "
                             f"FROM earnings "
                             f"WHERE accountId = {self.accId}").fetchall()
        # Инициализация таблицы QTableWidget
        if res:
            res.sort(key=lambda x: datetime.strptime(x[2], '%Y-%m-%d %H:%M:%S'), reverse=True)

            self.label.setText(f'История: {self.name} {accData[0]}{currencySymbol}')
            self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            self.tableWidget.horizontalHeader().setMinimumSectionSize(0)
            self.tableWidget.setEditTriggers(QTableWidget.NoEditTriggers)
            self.tableWidget.setRowCount(len(res))
            self.tableWidget.setColumnCount(len(res[0]))
            self.tableWidget.setHorizontalHeaderLabels(('Источник/Цель', 'Сумма', 'Дата'))
            for i, elem in enumerate(res):
                for j, val in enumerate(elem):
                    if j == 0:
                        if val == '':
                            val = 'Не указан'
                    elif j == 2:
                        # Получение текущей даты и времени
                        time = datetime.strptime(val, '%Y-%m-%d %H:%M:%S')

                        day_of_the_month = time.strftime("%d")
                        month = time.strftime("%B")
                        format_of_time = time.strftime("%H:%M:%S")

                        full_date = f'{format_of_time} {day_of_the_month} {months[month]} '

                        val = full_date

                    self.tableWidget.setItem(i, j, QTableWidgetItem(str(val)))

        else:
            self.label.setText(f'История {self.name} пуста')

        self.returnButton.clicked.connect(self.close)

    def closeEvent(self, event):  # переопределённый метод закрытия окна
        set_cords(self)
        self.mp = MainPage(self.userId, curr_acc_index=self.accId)
        self.mp.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    lp = LoginPage()
    lp.show()
    sys.exit(app.exec())
