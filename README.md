# OpenAI Whisper — полная установка на EndeavourOS / Arch Linux

Инструкция устанавливает:

* OpenAI Whisper из официального GitHub-репозитория;
* отдельное Python virtual environment;
* FFmpeg;
* PySide6 для графического интерфейса;
* локальное GUI-приложение Whisper;
* ярлык в меню GNOME;
* запуск без ручного `source` и без перехода в каталог Whisper;
* использование существующего локального Whisper без OpenAI API.

Все операции распознавания выполняются локально. Само GUI-приложение не содержит обращения к OpenAI API или облачному сервису.

> Важно: при первом запуске конкретной модели Whisper может скачать её веса из интернета. После загрузки модель хранится локально в кеше Whisper и используется без повторной загрузки.

---

# 1. Требования

Предполагается:

* EndeavourOS / Arch Linux;
* Python 3;
* NVIDIA GPU или CPU;
* GNOME или другое Linux desktop environment;
* доступ в интернет на этапе установки и первого скачивания моделей.

Для NVIDIA необходимо, чтобы драйвер уже был установлен и работал.

Проверить GPU:

```bash
nvidia-smi
```

Если команда показывает видеокарту и версию драйвера — NVIDIA-драйвер работает.

Проверить Python:

```bash
python --version
```

Проверить Git:

```bash
git --version
```

Если каких-либо компонентов нет, установить:

```bash
sudo pacman -S --needed git python python-pip ffmpeg
```

Whisper требует FFmpeg для обработки аудио и видео. Официальная документация Whisper отдельно указывает FFmpeg как обязательную системную зависимость.

Проверить FFmpeg:

```bash
ffmpeg -version
```

---

# 2. Создание каталога Whisper

Рекомендуемый каталог:

```text
~/Applications/whisper/
```

Создать его:

```bash
mkdir -p ~/Applications
cd ~/Applications
```

---

# 3. Скачать Whisper из официального GitHub

Клонировать официальный репозиторий:

```bash
git clone https://github.com/openai/whisper.git
```

После этого:

```bash
cd ~/Applications/whisper
```

Проверить:

```bash
ls
```

В каталоге должны находиться файлы самого Whisper, например:

```text
whisper/
README.md
setup.py
pyproject.toml
...
```

---

# 4. Создать Python virtual environment

Создать отдельное окружение:

```bash
python -m venv .venv
```

В результате появится:

```text
~/Applications/whisper/.venv/
```

Структура теперь выглядит примерно так:

```text
~/Applications/whisper/
├── .venv/
├── whisper/
├── README.md
├── setup.py
└── ...
```

Virtual environment нужен для того, чтобы зависимости Whisper не смешивались с системным Python.

---

# 5. Активировать окружение

```bash
source ~/Applications/whisper/.venv/bin/activate
```

После активации в начале строки терминала обычно появится:

```text
(.venv)
```

Проверить, какой Python используется:

```bash
which python
```

Должно быть примерно:

```text
/home/USERNAME/Applications/whisper/.venv/bin/python
```

Также:

```bash
which pip
```

Должен использоваться:

```text
/home/USERNAME/Applications/whisper/.venv/bin/pip
```

---

# 6. Обновить инструменты Python

Находясь внутри `.venv`:

```bash
python -m pip install --upgrade pip setuptools wheel
```

---

# 7. Установить Whisper из GitHub

Установка непосредственно из официального репозитория:

```bash
python -m pip install -e .
```

Опция `-e` устанавливает локальный репозиторий в editable-режиме.

Это удобно, если репозиторий Whisper находится непосредственно в:

```text
~/Applications/whisper/
```

Альтернативный способ, если не нужен editable-режим:

```bash
python -m pip install git+https://github.com/openai/whisper.git
```

Официальный репозиторий Whisper поддерживает оба варианта установки.

Для этой схемы рекомендуется:

```bash
python -m pip install -e .
```

---

# 8. Если установка Whisper требует Rust

Обычно готового Python wheel достаточно.

Если во время установки появляется ошибка вроде:

```text
No module named 'setuptools_rust'
```

установить:

```bash
python -m pip install setuptools-rust
```

После этого повторить:

```bash
python -m pip install -e .
```

Если установка требует Rust compiler:

```bash
sudo pacman -S --needed rust
```

После установки Rust повторить:

```bash
python -m pip install -e .
```

Whisper указывает Rust как возможную зависимость при отсутствии готового wheel для `tiktoken`.

---

# 9. Проверить установку Whisper

Сначала:

```bash
whisper --help
```

Если появилась справка Whisper — CLI работает.

Проверить Python API:

```bash
python -c "import whisper; print(whisper.available_models())"
```

Должен появиться список моделей, например:

```text
['tiny.en', 'tiny', 'base.en', 'base', 'small.en', 'small', 'medium.en', 'medium', 'large-v1', 'large-v2', 'large-v3', 'large', 'turbo']
```

Проверить расположение Whisper:

```bash
which whisper
```

Должно указывать на:

```text
~/Applications/whisper/.venv/bin/whisper
```

---

# 10. Проверить использование NVIDIA GPU

Проверить PyTorch:

```bash
python -c "import torch; print('CUDA:', torch.cuda.is_available()); print('GPU:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU')"
```

При рабочем CUDA должно быть примерно:

```text
CUDA: True
GPU: NVIDIA GeForce GTX ...
```

Если:

```text
CUDA: False
```

Whisper всё равно может работать, но будет использовать CPU.

Проверить более подробно:

```bash
python
```

Затем:

```python
import torch

print(torch.__version__)
print(torch.cuda.is_available())

if torch.cuda.is_available():
    print(torch.cuda.get_device_name(0))
```

Выйти:

```python
exit()
```

---

# 11. Первый запуск Whisper

Например:

```bash
whisper ~/Music/test.mp3 --model small --language Russian
```

При первом использовании модели Whisper может скачать её веса.

После этого они сохраняются локально и повторно скачиваться не должны.

Посмотреть кеш:

```bash
ls -lh ~/.cache/whisper
```

---

# 12. Выбор модели

Whisper содержит несколько моделей с разным соотношением скорости и качества.

Основные:

```text
tiny
base
small
medium
large
turbo
```

Для видеокарты с ограниченным объёмом VRAM практичным вариантом является:

```text
small
```

Для максимально качественной транскрипции можно использовать более крупные модели, но требования к памяти существенно возрастают.

Для обычной русскоязычной транскрипции:

```bash
whisper audio.mp3 --model small --language Russian
```

Если язык нужно определить автоматически:

```bash
whisper audio.mp3 --model small
```

Если требуется перевод речи на английский, нужно использовать мультиязычные модели; `turbo` не предназначен для speech-to-English translation.

---

# 13. Проверка Whisper через Python

Whisper можно использовать непосредственно из Python:

```python
import whisper

model = whisper.load_model("small")

result = model.transcribe(
    "audio.mp3",
    language="ru"
)

print(result["text"])
```

Официальный Python API Whisper предоставляет `load_model()` и `transcribe()`.

---

# 14. Установка PySide6

GUI будет использовать PySide6.

Находясь в том же `.venv`:

```bash
python -m pip install PySide6
```

Проверить:

```bash
python -c "from PySide6.QtWidgets import QApplication; print('PySide6 OK')"
```

Если появилось:

```text
PySide6 OK
```

GUI-зависимость установлена.

PySide6 официально распространяется через PyPI и устанавливается командой `pip install PySide6`.

---

# 15. Структура готовой установки

После всех действий желательно иметь:

```text
~/Applications/
└── whisper/
    ├── .venv/
    │   ├── bin/
    │   │   ├── python
    │   │   ├── pip
    │   │   └── whisper
    │   └── ...
    │
    ├── whisper/
    ├── README.md
    ├── setup.py
    └── ...
```

GUI можно хранить отдельно:

```text
~/.local/share/whisper-local/
└── app.py
```

Так Whisper и приложение остаются логически разделены.

---

# 16. Установка приложения Whisper Local

Предполагается, что приложение содержит:

```text
app.py
install.sh
README.md
```

Например:

```text
whisper-local-gui/
├── app.py
├── install.sh
└── README.md
```

Распаковать архив приложения.

Перейти в каталог:

```bash
cd ~/Downloads/whisper-local-gui
```

Сделать установщик исполняемым:

```bash
chmod +x install.sh
```

---

# 17. Установка приложения вручную

Если хочется установить приложение без автоматического установщика:

```bash
mkdir -p ~/.local/share/whisper-local
```

Скопировать GUI:

```bash
cp app.py ~/.local/share/whisper-local/app.py
```

---

# 18. Создание launcher

Создать каталог:

```bash
mkdir -p ~/.local/bin
```

Создать файл:

```bash
nano ~/.local/bin/whisper-local
```

Вставить:

```bash
#!/bin/bash

cd "$HOME/Applications/whisper"

exec "$HOME/Applications/whisper/.venv/bin/python" \
    "$HOME/.local/share/whisper-local/app.py"
```

Сохранить.

Сделать исполняемым:

```bash
chmod +x ~/.local/bin/whisper-local
```

---

# 19. Проверить запуск GUI

Запустить:

```bash
~/.local/bin/whisper-local
```

Если окно Whisper Local появилось — приложение установлено правильно.

Важно: здесь не нужно делать:

```bash
source .venv/bin/activate
```

Launcher непосредственно вызывает:

```text
~/Applications/whisper/.venv/bin/python
```

Поэтому используется именно нужное виртуальное окружение.

---

# 20. Создать ярлык в GNOME

Создать каталог приложений пользователя:

```bash
mkdir -p ~/.local/share/applications
```

Узнать имя пользователя:

```bash
whoami
```

Например:

```text
yzen
```

Создать desktop-файл:

```bash
nano ~/.local/share/applications/whisper-local.desktop
```

Вставить:

```ini
[Desktop Entry]
Type=Application
Name=Whisper Local
Comment=Локальное распознавание речи через OpenAI Whisper
Exec=/home/YOUR_USERNAME/.local/bin/whisper-local
Icon=audio-input-microphone
Terminal=false
Categories=AudioVideo;Audio;Utility;
StartupNotify=false
```

Заменить:

```text
YOUR_USERNAME
```

на имя пользователя.

Например:

```ini
Exec=/home/yzen/.local/bin/whisper-local
```

Не использовать:

```text
~/.local/bin/whisper-local
```

в `Exec`.

В desktop-файлах лучше указывать абсолютный путь.

---

# 21. Проверить desktop-файл

Установить утилиты:

```bash
sudo pacman -S --needed desktop-file-utils
```

Проверить:

```bash
desktop-file-validate ~/.local/share/applications/whisper-local.desktop
```

Если команда ничего не вывела — desktop-файл синтаксически корректен.

---

# 22. Обновить базу приложений

```bash
update-desktop-database ~/.local/share/applications
```

После этого открыть меню приложений GNOME.

Найти:

```text
Whisper Local
```

и запустить.

---

# 23. Если приложение запускается из терминала, но не из GNOME

Это обычно означает проблему именно с `.desktop` или окружением запуска.

Проверить launcher:

```bash
~/.local/bin/whisper-local
```

Если работает — сам Python/Whisper/PySide6 исправны.

Затем проверить desktop-файл:

```bash
gtk-launch whisper-local
```

Если приложение запускается — проблема была в обновлении меню GNOME.

Если не запускается, временно включить терминал:

```ini
Terminal=true
```

в:

```text
~/.local/share/applications/whisper-local.desktop
```

Затем снова:

```bash
gtk-launch whisper-local
```

Терминал покажет ошибку, из-за которой приложение закрывается.

После диагностики вернуть:

```ini
Terminal=false
```

---

# 24. Запуск без desktop-файла

Приложение всегда можно запустить напрямую:

```bash
~/.local/bin/whisper-local
```

Или непосредственно через Python:

```bash
~/Applications/whisper/.venv/bin/python \
    ~/.local/share/whisper-local/app.py
```

---

# 25. Запуск Whisper без активации venv

Активировать окружение каждый раз необязательно.

Вместо:

```bash
cd ~/Applications/whisper
source .venv/bin/activate
whisper audio.mp3
```

можно:

```bash
~/Applications/whisper/.venv/bin/whisper audio.mp3
```

Это особенно удобно для скриптов и desktop-файлов.

---

# 26. Обновление Whisper

Перейти в репозиторий:

```bash
cd ~/Applications/whisper
```

Активировать окружение:

```bash
source .venv/bin/activate
```

Получить изменения Git:

```bash
git pull
```

Затем переустановить editable-пакет:

```bash
python -m pip install -e .
```

Проверить:

```bash
whisper --help
```

---

# 27. Обновление PySide6

Активировать окружение:

```bash
source ~/Applications/whisper/.venv/bin/activate
```

Обновить:

```bash
python -m pip install --upgrade PySide6
```

---

# 28. Проверка всех компонентов одной командой

Можно выполнить:

```bash
~/Applications/whisper/.venv/bin/python -c "
import whisper
import torch
from PySide6 import QtCore

print('Whisper: OK')
print('PySide6:', QtCore.__version__)
print('PyTorch:', torch.__version__)
print('CUDA:', torch.cuda.is_available())

if torch.cuda.is_available():
    print('GPU:', torch.cuda.get_device_name(0))
else:
    print('GPU: CPU')
"
```

Ожидаемый результат:

```text
Whisper: OK
PySide6: ...
PyTorch: ...
CUDA: True
GPU: NVIDIA ...
```

---

# 29. Проверка FFmpeg

```bash
ffmpeg -version
```

Также:

```bash
which ffmpeg
```

Обычно:

```text
/usr/bin/ffmpeg
```

---

# 30. Проверка всей системы

Итоговая последовательность:

```bash
ffmpeg -version
```

```bash
~/Applications/whisper/.venv/bin/python --version
```

```bash
~/Applications/whisper/.venv/bin/whisper --help
```

```bash
~/Applications/whisper/.venv/bin/python -c "import whisper; print(whisper.available_models())"
```

```bash
~/Applications/whisper/.venv/bin/python -c "import torch; print(torch.cuda.is_available())"
```

```bash
~/Applications/whisper/.venv/bin/python -c "from PySide6.QtWidgets import QApplication; print('PySide6 OK')"
```

И затем:

```bash
~/.local/bin/whisper-local
```

---

# 31. Где находятся модели Whisper

По умолчанию модели сохраняются в:

```text
~/.cache/whisper/
```

Посмотреть:

```bash
ls -lh ~/.cache/whisper
```

Например:

```text
~/.cache/whisper/
├── tiny.pt
├── base.pt
└── small.pt
```

После первоначальной загрузки соответствующей модели Whisper использует локальный файл.

---

# 32. Полностью офлайн-режим после установки

После того как нужная модель уже скачана, можно проверить работу без сети.

Например:

```bash
ip link
```

или просто отключить интернет обычным способом.

Затем запустить:

```bash
~/.local/bin/whisper-local
```

и обработать файл.

Если модель уже находится в:

```text
~/.cache/whisper/
```

Whisper не должен скачивать её повторно.

---

# 33. Что делать, если Whisper работает только на CPU

Проверить:

```bash
~/Applications/whisper/.venv/bin/python -c "import torch; print(torch.cuda.is_available())"
```

Если:

```text
False
```

проверить NVIDIA:

```bash
nvidia-smi
```

Если `nvidia-smi` тоже не работает — проблема не в Whisper, а в драйвере NVIDIA.

Если:

```bash
nvidia-smi
```

работает, но:

```text
torch.cuda.is_available()
```

возвращает:

```text
False
```

нужно отдельно проверить установленную версию PyTorch и её CUDA-поддержку.

---

# 34. Как выбирать модель

Для обычной транскрипции:

```text
tiny
↓
base
↓
small
↓
medium
↓
large
```

Чем выше модель, тем обычно лучше распознавание, но тем больше требования к памяти и тем ниже скорость.

Практический вариант для видеокарты с небольшим объёмом VRAM:

```text
small
```

Если нужна максимальная точность и скорость не критична, можно попробовать более крупную модель на CPU или другой видеокарте.

Не стоит автоматически считать, что самая большая модель всегда будет лучшим вариантом для конкретной записи: качество сильно зависит от микрофона, шума, дикции, нескольких говорящих и языка.

---

# 35. Постобработка текста

Whisper отвечает именно за распознавание речи.

После него можно добавить отдельный этап:

```text
Аудио
  ↓
Whisper
  ↓
сырой текст
  ↓
постобработка
  ↓
готовый текст
```

Постобработка может исправлять:

* пунктуацию;
* регистр;
* очевидные опечатки;
* окончания слов;
* повторения;
* форматирование абзацев;
* технические термины;
* названия программ;
* имена собственные.

При этом желательно сохранять оригинальный результат Whisper отдельно.

Например:

```text
recording_raw.txt
recording.txt
```

где:

```text
recording_raw.txt
```

— буквальный результат Whisper,

а:

```text
recording.txt
```

— исправленный текст.

---

# 36. Словарь терминов

Для технических записей особенно полезно передавать Whisper список терминов.

Например:

```text
Whisper
NetBird
WireGuard
NAT
Linux
Arch Linux
EndeavourOS
GNOME
Nautilus
Dolphin
PySide6
Python
CUDA
NVIDIA
FFmpeg
```

Это помогает модели лучше интерпретировать специализированную лексику.

Для этого приложение можно расширить параметром `initial_prompt`.

---

# 37. Важное ограничение постобработки

Нельзя бездумно отправлять транскрипцию в обычный AI-корректор с инструкцией:

> Исправь все ошибки.

Языковая модель может изменить смысл сказанного.

Для транскрипции лучше использовать инструкцию вида:

```text
Исправляй только очевидные ошибки распознавания речи,
пунктуацию, грамматику и форматирование.

Не добавляй информацию, которой нет в исходном тексте.
Не меняй смысл.
Если слово или фраза неясны — оставь исходный вариант.
Не сокращай текст.
Не пересказывай текст.
```

Для полностью локальной обработки можно использовать локальную LLM вместо облачного API.

---

# 38. Итоговая структура системы

После полной установки система выглядит так:

```text
~/Applications/whisper/
│
├── .venv/
│   ├── bin/
│   │   ├── python
│   │   ├── pip
│   │   └── whisper
│   └── ...
│
├── whisper/
├── README.md
├── setup.py
└── ...
│
├── ~/.cache/whisper/
│   └── модели Whisper
│
├── ~/.local/share/whisper-local/
│   └── app.py
│
├── ~/.local/bin/
│   └── whisper-local
│
└── ~/.local/share/applications/
    └── whisper-local.desktop
```

Логика работы:

```text
GNOME Menu
    │
    ▼
whisper-local.desktop
    │
    ▼
~/.local/bin/whisper-local
    │
    ▼
~/Applications/whisper/.venv/bin/python
    │
    ▼
whisper-local/app.py
    │
    ▼
OpenAI Whisper
    │
    ▼
локальная модель
    │
    ▼
локальная транскрипция
```

Интернет/API для самой транскрипции не используется.

---

# 39. Минимальная команда для полного запуска

После завершения установки пользователю больше не требуется активировать окружение.

Для GUI достаточно:

```bash
~/.local/bin/whisper-local
```

А в обычной работе приложение запускается:

```text
Меню GNOME → Whisper Local
```

---

# 40. Быстрый вариант установки с нуля

Если всё вышеперечисленное уже понятно, полный набор команд для EndeavourOS выглядит так:

```bash
sudo pacman -S --needed git python python-pip ffmpeg
```

```bash
mkdir -p ~/Applications
cd ~/Applications
```

```bash
git clone https://github.com/openai/whisper.git
```

```bash
cd ~/Applications/whisper
```

```bash
python -m venv .venv
```

```bash
source .venv/bin/activate
```

```bash
python -m pip install --upgrade pip setuptools wheel
```

```bash
python -m pip install -e .
```

```bash
python -m pip install PySide6
```

Проверка:

```bash
whisper --help
```

```bash
python -c "import whisper; print(whisper.available_models())"
```

```bash
python -c "import torch; print('CUDA:', torch.cuda.is_available())"
```

После этого устанавливается GUI и desktop launcher из разделов выше.

---

# 41. Главное

Не нужно создавать отдельное окружение для GUI.

Правильная схема:

```text
Whisper
+
PySide6
+
GUI
↓
один .venv
```

То есть:

```text
~/Applications/whisper/.venv/
```

содержит одновременно:

```text
OpenAI Whisper
PyTorch
PySide6
и все зависимости
```

Это позволяет приложению напрямую использовать уже установленный Whisper через Python API:

```python
import whisper

model = whisper.load_model("small")
result = model.transcribe("audio.mp3")
```

и запускать всё как обычное приложение из GNOME без ручного управления виртуальным окружением. Официальный Whisper поддерживает такой Python API.
