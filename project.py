import sys
from PyQt6 import uic
from PyQt6.QtWidgets import QApplication, QMainWindow, QTabWidget, QWidget, QStackedWidget


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
        home_widget = self.tabs.widget(0).widget(0)
        home_widget.addPlace_button.clicked.connect(self.add_place)
        home_widget.search_button.clicked.connect(lambda: self.stack.setCurrentIndex(1))
        search_widget = self.tabs.widget(0).widget(1)
        search_widget.search_button_2.clicked.connect(self.search)
        search_widget.back_button.clicked.connect(lambda: self.stack.setCurrentIndex(0))

        self.tabs.currentChanged.connect(self.tab_changed)

        self.setCentralWidget(self.tabs)

    #при переключении вкладки в стеке виджет меняется на первый
    def tab_changed(self, index):
        current = self.tabs.widget(index)
        if isinstance(current, QStackedWidget):
            current.setCurrentIndex(0)

    #вызов виджета добавдения места
    def add_place(self):
        self.addPlace_form = addPlaceForm(self)
        self.addPlace_form.show()

    #осуществление поиска
    def search(self):
        ...


class addPlaceForm(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.initUI()

    def initUI(self):
        uic.loadUi('AddPlaceWidget.ui', self)


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)

if __name__ == '__main__':
    sys.excepthook = except_hook
    app = QApplication(sys.argv)
    ex = TravelDiary()
    ex.show()
    sys.exit(app.exec())