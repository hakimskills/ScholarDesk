from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QHBoxLayout,
    QFrame
)
from PySide6.QtCore import Qt


class Dashboard(QWidget):

    def __init__(self):
        super().__init__()

        self.setup_ui()


    def setup_ui(self):

        layout = QVBoxLayout()

        title = QLabel("لوحة التحكم")
        title.setAlignment(Qt.AlignRight)

        title.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
        """)


        cards_layout = QHBoxLayout()


        students = self.create_card(
            "عدد الطلاب",
            "250"
        )

        classes = self.create_card(
            "عدد الأقسام",
            "12"
        )

        payments = self.create_card(
            "مداخيل هذا الشهر",
            "150000 دج"
        )

        unpaid = self.create_card(
            "الطلاب غير المسددين",
            "25"
        )


        cards_layout.addWidget(students)
        cards_layout.addWidget(classes)
        cards_layout.addWidget(payments)
        cards_layout.addWidget(unpaid)


        layout.addWidget(title)
        layout.addLayout(cards_layout)

        self.setLayout(layout)



    def create_card(self, title, value):

        card = QFrame()

        card.setFixedHeight(150)

        card.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 15px;
                padding: 20px;
            }
        """)


        layout = QVBoxLayout()


        label_title = QLabel(title)
        label_title.setAlignment(Qt.AlignRight)


        label_value = QLabel(value)
        label_value.setAlignment(Qt.AlignRight)

        label_value.setStyleSheet("""
            font-size: 30px;
            font-weight: bold;
        """)


        layout.addWidget(label_title)
        layout.addWidget(label_value)


        card.setLayout(layout)

        return card