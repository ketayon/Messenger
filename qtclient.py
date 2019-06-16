#! /usr/bin/python

import sys
from PyQt5 import QtWidgets
import design

from twisted.internet.protocol import ClientFactory
from twisted.protocols.basic import LineOnlyReceiver


class ChatClient(LineOnlyReceiver):
    """
    Класс для работы с подключением к серверу
    """
    factory: 'ChatFactory'

    def __init__(self, factory):
        """
        Фабрика для последующего обращения
        """
        self.factory = factory

    def connectionMade(self):
        """
        Обработчик установки соединения с сервером
        """
        self.factory.window.protocol = self  # запись в окно приложения текущий протокол

    def lineReceived(self, line):
        """
        Обработчик получения новой строки от сервера
        """
        message = line.decode()
        self.factory.window.plainTextEdit.appendPlainText(message)  # добавить в поле сообщений


class ChatFactory(ClientFactory):
    """
    Класс фабрики для создания подключения
    """
    window: 'ExampleApp'

    def __init__(self, window):
        """
        Запомить окно приложения в конструкторе для обращения
        """
        self.window = window

    def buildProtocol(self, addr):
        """
        Обработчик создания подключения
        """
        return ChatClient(self)


class ExampleApp(QtWidgets.QMainWindow, design.Ui_MainWindow):
    """
    Класс для запуска графического приложения
    """
    protocol: ChatClient
    reactor = None  # ссылка на рекатор для обращения

    def __init__(self):
        """
        Запуск приложения и обработчиков
        """
        super().__init__()
        self.setupUi(self)
        self.init_handlers()

    def init_handlers(self):
        """
        Создание обработчиков действий (кнопки, поля и тд)
        """
        self.pushButton.clicked.connect(self.send_message)  # событие нажатия на кнопку

    def closeEvent(self, event):
        """
        Обработчик закрытия окна
        """
        self.reactor.callFromThread(self.reactor.stop)  # остановка реактора

    def send_message(self):
        """
        Обработчик для отправки сообщения на сервер
        """
        self.protocol.sendLine(self.lineEdit.text().encode())  # отправить на сервер
        self.lineEdit.setText('')  # сброс текста


def main():
    # создать приложение
    app = QtWidgets.QApplication(sys.argv)

    import qt5reactor

    # создать графическое окно
    window = ExampleApp()
    window.show()


    qt5reactor.install()

    from twisted.internet import reactor


    reactor.connectTCP("localhost", 7410, ChatFactory(window))

    window.reactor = reactor
    reactor.run()


if __name__ == '__main__':
    main()
