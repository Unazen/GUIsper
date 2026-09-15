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

(Все операции распознавания выполняются локально. Само GUI-приложение не содержит обращения к OpenAI API или облачному сервису.
> Важно: при первом запуске конкретной модели Whisper может скачать её веса из интернета. После загрузки модель хранится локально в кеше Whisper и используется без повторной загрузки.)
# 1. Требования

* EndeavourOS / Arch Linux (в ином случае приложения устанавливаются командами вашего дистрибутива);
* Python 3;
* NVIDIA GPU или CPU;
* GNOME или другое Linux desktop environment (инструкция сделана для меню Гнома);
* доступ в интернет на этапе установки и первого скачивания моделей.
Для NVIDIA необходимо, чтобы драйвер уже был установлен и работал.

Проверить GPU:
```bash
nvidia-smi
```

Проверить Python:
```bash
python --version
```

Проверить Git:
```bash
git --version
```

Проверить FFmpeg:
```bash
ffmpeg -version
```
---

# 2. Быстрый вариант установки с нуля

Установка зависимостей:
```bash
sudo pacman -S --needed git python python-pip ffmpeg
```

Создание каталога (рекомендуемый вариант):
```bash
mkdir -p ~/Applications
cd ~/Applications
```

Клонирование репозитория Whisper:
```bash
git clone https://github.com/openai/whisper.git
```

Переход в каталог:
```bash
cd ~/Applications/whisper
```

Создание виртуального окружения Python:
```bash
python -m venv .venv
```

Активация:
```bash
source .venv/bin/activate
```

Установка пайтон-зависимостей
```bash
python -m pip install --upgrade pip setuptools wheel
```

Установка из локального гит репозитория:
```bash
python -m pip install -e .
```

Установка Pyside:
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


# 3. Установка приложения Whisper Local

Содержание репозитория:
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

# 4. Структура готовой установки
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


# 5. Важное ограничение постобработки

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


# 7. Логика работы:

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