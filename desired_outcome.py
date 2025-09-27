import tkinter as tk
from tkinter import ttk, messagebox
import nmap
import paramiko
import socket
import subprocess
import sys
from threading import Thread


class HostConnector:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Подключение к хосту")
        self.root.geometry("400x300")

        self.setup_ui()

    def setup_ui(self):
        # Логин
        tk.Label(self.root, text="Логин:").pack(pady=5)
        self.login_entry = tk.Entry(self.root, width=30)
        self.login_entry.pack(pady=5)

        # Пароль
        tk.Label(self.root, text="Пароль:").pack(pady=5)
        self.password_entry = tk.Entry(self.root, width=30, show="*")
        self.password_entry.pack(pady=5)

        # IP-адрес
        tk.Label(self.root, text="IP-адрес:").pack(pady=5)
        self.ip_entry = tk.Entry(self.root, width=30)
        self.ip_entry.pack(pady=5)

        # Прогресс бар
        self.progress = ttk.Progressbar(self.root, mode='indeterminate')
        self.progress.pack(pady=10, fill=tk.X, padx=20)

        # Кнопка подключения
        self.connect_btn = tk.Button(self.root, text="Подключиться",
                                     command=self.start_connection)
        self.connect_btn.pack(pady=20)

        # Текстовая область для логов
        self.log_text = tk.Text(self.root, height=8, width=50)
        self.log_text.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)

    def log_message(self, message):
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.root.update()

    def scan_protocols(self, ip):
        """Сканирование доступных протоколов с помощью nmap"""
        self.log_message(f"Сканирование протоколов на {ip}...")

        nm = nmap.PortScanner()

        try:
            # Сканируем основные порты для распространенных протоколов
            nm.scan(ip, arguments='-T4 -F')

            open_ports = []
            for protocol in nm[ip].all_protocols():
                ports = nm[ip][protocol].keys()
                for port in ports:
                    if nm[ip][protocol][port]['state'] == 'open':
                        open_ports.append((port, protocol))

            self.log_message(f"Найдено открытых портов: {len(open_ports)}")
            return open_ports

        except Exception as e:
            self.log_message(f"Ошибка сканирования: {e}")
            return []

    def test_ssh_connection(self, ip, username, password, port=22):
        """Проверка SSH подключения"""
        try:
            self.log_message(f"Попытка SSH подключения на порт {port}...")
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(ip, port=port, username=username, password=password, timeout=10)
            return ssh
        except Exception as e:
            self.log_message(f"SSH подключение не удалось: {e}")
            return None

    def test_telnet_connection(self, ip, username, password, port=23):
        """Проверка Telnet подключения (упрощенная версия)"""
        try:
            self.log_message(f"Попытка Telnet подключения на порт {port}...")
            # Для telnet потребуется дополнительная библиотека telnetlib
            # Здесь упрощенная проверка
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((ip, port))
            sock.close()

            if result == 0:
                self.log_message(f"Telnet порт {port} доступен")
                return True
            return False
        except Exception as e:
            self.log_message(f"Telnet проверка не удалась: {e}")
            return False

    def start_interactive_session(self, protocol, ip, username, password, port):
        """Запуск интерактивной сессии"""
        if protocol == 'tcp' and port in [22, 2222, 22222]:  # SSH порты
            self.log_message("Запуск SSH сессии...")
            try:
                # Запускаем SSH клиент в отдельном потоке
                ssh_thread = Thread(target=self.run_ssh_session,
                                    args=(ip, username, password, port))
                ssh_thread.daemon = True
                ssh_thread.start()

            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось запустить SSH: {e}")

        else:
            messagebox.showinfo("Информация",
                                f"Ручное подключение по протоколу {protocol} на порту {port}")

    def run_ssh_session(self, ip, username, password, port):
        """Запуск SSH сессии в консоли"""
        try:
            # Команда для запуска SSH подключения
            if sys.platform == "win32":
                # Для Windows можно использовать putty или openssh если установлен
                cmd = f"ssh {username}@{ip} -p {port}"
                subprocess.run(cmd, shell=True)
            else:
                # Для Linux/Mac
                cmd = f"ssh {username}@{ip} -p {port}"
                subprocess.run(cmd, shell=True)

        except Exception as e:
            self.log_message(f"Ошибка SSH сессии: {e}")

    def start_connection(self):
        """Основная функция подключения"""
        username = self.login_entry.get()
        password = self.password_entry.get()
        ip = self.ip_entry.get()

        if not all([username, password, ip]):
            messagebox.showerror("Ошибка", "Заполните все поля")
            return

        self.connect_btn.config(state='disabled')
        self.progress.start()
        self.log_text.delete(1.0, tk.END)

        # Запускаем в отдельном потоке чтобы не блокировать GUI
        thread = Thread(target=self.connect_thread, args=(ip, username, password))
        thread.daemon = True
        thread.start()

    def connect_thread(self, ip, username, password):
        """Поток для установления соединения"""
        try:
            # Сканируем протоколы
            open_ports = self.scan_protocols(ip)

            if not open_ports:
                self.root.after(0, lambda: messagebox.showerror("Ошибка",
                                                                "Не найдено открытых портов или хост недоступен"))
                return

            # Сортируем порты по приоритету (SSH первым)
            prioritized_ports = sorted(open_ports,
                                       key=lambda x: (0 if x[0] == 22 else
                                                      1 if x[0] in [2222, 22222] else
                                                      2 if x[0] == 23 else 3))

            self.log_message("Проверка доступных протоколов...")

            # Пробуем SSH подключение на стандартных портах
            for port, protocol in prioritized_ports:
                if protocol == 'tcp' and port in [22, 2222, 22222]:
                    ssh = self.test_ssh_connection(ip, username, password, port)
                    if ssh:
                        self.root.after(0, lambda: self.on_successful_connection(
                            'ssh', ip, username, password, port, ssh))
                        return

            # Если SSH не сработал, пробуем другие протоколы
            for port, protocol in prioritized_ports:
                if protocol == 'tcp' and port == 23:  # Telnet
                    if self.test_telnet_connection(ip, username, password, port):
                        self.root.after(0, lambda: self.on_successful_connection(
                            'telnet', ip, username, password, port, None))
                        return

            self.root.after(0, lambda: messagebox.showerror("Ошибка",
                                                            "Не удалось установить соединение ни по одному протоколу"))

        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Ошибка", f"Ошибка: {e}"))
        finally:
            self.root.after(0, self.connection_finished)

    def on_successful_connection(self, protocol, ip, username, password, port, connection):
        """Обработка успешного подключения"""
        self.log_message(f"Успешное подключение по {protocol} на порту {port}")

        if messagebox.askyesno("Успех",
                               f"Подключение установлено по {protocol} (порт {port})\n"
                               "Запустить интерактивную сессию?"):
            self.start_interactive_session(protocol, ip, username, password, port)

    def connection_finished(self):
        """Завершение процесса подключения"""
        self.progress.stop()
        self.connect_btn.config(state='normal')

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    # Проверка зависимостей
    try:
        import nmap
        import paramiko
    except ImportError as e:
        print("Установите необходимые зависимости:")
        print("pip install python-nmap paramiko")
        sys.exit(1)

    app = HostConnector()
    app.run()