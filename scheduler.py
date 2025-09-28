from PySide6.QtWidgets import (
    QApplication, QMainWindow, QPushButton,
    QVBoxLayout, QHBoxLayout, QWidget, QScrollArea,
    QDialog, QLabel, QLineEdit, QDialogButtonBox
)
from PySide6.QtCore import Qt, QSize
from functools import partial
import json
import sys


week = ["월", "화", "수", "목", "금", "토", "일"]

class MainWindow(QMainWindow):
    def __init__(self, schedules):
        super().__init__()

        self.setWindowTitle("My Scheduler")
        self.setFixedSize(QSize(700, 600))
        self.defaultStyle = "font-size: 16px; text-align: center; padding: 0px; margin: 0px;"
        self.schedule_json = schedules
        # 메인 위젯 설정
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 전체 레이아웃
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 고정: 상단 Add Schedule 버튼
        add_schedule_button = QPushButton("Add Schedule")
        add_schedule_button.setFixedSize(700, 40)
        add_schedule_button.setStyleSheet(self.defaultStyle)
        add_schedule_button.clicked.connect(self.add_schedule)
        main_layout.addWidget(add_schedule_button, alignment=Qt.AlignTop)

        # 고정: 요일 레이블
        labels = []
        week_layout = QHBoxLayout()
        labels.append(QLabel("요일"))
        labels[0].setStyleSheet(self.defaultStyle + "background-color: lightgray;")
        week_layout.addWidget(labels[0])
        for i in range(7):
            labels.append(QLabel(week[i]))
            labels[i+1].setStyleSheet(self.defaultStyle + "background-color: lightgray;")
            week_layout.addWidget(labels[i+1])

        for j in range(8):
            labels[j].setAlignment(Qt.AlignCenter)

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
        if schedules is not None:
            for schedule in schedules:
                schedule_name = schedule["name"].replace(" ", "\n")
                row_layout = QHBoxLayout()
                label = QLabel(schedule_name)
                label.setStyleSheet(self.defaultStyle)
                label.setAlignment(Qt.AlignCenter)
                row_layout.addWidget(label)

                for i in range(7):
                    button = QPushButton()
                    button.setMinimumHeight(50)
                    button.setMinimumWidth(80)
                    button.setSizePolicy(
                        QPushButton().sizePolicy().horizontalPolicy(),
                        QPushButton().sizePolicy().verticalPolicy()
                    )
                    if schedule["days"][i] == 1:
                        button.setStyleSheet("background-color: lightblue;")
                    else:
                        button.setStyleSheet("background-color: white;")
                    row_layout.addWidget(button)

                    # ✅ 버튼에 스케줄 인덱스와 요일 인덱스 저장
                    button.setProperty("row_index", self.schedule_json.index(schedule))
                    button.setProperty("day_index", i)
                    # ✅ 클릭 연결
                    button.clicked.connect(partial(self.is_checked, button))

                self.scroll_layout.addLayout(row_layout)

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

            self.schedule_json.append({"name": schedule_name, "days": [0, 0, 0, 0, 0, 0, 0]})
            self.make_schedule_button(schedule_name)

            save_schedules("./schedules.json", self.schedule_json)

    def make_schedule_button(self, schedule_name: str):
        print(f"Schedule added: {schedule_name}")

        row_index = len(self.schedule_json) - 1
        schedule_name = schedule_name.replace(" ", "\n")
        row_layout = QHBoxLayout()
        label = QLabel(schedule_name)
        label.setStyleSheet(self.defaultStyle)
        label.setAlignment(Qt.AlignCenter)
        row_layout.addWidget(label)

        for day_index in range(7):
            button = QPushButton('')
            button.setMinimumHeight(50)
            button.setMinimumWidth(80)

            button.setProperty("row_index", row_index)
            button.setProperty("day_index", day_index)

            button.setStyleSheet("background-color: white;")

            button.clicked.connect(partial(self.is_checked, button))

            row_layout.addWidget(button)

        self.scroll_layout.addLayout(row_layout)


    def is_checked(self, button):
        row_index = button.property("row_index")
        day_index = button.property("day_index")

        if row_index is None or day_index is None:
            print("속성 정보 없음!")
            return

        current = self.schedule_json[row_index]["days"][day_index]
        new_value = 0 if current == 1 else 1
        self.schedule_json[row_index]["days"][day_index] = new_value

        # 색상 업데이트
        if new_value == 1:
            button.setStyleSheet("background-color: lightblue;")
        else:
            button.setStyleSheet("background-color: white;")

        # 저장
        save_schedules("./schedules.json", self.schedule_json)

        print(f"Updated: row {row_index}, day {day_index} → {new_value}")


def load_schedules(filename):
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


def save_schedules(filename, schedules):
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(schedules, file, ensure_ascii=False, indent=4)

def main():
    schedules = load_schedules("./schedules.json")
    print(schedules)
    app = QApplication(sys.argv)
    window = MainWindow(schedules)
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
