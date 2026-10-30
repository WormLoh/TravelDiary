import os
import sys
import random
import sqlite3
from PyQt6 import uic
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QApplication, QMainWindow, QTabWidget, QWidget, QStackedWidget, QFileDialog, QMessageBox

#функция которая вытаскивает blob файлы из базы данных и передаёт данный в QPixmap
def pic_from_db(id):
    con = sqlite3.connect('travel.db')
    cur = con.cursor()
    record = cur.execute("""SELECT photo FROM places_photos WHERE id = ?""", (str(id),)).fetchone()
    pict_binary = record[0]
    pixmap = QPixmap()
    pixmap.loadFromData(pict_binary)
    con.close()
    return pixmap


#класс основного окна приложения
class TravelDiary(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Дневник Путешествий")
        self.setFixedSize(1474, 900)

        # создание вкладок
        self.tabs = QTabWidget()

        # создание стек виджета
        self.stack = QStackedWidget()
        self.home_tab = QWidget()
        uic.loadUi('HomeWidget.ui', self.home_tab)
        self.stack.addWidget(self.home_tab)
        self.search_widget = QWidget()
        uic.loadUi('search.ui', self.search_widget)
        self.stack.addWidget(self.search_widget)

        self.diary_tab = QWidget()
        uic.loadUi('DiaryWidget.ui', self.diary_tab)
        self.wishlist_tab = QWidget()
        uic.loadUi('WishlistWidget.ui', self.wishlist_tab)

        #добавление вкладок
        self.tabs.addTab(self.stack, "Главная")
        self.tabs.addTab(self.diary_tab, "Дневник")
        self.tabs.addTab(self.wishlist_tab, "Вишлист")

        #добавление зависимостей
        self.home_widget = self.tabs.widget(0).widget(0)
        self.home_widget.addPlace_button.clicked.connect(self.add_place)
        self.home_widget.search_button.clicked.connect(lambda: self.stack.setCurrentIndex(1))
        self.home_widget.places_buttons.buttonClicked.connect(self.place_card)
        self.home_widget.logOut_button.clicked.connect(self.log_out)
        self.home_widget.log_button.clicked.connect(self.reg)
        search_widget = self.tabs.widget(0).widget(1)
        search_widget.search_button_2.clicked.connect(self.search)
        search_widget.back_button.clicked.connect(lambda: self.stack.setCurrentIndex(0))

        self.tabs.currentChanged.connect(self.tab_changed)
        self.setCentralWidget(self.tabs)
        self.random_places()

        self.reg = False
        if os.path.exists('TravelDiaryReg.txt'):
            with open('TravelDiaryReg.txt', mode='r', encoding='utf-8') as f:
                login = f.readline().rstrip()
                password = f.readline().rstrip()
            con = sqlite3.connect('travel.db')
            cur = con.cursor()
            user = cur.execute("""SELECT * FROM users WHERE login = ?""", (str(login),)).fetchone()
            con.close()
            if user is None:
                self.home_widget.logOut_button.hide()
            else:
                users_password = user[2]
                if password != users_password:
                    self.home_widget.logOut_button.hide()
                else:
                    self.receive_login(login)
        else:
            self.home_widget.logOut_button.hide()

    #открытие окна регистрации
    def reg(self):
        self.reg_form = RegForm(self)
        self.reg_form.show()

    #возврат логина из окна регистрации
    def receive_login(self, login):
        self.home_widget.log_button.hide()
        self.home_widget.logOut_button.show()
        self.home_widget.login.setText(login)
        self.reg = True

    #выход из аккаунта
    def log_out(self):
        answer = QMessageBox.question(
            self,
            'Подтверждение',
            'Вы уверены, что хотите выйти из аккаунта?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No  # Кнопка по умолчанию
        )

        if answer == QMessageBox.StandardButton.Yes:
            os.remove('TravelDiaryReg.txt')
            self.home_widget.logOut_button.hide()
            self.home_widget.log_button.show()
            self.home_widget.login.setText("")
            self.reg = False
        else:
            QMessageBox.information(self, 'Отмена', 'Операция отменена.')

    # выбор 3 схучайных мест на главном экране
    def random_places(self):
        con = sqlite3.connect("travel.db")
        cur = con.cursor()
        ids = [id[0] for id in cur.execute("SELECT id FROM places").fetchall()]
        random_ids = random.sample(ids, 3)
        for i in range(1, len(random_ids) + 1):
            place = cur.execute("""SELECT name, info FROM places 
                                       WHERE id = ?""", (str(random_ids[i - 1]),)).fetchone()
            photos = [id[0] for id in cur.execute("""SELECT id FROM places_photos 
                                                         WHERE place = ?""",
                                                      (str(random_ids[i - 1]),)).fetchall()]
            match i:
                case 1:
                    self.home_widget.place1_name.setText(place[0])
                    self.home_widget.place1_info.setPlainText(place[1][:345] + '...')
                    self.home_widget.place1_photo.setPixmap(pic_from_db(photos[0]))
                    self.home_widget.place1_photo.setScaledContents(True)
                case 2:
                    self.home_widget.place2_name.setText(place[0])
                    self.home_widget.place2_info.setPlainText(place[1][:345] + '...')
                    self.home_widget.place2_photo.setPixmap(pic_from_db(photos[0]))
                    self.home_widget.place2_photo.setScaledContents(True)
                case 3:
                    self.home_widget.place3_name.setText(place[0])
                    self.home_widget.place3_info.setPlainText(place[1][:345] + '...')
                    self.home_widget.place3_photo.setPixmap(pic_from_db(photos[0]))
                    self.home_widget.place3_photo.setScaledContents(True)
        con.close()

    #при переключении вкладки в стеке виджет меняется на первый
    def tab_changed(self, index):
        current = self.tabs.widget(index)
        if isinstance(current, QStackedWidget):
            current.setCurrentIndex(0)

    #вызов виджета добавдения места
    def add_place(self):
        self.addPlace_form = AddPlaceForm()
        self.addPlace_form.show()

    #вызов виджета карточки места
    def place_card(self, place):
        con = sqlite3.connect("travel.db")
        cur = con.cursor()
        if place is self.home_widget.place1:
            id = cur.execute("""SELECT id FROM places WHERE name = ?""",
                             (self.home_widget.place1_name.text(),)).fetchone()
        elif place is self.home_widget.place2:
            id = cur.execute("""SELECT id FROM places WHERE name = ?""",
                             (self.home_widget.place2_name.text(),)).fetchone()
        else:
            id = cur.execute("""SELECT id FROM places WHERE name = ?""",
                             (self.home_widget.place3_name.text(),)).fetchone()
        con.close()
        self.PlaceCard_form = PlaceCardForm(self, id, self.reg, self.home_widget.login.text())
        self.PlaceCard_form.show()

    #осуществление поиска
    def search(self):
        ...


class RegForm(QWidget):
    def __init__(self, parent_form):
        super().__init__()
        uic.loadUi('Reg.ui', self)
        self.setWindowTitle("Регистрация")

        self.parent_form = parent_form

        self.reg_button.clicked.connect(self.reg)
        self.log_button.clicked.connect(self.log)

    def make_login_txt(self):
        with open('TravelDiaryReg.txt', mode='w', encoding='utf-8') as f:
            print(self.login_line.text(), file=f)
            print(self.password_line.text(), file=f)

    def reg(self):
        if not self.login_line.text():
            QMessageBox.information(self,'Информация','Введите логин❗')
        elif  not self.password_line.text():
            QMessageBox.information(self, 'Информация', 'Введите пароль❗')
        else:
            try:
                con = sqlite3.connect('travel.db')
                cur = con.cursor()
                cur.execute("""INSERT INTO users (login, password) VALUES (?, ?) """,
                            (self.login_line.text(), self.password_line.text()))
                con.commit()
                con.close()
                self.make_login_txt()
                self.reg_done(self.login_line.text())
            except sqlite3.IntegrityError:
                QMessageBox.information(self,'Информация','Логин уже занят❗')

    def log(self):
        if not self.login_line.text():
            QMessageBox.information(self,'Информация','Введите логин❗')
        elif  not self.password_line.text():
            QMessageBox.information(self, 'Информация', 'Введите пароль❗')
        else:
            con = sqlite3.connect('travel.db')
            cur = con.cursor()
            user = cur.execute("""SELECT * FROM users WHERE login = ?""", (self.login_line.text(),)).fetchone()
            con.close()
            if user is None:
                QMessageBox.information(self,'Информация','Логин не существует❗')
            else:
                password = user[2]
                if self.password_line.text() != password:
                    QMessageBox.information(self,'Информация','Неверный пароль❗')
                else:
                    self.make_login_txt()
                    self.reg_done(self.login_line.text())

    def reg_done(self, login):
        self.parent_form.receive_login(login)
        self.close()


#класс виджета добавления места
class AddPlaceForm(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        uic.loadUi('AddPlaceWidget.ui', self)
        self.setWindowTitle("Карточка добавления места")


#класс виджета карточки места
class PlaceCardForm(QWidget):
    def __init__(self, *args):
        super().__init__()
        self.initUI(args)

    def initUI(self, args):
        uic.loadUi('PlaceCard.ui', self)
        self.setWindowTitle("Карточка места")

        self.id = args[1][0]
        self.reg = args[2]
        self.login = args[3]
        self.changePhoto_buttons.buttonClicked.connect(self.change_photo)
        self.addToWishlist_button.clicked.connect(self.addPlaceToWishlist)
        self.makeList_button.clicked.connect(self.make_list)
        self.setPlace(self.id)
        self.change_photo(self)

    #установка места при запуске виджета
    def setPlace(self, id):
        con = sqlite3.connect("travel.db")
        cur = con.cursor()
        self.curr_place = cur.execute("""SELECT * FROM places WHERE id = ?""", (str(id),)).fetchone()
        self.curr_country = cur.execute("""SELECT name FROM countries WHERE id = ?""",
                                        (str(self.curr_place[2]),)).fetchone()
        self.currPlacePhotos_ids = [id[0] for id in cur.execute("""SELECT id FROM places_photos 
                                                         WHERE place = ?""",
                                                      (str(id),)).fetchall()]
        con.close()
        self.curr_photo_id = 0
        self.place_name.setText(self.curr_place[1])
        self.country.setText('Страна: ' + self.curr_country[0])
        self.location.setText('Местоположение: ' + self.curr_place[3])
        self.location.setWordWrap(True)
        self.info.setPlainText(self.curr_place[4])
        self.info.setReadOnly(True)

    #смена фотографий на кнопочки влево и вправо
    def change_photo(self, sender):
        if sender is self.right_button:
            if self.curr_photo_id < len(self.currPlacePhotos_ids) - 1:
                self.curr_photo_id = self.curr_photo_id + 1
                self.photo.setPixmap(pic_from_db(self.currPlacePhotos_ids[self.curr_photo_id]))
                self.photo.setScaledContents(True)
        elif sender is self.left_button:
            if self.curr_photo_id > 0:
                self.curr_photo_id = self.curr_photo_id - 1
                self.photo.setPixmap(pic_from_db(self.currPlacePhotos_ids[self.curr_photo_id]))
                self.photo.setScaledContents(True)
        else:
            self.photo.setPixmap(pic_from_db(self.currPlacePhotos_ids[0]))
            self.photo.setScaledContents(True)

    #добавление места в вишлист
    def addPlaceToWishlist(self):
        if not self.reg:
            QMessageBox.information(self, 'Информация', 'Вы не зарегестрированы❗')
        else:
            con = sqlite3.connect('travel.db')
            cur = con.cursor()
            user_id =  cur.execute("""SELECT id FROM users WHERE login = ?""", (self.login,)).fetchone()[0]
            in_wishlist = cur.execute("""SELECT * FROM users_wishlists WHERE user = ? and place = ?""",
                                      (user_id, self.id)).fetchone()
            if in_wishlist is None:
                cur.execute("""INSERT INTO users_wishlists (place, user) VALUES (?, ?) """, (self.id, user_id))
                con.commit()
                con.close()
                QMessageBox.information(self, 'Информация', 'Место добавлено вишлист 👍')
            else:
                QMessageBox.information(self,'Информация','Место уже в вишлисте 👍')


    #создание записи в дневнике
    def make_list(self):
        if not self.reg:
            QMessageBox.information(self, 'Информация', 'Вы не зарегестрированы❗')
        else:
           self.addPlace_form = AddDiaryListForm(self, self.curr_place)
           self.addPlace_form.show()
           self.close()


class AddDiaryListForm(QWidget):
    def __init__(self, *args):
        super().__init__()
        self.initUI(args)

    def initUI(self, args):
        uic.loadUi('AddDiaryList.ui', self)
        self.setWindowTitle("Добавь заметку в дневник")

        self.place_for_add = args[1]
        self.place_name.setText(self.place_for_add[1])
        self.photos = ''
        self.addPhoto_button.clicked.connect(self.add_photo)
        self.addList_button.clicked.connect(self.add_lict)

    def add_photo(self):
        self.photos, _ = QFileDialog.getOpenFileNames(
            self, 'Выберите файлы', '',
            'Картинки (*.jpg *.png);;Все файлы (*)')


    def add_lict(self):
        if self.photos:
            print(self.photos)


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)

if __name__ == '__main__':
    sys.excepthook = except_hook
    app = QApplication(sys.argv)
    ex = TravelDiary()
    ex.show()
    sys.exit(app.exec())