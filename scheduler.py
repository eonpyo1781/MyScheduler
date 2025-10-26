from PySide6.QtWidgets import (
    QApplication, QMainWindow, QPushButton,
    QVBoxLayout, QHBoxLayout, QWidget, QScrollArea,
    QDialog, QLabel, QLineEdit, QDialogButtonBox
)
from PySide6.QtCore import Qt, QSize
from functools import partial
from datetime import date, timedelta
import os, json, sys

week = ["Schedule", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
today = date.today().weekday()
WINDOW_WIDTH = 700
WINDOW_HEIGHT = 600
CHECKED_COLOR = "lightblue"
UNCHECKED_COLOR = "lightgray"

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.schedule_count = 0
        self.setWindowTitle("My Scheduler")
        self.setFixedSize(QSize(WINDOW_WIDTH, WINDOW_HEIGHT))
        self.defaultStyle = "font-size: 16px; text-align: center; padding: 0px; margin: 0px;"
        self.scheModel = ScheduleModel("schedules.json")

        # 메인 위젯 설정
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 전체 레이아웃
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        top_layout = QHBoxLayout()
        # 고정: 상단 Add Schedule 버튼
        add_schedule_button = QPushButton("Add Schedule")
        add_schedule_button.setObjectName("TopScheduleButton")
        add_schedule_button.clicked.connect(self.add_schedule)

        monday = date.today() - timedelta(days=date.today().weekday())
        sunday = monday + timedelta(days=6)
        date_label = QPushButton(f"{monday} ~ {sunday}")
        date_label.setObjectName("TopScheduleButton")
        top_layout.addWidget(add_schedule_button)
        top_layout.addWidget(date_label)
        main_layout.addLayout(top_layout)

        # 고정: 요일 레이블
        labels = []
        week_layout = QHBoxLayout()

        for i in range(8):
            labels.append(QLabel(week[i]))
            labels[i].setObjectName("WeekLabel")
            labels[i].setAlignment(Qt.AlignCenter)
            week_layout.addWidget(labels[i])
        main_layout.addLayout(week_layout)

        # 스크롤 가능한 영역 만들기
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        main_layout.addWidget(self.scroll_area)

        # 스크롤 영역 안쪽에 위젯 & 레이아웃
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setAlignment(Qt.AlignTop)

        self.scroll_area.setWidget(self.scroll_content)

        # 기존 스케줄 불러오기
        if self.scheModel.schedules is not None:
            for schedule in self.scheModel.schedules:
                self.make_schedule_button(schedule["name"], schedule["days"])

    def add_schedule(self):
        dig = QDialog(self)
        dig.setWindowTitle("Schedule Name?")
        dig.setFixedSize(200, 100)
        label = QLineEdit(dig)
        label.setPlaceholderText("Enter schedule name")
        layout = QVBoxLayout(dig)
        layout.addWidget(label)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dig.accept)
        buttons.rejected.connect(dig.reject)
        layout.addWidget(buttons)

        if dig.exec() == QDialog.Accepted:
            schedule_name = label.text()

            self.scheModel.schedules.append({"name": schedule_name, "days": [0, 0, 0, 0, 0, 0, 0]})
            self.make_schedule_button(schedule_name, [0, 0, 0, 0, 0, 0, 0])

            self.scheModel.save_schedules(self.scheModel.schedules)

    def make_schedule_button(self, schedule_name: str, schedule_done):
        print(f"Schedule added: {schedule_name}")

        schedule_name = schedule_name.replace(" ", "\n")
        row_layout = QHBoxLayout()
        row_layout.setSpacing(5)  # 버튼 사이 간격
        row_layout.setContentsMargins(0, 0, 0, 0)  # 주변 여백 제거

        label = QLabel(schedule_name)
        label.setObjectName("ScheduleName")
        label.setAlignment(Qt.AlignCenter)
        row_layout.addWidget(label)

        for day_index in range(7):
            button = QPushButton('')

            if(day_index < today and schedule_done[day_index] == 0):
                button.setObjectName("PrevDayScheduleButton")
            else:
                button.setObjectName("DayScheduleButton")
            button.setCheckable(True)

            if schedule_done[day_index] == 1:
                button.setChecked(True)
            else:
                button.setChecked(False)

            button.setSizePolicy(
                QPushButton().sizePolicy().horizontalPolicy(),
                QPushButton().sizePolicy().verticalPolicy()
            )
            button.setProperty("row_index", self.schedule_count)
            button.setProperty("day_index", day_index)
            button.clicked.connect(partial(self.is_checked, button))
            
            row_layout.addWidget(button)

        self.scroll_layout.addLayout(row_layout)
        self.schedule_count += 1

    def is_checked(self, button):
        row_index = button.property("row_index")
        day_index = button.property("day_index")

        if row_index is None or day_index is None:
            print("속성 정보 없음!")
            return

        current = self.scheModel.schedules[row_index]["days"][day_index]
        new_value = 0 if current == 1 else 1
        self.scheModel.schedules[row_index]["days"][day_index] = new_value
                
        if button.isChecked(): 
            button.setChecked(True)
        else:
            button.setChecked(False)

        self.scheModel.save_schedules(self.scheModel.schedules)

        print(f"Updated: row {row_index}, day {day_index} → {new_value}")

class ScheduleModel:
    def __init__(self, filename):
        self.filename = os.path.join(os.path.dirname(__file__), filename)
        self.schedules = self.load_schedules(filename)

    def load_schedules(self, filename):
        print(filename + " being loading.")
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                schedules = json.load(file)
                return schedules
        except FileNotFoundError:
            print("파일을 찾을 수 없습니다. 빈 리스트로 시작합니다.")
            return []
        except json.JSONDecodeError as e:
            print(f"JSON 파싱 오류: {e}")
            return []

    def save_schedules(self, schedules):
        with open(self.filename, 'w', encoding='utf-8') as file:
            json.dump(schedules, file, indent=None, ensure_ascii=False)

def main():
    app = QApplication(sys.argv)

    print(today)
    try:
        with open("style.qss", "r") as f:
            style_sheet = f.read()
        print("style.qss done.")
        app.setStyleSheet(style_sheet)
    except FileNotFoundError:
        print("Warning: style.qss not found.")

    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
