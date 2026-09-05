#!/usr/bin/env python3
import sys
import traceback
from pathlib import Path

from PySide6.QtCore import QObject, QThread, Signal, Slot, Qt
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QComboBox, QPlainTextEdit,
    QFileDialog, QProgressBar, QMessageBox, QGroupBox
)

import whisper


FORMATS = {
    "TXT — обычный текст": "txt",
    "SRT — субтитры": "srt",
    "VTT — WebVTT": "vtt",
    "TSV — таблица": "tsv",
    "JSON — полный результат": "json",
}

LANGUAGES = {
    "Авто": None,
    "Русский": "ru",
    "English": "en",
    "Deutsch": "de",
    "Français": "fr",
    "Español": "es",
    "Беларуская": "be",
    "Українська": "uk",
    "Polski": "pl",
}


class Worker(QObject):
    log = Signal(str)
    finished = Signal(str)
    error = Signal(str)

    def __init__(self, input_file, output_file, model_name, language):
        super().__init__()
        self.input_file = input_file
        self.output_file = output_file
        self.model_name = model_name
        self.language = language

    @Slot()
    def run(self):
        try:
            self.log.emit(f"Файл: {self.input_file}")
            self.log.emit(f"Модель: {self.model_name}")
            self.log.emit("Загрузка локальной модели...")

            model = whisper.load_model(self.model_name)
            self.log.emit(f"Модель загружена. Устройство: {model.device}")
            self.log.emit("Начинаю распознавание...")

            options = {}
            if self.language:
                options["language"] = self.language

            # verbose=True makes Whisper print segment progress to stdout,
            # but the GUI deliberately uses an indeterminate progress bar
            # because the Whisper Python API does not expose a simple total
            # progress callback.
            result = model.transcribe(
                self.input_file,
                verbose=True,
                **options,
            )

            out = Path(self.output_file)
            fmt = out.suffix.lower().lstrip(".")
            self.log.emit(f"Сохраняю результат: {out}")

            if fmt == "txt":
                text = result["text"].strip()
                out.write_text(text + "\n", encoding="utf-8")

            elif fmt in ("srt", "vtt", "tsv", "json"):
                from whisper.utils import get_writer
                writer = get_writer(fmt, str(out.parent))
                writer(result, str(Path(self.input_file).stem), options={})

                generated = out.parent / f"{Path(self.input_file).stem}.{fmt}"
                if generated != out:
                    if generated.exists():
                        generated.replace(out)
                    else:
                        raise RuntimeError(
                            f"Whisper создал неожиданный файл: {generated}"
                        )
            else:
                raise RuntimeError(f"Неподдерживаемый формат: {fmt}")

            self.log.emit("Готово.")
            self.finished.emit(str(out))

        except Exception:
            self.error.emit(traceback.format_exc())


class WhisperWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Whisper Local")
        self.resize(720, 520)

        self.thread = None
        self.worker = None

        root = QWidget()
        self.setCentralWidget(root)
        layout = QVBoxLayout(root)

        file_box = QGroupBox("Исходный файл")
        file_layout = QHBoxLayout(file_box)
        self.file_edit = QLineEdit()
        self.file_edit.setPlaceholderText("Выберите аудио или видеофайл...")
        browse = QPushButton("Выбрать…")
        browse.clicked.connect(self.choose_file)
        file_layout.addWidget(self.file_edit)
        file_layout.addWidget(browse)
        layout.addWidget(file_box)

        options_box = QGroupBox("Параметры")
        options = QHBoxLayout(options_box)

        options.addWidget(QLabel("Модель:"))
        self.model_combo = QComboBox()
        self.model_combo.addItems(["small","base", "tiny"])
        self.model_combo.setCurrentText("small")
        options.addWidget(self.model_combo)

        options.addWidget(QLabel("Язык:"))
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(LANGUAGES.keys())
        self.lang_combo.setCurrentText("Русский")
        options.addWidget(self.lang_combo)

        options.addWidget(QLabel("Формат:"))
        self.format_combo = QComboBox()
        self.format_combo.addItems(FORMATS.keys())
        options.addWidget(self.format_combo)

        layout.addWidget(options_box)

        output_box = QGroupBox("Выходной файл")
        output_layout = QHBoxLayout(output_box)
        self.output_edit = QLineEdit()
        self.output_edit.setPlaceholderText("Будет создан рядом с исходным файлом")
        output_browse = QPushButton("Сохранить как…")
        output_browse.clicked.connect(self.choose_output)
        output_layout.addWidget(self.output_edit)
        output_layout.addWidget(output_browse)
        layout.addWidget(output_box)

        self.start_button = QPushButton("РАСПОЗНАТЬ")
        self.start_button.setMinimumHeight(42)
        self.start_button.clicked.connect(self.start_transcription)
        layout.addWidget(self.start_button)

        self.progress = QProgressBar()
        self.progress.setRange(0, 0)  # indeterminate
        self.progress.hide()
        layout.addWidget(self.progress)

        layout.addWidget(QLabel("Лог"))
        self.log_view = QPlainTextEdit()
        self.log_view.setReadOnly(True)
        layout.addWidget(self.log_view)

        self.status = QLabel("Готово к работе.")
        layout.addWidget(self.status)

    def choose_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите аудио или видео",
            str(Path.home()),
            "Медиа (*.mp3 *.wav *.m4a *.flac *.ogg *.opus *.aac *.mp4 *.mkv *.webm *.avi *.mov);;Все файлы (*)",
        )
        if path:
            self.file_edit.setText(path)
            if not self.output_edit.text():
                self.output_edit.setText(self.default_output(path))

    def default_output(self, input_path):
        suffix = FORMATS[self.format_combo.currentText()]
        return str(Path(input_path).with_suffix("." + suffix))

    def choose_output(self):
        input_path = self.file_edit.text().strip()
        default = self.default_output(input_path) if input_path else str(Path.home() / "transcription.txt")
        fmt = FORMATS[self.format_combo.currentText()]
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Куда сохранить результат",
            default,
            f"{fmt.upper()} (*.{fmt})",
        )
        if path:
            p = Path(path)
            if p.suffix.lower() != "." + fmt:
                p = p.with_suffix("." + fmt)
            self.output_edit.setText(str(p))

    def start_transcription(self):
        input_path = Path(self.file_edit.text().strip()).expanduser()
        if not input_path.is_file():
            QMessageBox.warning(self, "Ошибка", "Выбери существующий аудио- или видеофайл.")
            return

        fmt = FORMATS[self.format_combo.currentText()]
        output_text = self.output_edit.text().strip()
        output_path = Path(output_text).expanduser() if output_text else input_path.with_suffix("." + fmt)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        if output_path.resolve() == input_path.resolve():
            QMessageBox.warning(self, "Ошибка", "Выходной файл не может совпадать с исходным.")
            return

        self.start_button.setEnabled(False)
        self.progress.show()
        self.log_view.clear()
        self.status.setText("Распознавание...")
        self.log_view.appendPlainText("=== Whisper Local ===")
        self.log_view.appendPlainText("Аудио обрабатывается локально на этом ПК.")

        language = LANGUAGES[self.lang_combo.currentText()]
        model_name = self.model_combo.currentText()

        self.thread = QThread()
        self.worker = Worker(str(input_path), str(output_path), model_name, language)
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.log.connect(self.append_log)
        self.worker.finished.connect(self.done)
        self.worker.error.connect(self.failed)
        self.worker.finished.connect(self.thread.quit)
        self.worker.error.connect(self.thread.quit)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.finished.connect(self.cleanup_thread)

        self.thread.start()

    @Slot(str)
    def append_log(self, text):
        self.log_view.appendPlainText(text)
        self.log_view.verticalScrollBar().setValue(
            self.log_view.verticalScrollBar().maximum()
        )

    @Slot(str)
    def done(self, output_path):
        self.progress.hide()
        self.start_button.setEnabled(True)
        self.status.setText("Готово.")
        self.append_log(f"Результат: {output_path}")
        QMessageBox.information(self, "Готово", f"Результат сохранён:\n{output_path}")

    @Slot(str)
    def failed(self, details):
        self.progress.hide()
        self.start_button.setEnabled(True)
        self.status.setText("Ошибка.")
        self.append_log(details)
        QMessageBox.critical(self, "Ошибка Whisper", details)

    def cleanup_thread(self):
        if self.worker:
            self.worker.deleteLater()
        self.worker = None
        self.thread = None


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Whisper Local")
    window = WhisperWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
