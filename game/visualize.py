import sys
import threading

from .models import Field, Direction

from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtGui import QPainter, QColor, QFont
from PyQt5.QtCore import Qt
from PyQt5 import QtCore


class Communicate(QtCore.QObject):
    signal = QtCore.pyqtSignal(str)


class Visualizer(QWidget):
    BACKGROUND_COLOR = '#bbada0'
    BORDER_WIDTH = 12
    CELL_WIDTH = 98

    CELL_COLORS = {
        0: (QColor(205, 193, 180), None),
        2: (QColor(238, 228, 219), QColor(119, 110, 101)),
        4: (QColor(237, 224, 200), QColor(119, 110, 101)),
        8: (QColor(242, 177, 121), QColor(249, 246, 242)),
        16: (QColor(245, 149, 99), QColor(249, 246, 242)),
        32: (QColor(246, 124, 95), QColor(249, 246, 242)),
        64: (QColor(246, 94, 59), QColor(249, 246, 242)),
        128: (QColor(237, 207, 114), QColor(249, 246, 242)),
        256: (QColor(237, 204, 97), QColor(249, 246, 242)),
        'other': (QColor(237, 204, 97), QColor(249, 246, 242)),
    }
    DIRECTIONS = {
        Qt.Key_Right: Direction.RIGHT,
        Qt.Key_Up: Direction.UP,
        Qt.Key_Left: Direction.LEFT,
        Qt.Key_Down: Direction.DOWN,
    }

    def __init__(self, field, caption=''):
        super().__init__()
        self._field = field
        self._width = 0
        self._caption = caption

        self.comm = Communicate()
        self.comm.signal.connect(self._handle_data)

        self.initUI()

    def _get_real_coordinate(self, x):
        return x * (self.BORDER_WIDTH + self.CELL_WIDTH) + self.BORDER_WIDTH

    def _draw_cell(self, qp, x, y, value=0):
        cell_color, font_color = self.CELL_COLORS.get(value,
            (self.CELL_COLORS['other']))

        real_x = self._get_real_coordinate(x)
        real_y = self._get_real_coordinate(y)

        qp.setPen(cell_color)
        qp.setBrush(cell_color)
        rect = (real_x, real_y, self.CELL_WIDTH, self.CELL_WIDTH)
        qp.drawRect(*rect)
        if value > 0:
            self.drawText(qp, rect, str(value), font_color)


    def initUI(self):
        size = self._field.size * (self.BORDER_WIDTH + self.CELL_WIDTH) + \
            self.BORDER_WIDTH
        self._width = size

        self.setGeometry(0, 0, size, size)
        self.setStyleSheet("background-color: {};".format(
            self.BACKGROUND_COLOR))
        self.setWindowTitle('2048')
        self.show()

    def paintEvent(self, event):
        qp = QPainter()
        qp.begin(self)
        for i in range(self._field.size):
            for j in range(self._field.size):
                self._draw_cell(qp, j, i, value=self._field.values[i][j].value)
        self.drawText(qp, (20, 20, self._width - 40, 50), self._caption,
                      QColor(115, 255, 115), align=Qt.AlignLeft)
        self.drawText(qp, (20, 20, self._width - 40, 50), self._field.score,
                      QColor(115, 255, 115), align=Qt.AlignRight)
        qp.end()

    def drawText(self, qp, rect, text, color, *, align=Qt.AlignCenter):
        qp.setPen(color)
        font = QFont('Decorative', 32)
        font.setBold(True)
        qp.setFont(font)
        qp.drawText(*rect, align, str(text))

    def move(self, direction):
        field, _ = self._field.get_moved(direction)
        self._field = field
        self.update()

    def keyPressEvent(self, event):
        if event.key() in self.DIRECTIONS:
            self.move(self.DIRECTIONS[event.key()])
        elif event.key() == Qt.Key_Escape:
            self.close()

    def _run_bot_thread(self, comm, bot):
        import time
        def _callback(field):
            self._field = field
            comm.signal.emit('update')
            time.sleep(0.1)
        bot(self._field, callback=_callback)
        time.sleep(2)
        comm.signal.emit('quit')


    def run_bot(self, bot):
        my_thread = threading.Thread(target=self._run_bot_thread,
                                     args=(self.comm, bot))
        my_thread.daemon = True
        my_thread.start()

    def _handle_data(self, data):
        if data == 'update':
            self.update()
        elif data == 'quit':
            print(self.score)
            self.close()

    @property
    def score(self):
        return self._field.score

    @property
    def is_over(self):
        return self._field.is_over

    @property
    def field(self):
        return self._field


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Visualizer(Field(), 'Gen. 1')
    sys.exit(app.exec_())
