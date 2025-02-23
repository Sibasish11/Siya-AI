from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QStackedWidget, QWidget, QLineEdit, QGridLayout, QVBoxLayout, QHBoxLayout, QPushButton, QFrame, QLabel, QSizePolicy, QCheckBox, QInputDialog
from PyQt5.QtGui import QIcon, QPainter, QMovie, QPixmap, QColor, QTextCharFormat, QFont, QTextBlockFormat
from PyQt5.QtCore import Qt, QSize, QTimer
from dotenv import dotenv_values
import sys
import os

# Load environment variables
env_vars = dotenv_values(".env")
Assistantname = env_vars.get("Assistantname")
current_dir = os.getcwd()
old_chat_messages = ""
TempDirPath = os.path.join(current_dir, "Frontend", "Files")
GraphicsDirPath = os.path.join(current_dir, "Frontend", "Graphics")

# Ensure necessary directories exist
os.makedirs(TempDirPath, exist_ok=True)
os.makedirs(GraphicsDirPath, exist_ok=True)

# Utility functions (unchanged)
def AnswerModifier(Answer):
    lines = Answer.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]
    modified_answer = '\n'.join(non_empty_lines)
    return modified_answer

def QueryModifier(Query):
    new_query = Query.lower().strip()
    query_words = new_query.split()
    question_words = ["how", "what", "when", "where", "why", "who", "which", "whose", "whom", "can you", "what's", "where's", "how's"]

    if any(word + " " in new_query for word in question_words):
        if query_words[-1][-1] in ['.', '?', '!']:
            new_query = new_query[:-1] + "?"
        else:
            new_query += "?"
    else:
        if query_words[-1][-1] in ['.', '?', '!']:
            new_query = new_query[:-1] + "."
        else:
            new_query += "."

    return new_query.capitalize()

def SetMicrophoneStatus(Command):
    mic_file = os.path.join(TempDirPath, "Mic.data")
    with open(mic_file, "w", encoding="utf-8") as file:
        file.write(Command)

def GetMicrophoneStatus():
    mic_file = os.path.join(TempDirPath, "Mic.data")
    with open(mic_file, "r", encoding="utf-8") as file:
        Status = file.read().strip()
    return Status

def SetAssistantStatus(Status):
    status_file = os.path.join(TempDirPath, "Status.data")
    with open(status_file, "w", encoding="utf-8") as file:
        file.write(Status)

def GetAssistantStatus():
    status_file = os.path.join(TempDirPath, "Status.data")
    with open(status_file, "r", encoding="utf-8") as file:
        Status = file.read().strip()
        return Status
        
def MicButtonInitialed():
    SetMicrophoneStatus("False")

def MicButtonClosed():
    SetMicrophoneStatus("True")

def GraphicsDirectoryPath(Filename):
    return os.path.join(GraphicsDirPath, Filename)

def TempDirectoryPath(Filename):
    return os.path.join(TempDirPath, Filename)

def ShowTextToScreen(Text):
    responses_file = os.path.join(TempDirPath, "responses.data")
    with open(responses_file, "w", encoding="utf-8") as file:
        file.write(Text)

# Add this method to handle focus mode input
def get_focus_mode_stop_time():
    stop_time, ok = QInputDialog.getText(None, "Focus Mode", "Enter stop time (example: 10:10):")
    if ok and stop_time:
        return stop_time
    return None

# Chat Section
class ChatSection(QWidget):
    def __init__(self):
        super(ChatSection, self).__init__()
        self.dyslexic_font = QFont("OpenDyslexic", 19)
        if not self.dyslexic_font.exactMatch():
            print("OpenDyslexic font not found, using Comic Sans MS as fallback")
            self.dyslexic_font = QFont("Comic Sans MS", 19)  # Fallback font
        self.default_font = QFont("Arial", 19)  # Specify a default font
        self.current_font = self.default_font

        layout = QVBoxLayout(self)
        layout.setContentsMargins(-10, 40, 40, 100)
        layout.setSpacing(-100)
        self.chat_text_edit = QTextEdit()
        self.chat_text_edit.setReadOnly(True)
        self.chat_text_edit.setTextInteractionFlags(Qt.NoTextInteraction)
        self.chat_text_edit.setFrameStyle(QFrame.NoFrame)
        layout.addWidget(self.chat_text_edit)
        self.setStyleSheet("background-color: black;")
        layout.setSizeConstraint(QVBoxLayout.SetDefaultConstraint)
        layout.setStretch(1, 1)
        self.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))
        text_color = QColor(Qt.blue)
        text_color_text = QTextCharFormat()
        text_color_text.setForeground(text_color)
        self.chat_text_edit.setCurrentCharFormat(text_color_text)
        self.gif_label = QLabel()
        self.gif_label.setStyleSheet("border: none;")
        movie = QMovie(GraphicsDirectoryPath("Jarvis.gif"))
        max_gif_size_W = 480
        max_gif_size_H = 270
        movie.setScaledSize(QSize(max_gif_size_W, max_gif_size_H))
        self.gif_label.setAlignment(Qt.AlignRight | Qt.AlignBottom)
        self.gif_label.setMovie(movie)
        movie.start()
        layout.addWidget(self.gif_label)
        self.label = QLabel("")
        self.label.setStyleSheet("color: white; font-size:16px; margin-right: 195px; border: none; margin-top: -30px;")
        self.label.setAlignment(Qt.AlignRight)
        layout.addWidget(self.label)
        layout.setSpacing(-10)
        layout.addWidget(self.gif_label)
        self.chat_text_edit.setFont(self.current_font)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.loadMessages)
        self.timer.timeout.connect(self.SpeechRecogText)
        self.timer.start(5)
        self.chat_text_edit.viewport().installEventFilter(self)
        self.setStyleSheet("""
              QScrollBar:vertical {
              border: none;
              width: 10px;
              margin: 0px 0px 0px 0px;
              }
              
              QScrollBar::handle:vertical {
              background: white;
              min-height: 20px;
              }

              QScrollBar::add-line:vertical {
              background: black;
              subcontrol-position: bottom;
              subcontrol-origin: margin;
              height: 10px;
              }
                           
              QScrollBar::sub-line:vertical {
              background: black;
              subcontrol-position: top;
              subcontrol-origin: margin;
              height: 10px;
              }
                           
              QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {
              border: none;
              background: none;
              color: none;
              }
                           
              QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical{
              background: none;
              }
        """)

    def loadMessages(self):
        global old_chat_messages
        with open(TempDirectoryPath("responses.data"), "r", encoding="utf-8") as file:
            messages = file.read()
            if not messages or len(messages) <= 1 or str(old_chat_messages) == str(messages):
                return
            print(f"Adding message with font: {self.current_font.family()}")  # Debug print
            self.addMessage(message=messages, color="White")
            old_chat_messages = messages

    def SpeechRecogText(self):
        with open(TempDirectoryPath("Status.data"), "r", encoding="utf-8") as file:
            messages = file.read()
            self.label.setText(messages)

    def load_icon(self, path, width=60, height=60):
        pixmap = QPixmap(path)
        new_pixmap = pixmap.scaled(width, height)
        self.icon_label.setPixmap(new_pixmap)

    def toggle_icon(self, event=None):
        if self.toggled:
            self.load_icon(GraphicsDirectoryPath('voice.png'), 60, 60)
            MicButtonInitialed()
        else:
            self.load_icon(GraphicsDirectoryPath('mic.png'), 60, 60)
            MicButtonClosed()
        self.toggled = not self.toggled

    def toggle_font(self, use_dyslexic_font):
        """Toggle between dyslexic and default font"""
        print(f"Toggling font to {'Dyslexic' if use_dyslexic_font else 'Default'}")
        self.current_font = self.dyslexic_font if use_dyslexic_font else self.default_font
        
        # Store current cursor position and content
        cursor = self.chat_text_edit.textCursor()
        current_position = cursor.position()
        current_text = self.chat_text_edit.toPlainText()
        
        # Update font for entire text
        self.chat_text_edit.setFont(self.current_font)
        
        # Preserve formatting and reapply content
        self.chat_text_edit.clear()
        self.addMessage(current_text, "White")
        
        # Restore cursor position
        cursor.setPosition(current_position)
        self.chat_text_edit.setTextCursor(cursor)

    def addMessage(self, message, color):
        """Add message with current font settings"""
        cursor = self.chat_text_edit.textCursor()
        format = QTextCharFormat()
        formatm = QTextBlockFormat()
        formatm.setTopMargin(10)
        formatm.setLeftMargin(10)
        format.setForeground(QColor(color))
        format.setFont(self.current_font)  # Ensure new messages use current font
        cursor.setCharFormat(format)
        cursor.setBlockFormat(formatm)
        cursor.insertText(message + "\n")
        self.chat_text_edit.setTextCursor(cursor)

# Initial Screen
class InitialScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        desktop = QApplication.desktop()
        screen_width = desktop.screenGeometry().width()
        screen_height = desktop.screenGeometry().height()
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        gif_label = QLabel()
        movie = QMovie(GraphicsDirectoryPath('Jarvis.gif'))
        gif_label.setMovie(movie)
        max_gif_size_H = int(screen_width / 16 * 9)
        movie.setScaledSize(QSize(screen_width, max_gif_size_H))
        gif_label.setAlignment(Qt.AlignCenter)
        movie.start()
        gif_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.icon_label = QLabel()
        pixmap = QPixmap(GraphicsDirectoryPath('Mic_on.png'))
        new_pixmap = pixmap.scaled(60, 60)
        self.icon_label.setPixmap(new_pixmap)
        self.icon_label.setFixedSize(150,150)
        self.icon_label.setAlignment(Qt.AlignCenter)
        self.toggle = True
        self.toggle_icon()
        self.icon_label.mousePressEvent = self.toggle_icon
        self.label = QLabel("")
        self.label.setStyleSheet("color: white; font-size:16px; margin-bottom:0;")
        self.dyslexic_font_checkbox = QCheckBox("Use Dyslexic Font")
        self.dyslexic_font_checkbox.setStyleSheet("color: white;")
        self.dyslexic_font_checkbox.stateChanged.connect(self.toggle_font)
        content_layout.addWidget(gif_label, alignment=Qt.AlignCenter)
        content_layout.addWidget(self.label, alignment=Qt.AlignCenter)
        content_layout.addWidget(self.icon_label, alignment=Qt.AlignCenter)
        content_layout.addWidget(self.dyslexic_font_checkbox, alignment=Qt.AlignCenter)
        content_layout.setContentsMargins(0, 0, 0, 150)
        self.setLayout(content_layout)
        self.setFixedHeight(screen_height)
        self.setFixedWidth(screen_width)
        self.setStyleSheet("background-color: black;")
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.SpeechRecogText)
        self.timer.start(5)

    def SpeechRecogText(self):
        with open(TempDirectoryPath("Status.data"), "r", encoding="utf-8") as file:
            messages = file.read()
            self.label.setText(messages)

    def load_icon(self, path, width=60, height=60):
        pixmap = QPixmap(path)
        new_pixmap = pixmap.scaled(width, height)
        self.icon_label.setPixmap(new_pixmap)

    def toggle_icon(self, event=None):
        if self.toggle:
            self.load_icon(GraphicsDirectoryPath('Mic_on.png'), 60, 60)
            MicButtonInitialed()
        else:
            self.load_icon(GraphicsDirectoryPath('Mic_off.png'), 60, 60)
            MicButtonClosed()
        self.toggle = not self.toggle

    def toggle_font(self, state):
        """Handle checkbox state change"""
        use_dyslexic_font = state == Qt.Checked
        # Access the stacked widget from the main window
        main_window = self.window()
        stacked_widget = main_window.centralWidget()
        # Get the MessageScreen (index 1) and find ChatSection within it
        message_screen = stacked_widget.widget(1)
        if message_screen:
            chat_section = message_screen.findChild(ChatSection)
            if chat_section:
                chat_section.toggle_font(use_dyslexic_font)
                status = "Dyslexic mode enabled" if use_dyslexic_font else "Dyslexic mode disabled"
                SetAssistantStatus(status)
            else:
                print("ChatSection not found in MessageScreen")
        else:
            print("MessageScreen not found in stacked widget")

class MessageScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        desktop = QApplication.desktop()
        screen_width = desktop.screenGeometry().width()
        screen_height = desktop.screenGeometry().height()
        layout = QVBoxLayout()
        label = QLabel("")
        layout.addWidget(label)
        self.chat_section = ChatSection()
        layout.addWidget(self.chat_section)
        self.setLayout(layout)
        self.setStyleSheet("background-color: black;")
        self.setFixedHeight(screen_height)
        self.setFixedWidth(screen_width)

class CustomTopBar(QWidget):
    def __init__(self, parent, stacked_widget):
        super().__init__(parent)
        self.initUI()
        self.current_screen = None
        self.stacked_widget = stacked_widget

    def initUI(self):
        self.setFixedHeight(50)
        layout = QHBoxLayout(self)
        layout.setAlignment(Qt.AlignRight)
        home_button = QPushButton()
        home_icon = QIcon(GraphicsDirectoryPath("Home.png"))
        home_button.setIcon(home_icon)
        home_button.setText(" Home")
        home_button.setStyleSheet("height:50px; line-height:50px ; background-color:black ; color: white")
        message_button = QPushButton()
        message_icon = QIcon(GraphicsDirectoryPath("Chats.png"))
        message_button.setIcon(message_icon)
        message_button.setText(" Chat")
        message_button.setStyleSheet("height:50px; line-height:50px; background-color:black ; color: white")
        minimize_button = QPushButton()
        minimize_icon = QIcon(GraphicsDirectoryPath("Minimize2.png"))
        minimize_button.setIcon(minimize_icon)
        minimize_button.setStyleSheet("background-color:black")
        minimize_button.clicked.connect(self.minimizeWindow)
        self.maximize_button = QPushButton()
        self.maximize_icon = QIcon(GraphicsDirectoryPath('Maximize.png'))
        self.restore_icon = QIcon(GraphicsDirectoryPath('Minimize.png'))
        self.maximize_button.setIcon(self.maximize_icon)
        self.maximize_button.setFlat(True)
        self.maximize_button.setStyleSheet("background-color:black")
        self.maximize_button.clicked.connect(self.maximizeWindow)
        close_button = QPushButton()
        close_icon = QIcon(GraphicsDirectoryPath('Close.png'))
        close_button.setIcon(close_icon)
        close_button.setStyleSheet("background-color:black")
        close_button.clicked.connect(self.closeWindow)
        line_frame = QFrame()
        line_frame.setFixedHeight(1)
        line_frame.setFrameShape(QFrame.HLine)
        line_frame.setFrameShadow(QFrame.Sunken)
        line_frame.setStyleSheet("border-color: black;")
        title_label = QLabel(f" {str(Assistantname).capitalize()} AI  ")
        title_label.setStyleSheet("color: white; font-size: 20px;; background-color:black;")
        home_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        message_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))
        layout.addWidget(title_label)
        layout.addStretch(1)
        layout.addWidget(home_button)
        layout.addWidget(message_button)
        layout.addStretch(1)
        layout.addWidget(minimize_button)
        layout.addWidget(self.maximize_button)
        layout.addWidget(close_button)
        layout.addWidget(line_frame)
        self.draggable = True
        self.offset = None

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), Qt.black)
        super().paintEvent(event)

    def minimizeWindow(self):
        self.parent().showMinimized()

    def maximizeWindow(self):
        if self.parent().isMaximized():
            self.parent().showNormal()
            self.maximize_button.setIcon(self.maximize_icon)
        else:
            self.parent().showMaximized()
            self.maximize_button.setIcon(self.restore_icon)

    def closeWindow(self):
        self.parent().close()

    def mousePressEvent(self, event):
        if self.draggable:
            self.offset = event.pos()

    def mouseMoveEvent(self, event):
        if self.draggable and self.offset:
            new_pos = event.globalPos() - self.offset
            self.parent().move(new_pos)

    def showMessage(self):
        if self.current_screen is not None:
            self.current_screen.hide()

        message_screen = MessageScreen(self)
        layout = self.parent().layout()
        if layout is not None:
            layout.addWidget(message_screen)
        self.current_screen = message_screen

    def showInitialScreen(self):
        if self.current_screen is not None:
            self.current_screen.hide()

        initial_screen = InitialScreen(self)
        layout = self.parent().layout()
        if layout is not None:
            layout.addWidget(initial_screen)
        self.current_screen = initial_screen

# Main Window
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.initUI()

    def initUI(self):
        desktop = QApplication.desktop()
        screen_width = desktop.screenGeometry().width()
        screen_height = desktop.screenGeometry().height()
        stacked_widget = QStackedWidget(self)
        initial_screen = InitialScreen()
        message_screen = MessageScreen()
        stacked_widget.addWidget(initial_screen)
        stacked_widget.addWidget(message_screen)
        self.setGeometry(0, 0, screen_width, screen_height)
        self.setStyleSheet("background-color: black;")
        top_bar = CustomTopBar(self, stacked_widget)
        self.setMenuWidget(top_bar)
        self.setCentralWidget(stacked_widget)

def GraphicalUserInterface():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    GraphicalUserInterface()