#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import subprocess
import socket
import threading
import platform
from PIL import Image, ImageTk
import sys


class ConnectionManager:
    def __init__(self):
        self.devices = {
            '198.18.200.193': {'protocol': 'telnet', 'port': 23, 'name': 'Сетевое устройство (Telnet)'},
            '198.18.200.49': {'protocol': 'ssh', 'port': 22, 'name': 'Сервер Linux (SSH)'},
            '198.18.200.48': {'protocol': 'vnc', 'port': 5900, 'name': 'Виртуальная машина (VNC)'},
            '198.18.200.213': {'protocol': 'rdp', 'port': 3389, 'name': 'Windows сервер (RDP)'}
        }

    def detect_protocol(self, ip):
        """Автоматическое определение протокола"""
        if ip in self.devices:
            return self.devices[ip]['protocol'], self.devices[ip]['port']

        protocols = [
            ('ssh', 22),
            ('telnet', 23),
            ('rdp', 3389),
            ('vnc', 5900)
        ]

        for protocol, port in protocols:
            if self.test_port(ip, port):
                return protocol, port

        return None, None

    def test_port(self, ip, port, timeout=2):
        """Проверка доступности порта"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((ip, port))
            sock.close()
            return result == 0
        except:
            return False


class ModernRemoteConnectionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🚀 Remote Connection Manager Pro")
        self.root.geometry("700x600")
        self.root.resizable(True, True)
        self.root.configure(bg='#2c3e50')

        # Установка стиля
        self.setup_styles()

        self.conn_manager = ConnectionManager()
        self.setup_ui()

    def setup_styles(self):
        """Настройка современных стилей"""
        style = ttk.Style()
        style.theme_use('clam')

        # Настройка цветов
        style.configure('TFrame', background='#2c3e50')
        style.configure('TLabel', background='#2c3e50', foreground='white', font=('Arial', 10))
        style.configure('Title.TLabel', background='#2c3e50', foreground='#3498db',
                        font=('Arial', 18, 'bold'))
        style.configure('Protocol.TLabel', background='#34495e', foreground='#ecf0f1',
                        font=('Arial', 11, 'bold'))
        style.configure('Success.TLabel', background='#2c3e50', foreground='#2ecc71')
        style.configure('Error.TLabel', background='#2c3e50', foreground='#e74c3c')

        style.configure('TButton', font=('Arial', 10, 'bold'), padding=10)
        style.map('Accent.TButton',
                  background=[('active', '#2980b9'), ('pressed', '#1c638e')])
        style.configure('Accent.TButton', background='#3498db', foreground='white')

        style.configure('TCombobox', padding=5)
        style.configure('TEntry', padding=5)

    def setup_ui(self):
        """Создание современного интерфейса"""
        # Создание вкладок
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)

        # Вкладка подключения
        conn_frame = ttk.Frame(notebook, padding=20)
        notebook.add(conn_frame, text='🔌 Подключение')

        # Вкладка инструкции
        help_frame = ttk.Frame(notebook)
        notebook.add(help_frame, text='📖 Инструкция')

        self.setup_connection_tab(conn_frame)
        self.setup_help_tab(help_frame)

    def setup_connection_tab(self, parent):
        """Настройка вкладки подключения"""
        # Заголовок
        title_label = ttk.Label(parent, text="Удаленное подключение к устройствам",
                                style='Title.TLabel')
        title_label.pack(pady=(0, 20))

        # Основной контейнер
        main_container = ttk.Frame(parent)
        main_container.pack(fill='both', expand=True)

        # Левая панель - устройства
        left_frame = ttk.LabelFrame(main_container, text="📱 Выбор устройства", padding=15)
        left_frame.pack(side='left', fill='y', padx=(0, 10))

        # Правая панель - аутентификация
        right_frame = ttk.LabelFrame(main_container, text="🔐 Аутентификация", padding=15)
        right_frame.pack(side='right', fill='both', expand=True)

        self.setup_devices_panel(left_frame)
        self.setup_auth_panel(right_frame)

    def setup_devices_panel(self, parent):
        """Панель выбора устройств"""
        # Предустановленные устройства
        ttk.Label(parent, text="Быстрый выбор:").pack(anchor='w', pady=(0, 10))

        self.device_var = tk.StringVar()
        device_listbox = tk.Listbox(parent, height=6, font=('Arial', 10),
                                    bg='#34495e', fg='white', selectbackground='#3498db')

        for ip, info in self.conn_manager.devices.items():
            device_listbox.insert(tk.END, f"{info['name']}\nIP: {ip}")

        device_listbox.pack(fill='x', pady=(0, 15))
        device_listbox.bind('<<ListboxSelect>>', self.on_device_select)

        # Ручной ввод IP
        ttk.Label(parent, text="Или введите IP вручную:").pack(anchor='w', pady=(10, 5))

        ip_frame = ttk.Frame(parent)
        ip_frame.pack(fill='x', pady=(0, 15))

        self.ip_var = tk.StringVar()
        ip_entry = ttk.Entry(ip_frame, textvariable=self.ip_var, font=('Arial', 11))
        ip_entry.pack(side='left', fill='x', expand=True)
        ip_entry.bind('<KeyRelease>', self.on_ip_change)

        # Кнопка проверки
        test_btn = ttk.Button(ip_frame, text="Проверить", command=self.test_connection,
                              style='Accent.TButton', width=10)
        test_btn.pack(side='right', padx=(5, 0))

        # Информация о протоколе
        protocol_frame = ttk.Frame(parent, relief='solid', borderwidth=1)
        protocol_frame.pack(fill='x', pady=(10, 0))

        ttk.Label(protocol_frame, text="Информация о подключении:",
                  font=('Arial', 10, 'bold')).pack(anchor='w', pady=(5, 10))

        self.protocol_label = ttk.Label(protocol_frame, text="Протокол: Не выбран",
                                        style='Protocol.TLabel')
        self.protocol_label.pack(anchor='w', pady=2)

        self.port_label = ttk.Label(protocol_frame, text="Порт: -", style='Protocol.TLabel')
        self.port_label.pack(anchor='w', pady=2)

        self.status_label = ttk.Label(protocol_frame, text="Статус: Ожидание",
                                      style='Protocol.TLabel')
        self.status_label.pack(anchor='w', pady=2)

    def setup_auth_panel(self, parent):
        """Панель аутентификации"""
        # Поля ввода
        auth_frame = ttk.Frame(parent)
        auth_frame.pack(fill='both', expand=True)

        # Логин
        ttk.Label(auth_frame, text="Логин:", font=('Arial', 11, 'bold')).pack(anchor='w', pady=(10, 5))
        self.username_var = tk.StringVar()
        username_entry = ttk.Entry(auth_frame, textvariable=self.username_var,
                                   font=('Arial', 12), width=30)
        username_entry.pack(fill='x', pady=(0, 15))

        # Пароль
        ttk.Label(auth_frame, text="Пароль:", font=('Arial', 11, 'bold')).pack(anchor='w', pady=(5, 5))
        self.password_var = tk.StringVar()
        password_entry = ttk.Entry(auth_frame, textvariable=self.password_var,
                                   show="•", font=('Arial', 12), width=30)
        password_entry.pack(fill='x', pady=(0, 20))

        # Кнопка подключения
        self.connect_button = ttk.Button(auth_frame, text="🚀 УСТАНОВИТЬ ПОДКЛЮЧЕНИЕ",
                                         command=self.connect, style='Accent.TButton',
                                         state=tk.DISABLED)
        self.connect_button.pack(fill='x', pady=10)

        # Прогресс бар
        self.progress = ttk.Progressbar(auth_frame, mode='indeterminate')
        self.progress.pack(fill='x', pady=5)

        # История подключений
        history_frame = ttk.LabelFrame(auth_frame, text="📊 История подключений", padding=10)
        history_frame.pack(fill='both', expand=True, pady=(20, 0))

        self.history_text = scrolledtext.ScrolledText(history_frame, height=6,
                                                      bg='#ecf0f1', font=('Arial', 9))
        self.history_text.pack(fill='both', expand=True)
        self.history_text.config(state=tk.DISABLED)

        # Обновление состояния кнопки
        username_entry.bind('<KeyRelease>', self.check_fields)
        password_entry.bind('<KeyRelease>', self.check_fields)

    def setup_help_tab(self, parent):
        """Вкладка с инструкцией"""
        help_text = """
📋 КРАТКАЯ ИНСТРУКЦИЯ ПО ИСПОЛЬЗОВАНИЮ

1. 🚀 БЫСТРОЕ ПОДКЛЮЧЕНИЕ:
   • Выберите устройство из списка "Быстрый выбор"
   • Или введите IP-адрес вручную и нажмите "Проверить"

2. 🔐 АУТЕНТИФИКАЦИЯ:
   • Введите логин в поле "Логин"
   • Введите пароль в поле "Пароль"
   • Нажмите "УСТАНОВИТЬ ПОДКЛЮЧЕНИЕ"

3. 🔄 АВТОМАТИЧЕСКОЕ ОПРЕДЕЛЕНИЕ:
   • Скрипт автоматически определит протокол подключения
   • Отобразит информацию о порте и статусе

4. 📊 ПОДДЕРЖИВАЕМЫЕ ПРОТОКОЛЫ:
   ✅ SSH - для Linux/Unix серверов
   ✅ Telnet - для сетевого оборудования
   ✅ RDP - для Windows серверов
   ✅ VNC - для удаленного рабочего стола

5. ⚠️ ТРЕБОВАНИЯ:
   • Для RDP на Windows: встроенный клиент
   • Для SSH: установленный ssh-клиент
   • Для VNC: VNC Viewer
   • Для Telnet: включенный telnet-клиент

6. 🛠️ УСТРАНЕНИЕ НЕПОЛАДОК:
   • Проверьте доступность устройства (ping)
   • Убедитесь в правильности логина/пароля
   • Проверьте настройки брандмауэра

7. 💡 ПОДСКАЗКИ:
   • Двойной клик по устройству для быстрого выбора
   • Enter для быстрого подключения после ввода пароля
   • История подключений сохраняется во время сессии

   Desktop2Proxy WHAT 27.09.2025
(ссылка на репозиторий)

Репозиторий содержит в себе исполняемые файлы main.py, connectud.py, desired_outcome.py, readme.txt

Целями main.py являются:

1. Определение открытых портов и поддерживаемых протоколов в вводимом пользователем
сетевом интерфейсе или операционной системе
2. Определение операционной системы и ее версии, которая стоит на сетевом интерфейсе, указываемом
пользователем
3. Проведение анализза безопасности операционной системы, которая стоит на сетевом
интерфейсе (фича)

Используемые библиотеки и зависимости: nmap, json



Целями connectud.py являются:

1. Запрос данных от пользователя (ip-адрес, логин, пароль) для дальнейшего удаленного подключения
к сетевым интерфейсам и операционным системам на основе поддерживаемых протоколов
2. Удаленное подключение через: vnc, ssh, rdp, telnet
3. Вывод интерфейса (командной строки, например) для дальнейшего администрирования
сетевых интерфейсов и операционных систем

Требования: 
1. Для работы Telnet на Windows необходимо включение компонента Windows "Клиент Telnet"
2. Для работы vnc необходим vncviewer
3. Для работы RDP на Windows необходимо через редактор групповых политик Windows включить защиту от
атак с использованием криптографического оракула и в "Уровень защиты" указать "Оставить уязвимость"

Используемые библиотеки и зависимости: subprocess, socket, threading, platform, tkinter



desired_outcome.py содержит в себе прототип программы и код, который может помочь при дальнейшей разработке


Инструкция:

main.py:
1. Введите IP-адресс
2. Ожидайте результата анализа хоста при помощи nmap

connectud.py:
1. Выберите один из существующих сетевых интерфесов (Выбор устройства)
2. Введите логин и пароль
3. Более подробные инструкции имеются в разделе "Инструкции"
p.s. работает пока только rdp, кроме Windows 11. Программа требует доработок, особенно в подключении





        """

        help_text_widget = scrolledtext.ScrolledText(parent, wrap=tk.WORD,
                                                     bg='#ecf0f1', font=('Arial', 11))
        help_text_widget.pack(fill='both', expand=True, padx=10, pady=10)
        help_text_widget.insert('1.0', help_text)
        help_text_widget.config(state=tk.DISABLED)

    def on_device_select(self, event):
        """Обработка выбора устройства из списка"""
        widget = event.widget
        selection = widget.curselection()
        if selection:
            index = selection[0]
            ip = list(self.conn_manager.devices.keys())[index]
            self.ip_var.set(ip)
            self.update_protocol_info(ip)
            self.add_to_history(f"Выбрано устройство: {self.conn_manager.devices[ip]['name']}")

    def on_ip_change(self, event):
        """Обработка ручного ввода IP"""
        ip = self.ip_var.get()
        self.update_protocol_info(ip)

    def test_connection(self):
        """Тестирование подключения"""
        ip = self.ip_var.get()
        if not ip:
            messagebox.showwarning("Внимание", "Введите IP-адрес для проверки")
            return

        thread = threading.Thread(target=self._test_connection_thread, args=(ip,))
        thread.daemon = True
        thread.start()

    def _test_connection_thread(self, ip):
        """Поток для тестирования подключения"""
        self.root.after(0, lambda: self.status_label.config(text="Статус: Проверка..."))
        self.root.after(0, self.progress.start)

        try:
            # Проверка ping
            param = '-n' if platform.system().lower() == 'windows' else '-c'
            result = subprocess.run(['ping', param, '1', ip],
                                    capture_output=True, text=True, timeout=5)

            if result.returncode == 0:
                protocol, port = self.conn_manager.detect_protocol(ip)
                if protocol:
                    self.root.after(0, lambda: self.status_label.config(
                        text=f"Статус: Доступно ({protocol.upper()})"))
                    self.root.after(0, lambda: self.add_to_history(f"✓ Устройство {ip} доступно"))
                else:
                    self.root.after(0, lambda: self.status_label.config(
                        text="Статус: Доступно (протокол не определен)"))
            else:
                self.root.after(0, lambda: self.status_label.config(text="Статус: Недоступно"))
                self.root.after(0, lambda: self.add_to_history(f"✗ Устройство {ip} недоступно"))

        except Exception as e:
            self.root.after(0, lambda: self.status_label.config(text="Статус: Ошибка проверки"))
            self.root.after(0, lambda: self.add_to_history(f"! Ошибка проверки {ip}: {str(e)}"))

        finally:
            self.root.after(0, self.progress.stop)

    def update_protocol_info(self, ip):
        """Обновление информации о протоколе"""
        if ip:
            protocol, port = self.conn_manager.detect_protocol(ip)
            if protocol:
                self.protocol_label.config(text=f"Протокол: {protocol.upper()}")
                self.port_label.config(text=f"Порт: {port}")
                device_name = self.conn_manager.devices.get(ip, {}).get('name', 'Пользовательское устройство')
                self.add_to_history(f"Обнаружено: {device_name} ({protocol.upper()})")
            else:
                self.protocol_label.config(text="Протокол: Не определен")
                self.port_label.config(text="Порт: -")
        else:
            self.protocol_label.config(text="Протокол: Не выбран")
            self.port_label.config(text="Порт: -")

        self.check_fields()

    def check_fields(self, event=None):
        """Проверка заполнения полей"""
        ip = self.ip_var.get()
        username = self.username_var.get()
        password = self.password_var.get()

        if ip and username and password:
            self.connect_button.config(state=tk.NORMAL)
        else:
            self.connect_button.config(state=tk.DISABLED)

    def add_to_history(self, message):
        """Добавление сообщения в историю"""
        self.history_text.config(state=tk.NORMAL)
        self.history_text.insert(tk.END, f"{message}\n")
        self.history_text.see(tk.END)
        self.history_text.config(state=tk.DISABLED)

    def connect(self):
        """Установка подключения"""
        ip = self.ip_var.get()
        username = self.username_var.get()
        password = self.password_var.get()

        protocol, port = self.conn_manager.detect_protocol(ip)

        if not protocol:
            messagebox.showerror("Ошибка", f"Не удалось определить протокол для {ip}")
            return

        self.add_to_history(f"⌛ Подключение к {ip} по {protocol.upper()}...")

        # Запуск в отдельном потоке
        thread = threading.Thread(target=self.establish_connection,
                                  args=(ip, protocol, port, username, password))
        thread.daemon = True
        thread.start()

    def establish_connection(self, ip, protocol, port, username, password):
        """Установка соединения в отдельном потоке"""
        self.root.after(0, lambda: self.status_label.config(text="Статус: Подключение..."))
        self.root.after(0, self.progress.start)
        self.root.after(0, lambda: self.connect_button.config(state=tk.DISABLED))

        try:
            success = False
            if protocol == 'ssh':
                success = self.connect_ssh(ip, username, password, port)
            elif protocol == 'telnet':
                success = self.connect_telnet(ip, username, password, port)
            elif protocol == 'rdp':
                success = self.connect_rdp(ip, username, password, port)
            elif protocol == 'vnc':
                success = self.connect_vnc(ip, username, password, port)
            else:
                self.root.after(0, lambda: messagebox.showerror("Ошибка", f"Протокол {protocol} не поддерживается"))

            if success:
                self.root.after(0, self.show_success)
            else:
                self.root.after(0, lambda: self.show_error("Подключение не удалось"))

        except Exception as e:
            self.root.after(0, lambda: self.show_error(f"Ошибка подключения: {str(e)}"))
        finally:
            self.root.after(0, self.progress.stop)
            self.root.after(0, lambda: self.connect_button.config(state=tk.NORMAL))

    def connect_ssh(self, ip, username, password, port=22):
        """Подключение по SSH"""
        try:
            if platform.system() == "Windows":
                subprocess.Popen(['putty', f'-ssh', f'{username}@{ip}', f'-P', str(port), f'-pw', password])
            else:
                subprocess.Popen(['xterm', '-e', f'ssh {username}@{ip} -p {port}'])
            return True
        except Exception as e:
            self.add_to_history(f"✗ SSH ошибка: {str(e)}")
            return False

    def connect_telnet(self, ip, username, password, port=23):
        """Подключение по Telnet"""
        try:
            if platform.system() == "Windows":
                subprocess.Popen(['telnet', ip, str(port)])
            else:
                subprocess.Popen(['xterm', '-e', f'telnet {ip} {port}'])
            return True
        except Exception as e:
            self.add_to_history(f"✗ Telnet ошибка: {str(e)}")
            return False

    def connect_rdp(self, ip, username, password, port=3389):
        """Подключение по RDP"""
        try:
            if platform.system() == "Windows":
                subprocess.Popen(['mstsc', f'/v:{ip}:{port}'])
            else:
                subprocess.Popen(['xfreerdp', f'/v:{ip}:{port}', f'/u:{username}', f'/p:{password}'])
            return True
        except Exception as e:
            self.add_to_history(f"✗ RDP ошибка: {str(e)}")
            return False

    def connect_vnc(self, ip, username, password, port=5900):
        """Подключение по VNC"""
        try:
            subprocess.Popen(['vncviewer', f'{ip}:{port}'])
            return True
        except Exception as e:
            self.add_to_history(f"✗ VNC ошибка: {str(e)}")
            return False

    def show_success(self):
        """Показать сообщение об успешном подключении"""
        self.status_label.config(text="Статус: Подключено")
        self.add_to_history("✓ Подключение установлено успешно!")
        messagebox.showinfo("Успех",
                            "Подключение успешно установлено!\nУправление устройством доступно в открывшемся окне.")

    def show_error(self, message):
        """Показать сообщение об ошибке"""
        self.status_label.config(text="Статус: Ошибка")
        self.add_to_history(f"✗ {message}")
        messagebox.showerror("Ошибка", message)


def main():
    try:
        root = tk.Tk()
        app = ModernRemoteConnectionApp(root)
        root.mainloop()
    except Exception as e:
        print(f"Ошибка запуска приложения: {e}")


if __name__ == "__main__":
    main()