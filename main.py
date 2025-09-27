import nmap
import json


def interpret_nmap_scan(ip_address):
    """
    Выполняет сканирование nmap и интерпретирует результаты
    """
    nm = nmap.PortScanner()

    print(f"🎯 Выполняем: nmap {ip_address}")
    print("=" * 60)

    try:
        # Выполняем сканирование с определением ОС (более безопасные аргументы)
        nm.scan(hosts=ip_address, arguments='-O --osscan-limit')

        if ip_address not in nm.all_hosts():
            print(f"❌ Хост {ip_address} не найден или недоступен")
            return None

        host_info = nm[ip_address]

        # Интерпретация результатов
        interpret_results(host_info, ip_address)

        return host_info

    except Exception as e:
        print(f"⚠️ Ошибка при сканировании: {e}")
        # Попробуем простое сканирование без определения ОС
        return simple_scan(ip_address)


def simple_scan(ip_address):
    """
    Простое сканирование без определения ОС
    """
    print("\n🔄 Пробуем простое сканирование без определения ОС...")
    nm = nmap.PortScanner()

    try:
        nm.scan(hosts=ip_address, arguments='-sS')

        if ip_address not in nm.all_hosts():
            print(f"❌ Хост {ip_address} недоступен")
            return None

        host_info = nm[ip_address]
        interpret_results(host_info, ip_address)
        return host_info

    except Exception as e:
        print(f"❌ Ошибка при простом сканировании: {e}")
        return None


def safe_get_os_info(host_info):
    """
    Безопасное извлечение информации об ОС
    """
    try:
        if 'osmatch' in host_info:
            osmatch = host_info['osmatch']

            # Проверяем тип данных osmatch
            if isinstance(osmatch, list) and osmatch:
                return osmatch
            elif isinstance(osmatch, dict):
                return [osmatch]  # Преобразуем в список
            else:
                print(f"⚠️ Неожиданный формат данных OS: {type(osmatch)}")
                return []
        return []
    except Exception as e:
        print(f"⚠️ Ошибка при обработке данных ОС: {e}")
        return []


def detect_os(host_info, ip_address):
    """
    Определяет операционную систему хоста
    """
    print(f"\n🖥️ ОПРЕДЕЛЕНИЕ ОПЕРАЦИОННОЙ СИСТЕМЫ {ip_address}")
    print("-" * 50)

    osmatch_list = safe_get_os_info(host_info)

    if osmatch_list:
        print("📋 Обнаруженные операционные системы:")

        for i, os_match in enumerate(osmatch_list, 1):
            # Безопасное извлечение данных
            accuracy = os_match.get('accuracy', 'N/A') if isinstance(os_match, dict) else 'N/A'
            name = os_match.get('name', 'Неизвестно') if isinstance(os_match, dict) else str(os_match)

            print(f"\n{i}. {name}")
            print(f"   📊 Точность определения: {accuracy}%")

            if isinstance(os_match, dict) and 'osclass' in os_match:
                os_class = os_match['osclass']
                if isinstance(os_class, dict):
                    vendor = os_class.get('vendor', 'Неизвестно')
                    os_family = os_class.get('osfamily', 'Неизвестно')
                    os_gen = os_class.get('osgen', 'Неизвестно')
                    type = os_class.get('type', 'Неизвестно')

                    print(f"   🏢 Производитель: {vendor}")
                    print(f"   👨‍👩‍👧‍👦 Семейство ОС: {os_family}")
                    print(f"   🔄 Поколение ОС: {os_gen}")
                    print(f"   📝 Тип: {type}")
                else:
                    print(f"   📝 Класс ОС: {os_class}")

        # Выбираем наиболее вероятную ОС
        if isinstance(osmatch_list[0], dict):
            best_os = osmatch_list[0]
            best_accuracy = best_os.get('accuracy', '0')
            best_name = best_os.get('name', 'Неизвестно')

            print(f"\n🎯 Наиболее вероятная ОС: {best_name} (точность: {best_accuracy}%)")
            analyze_os_security(best_name, best_os)
        else:
            print(f"\n🎯 Обнаруженная ОС: {osmatch_list[0]}")

    else:
        print("❌ Не удалось определить операционную систему")
        print("💡 Возможные причины:")
        print("   - Хост недоступен для детального сканирования")
        print("   - Брандмауэр блокирует сканирование")
        print("   - Недостаточно данных для определения ОС")
        print("   - Требуются права администратора")


def analyze_os_security(os_name, os_info):
    """
    Анализирует безопасность обнаруженной ОС
    """
    print(f"\n🛡️ АНАЛИЗ БЕЗОПАСНОСТИ ОС:")
    print("-" * 30)

    if not isinstance(os_name, str):
        os_name = str(os_name)

    os_name_lower = os_name.lower()

    security_notes = []

    # Анализ Windows систем
    if 'windows' in os_name_lower:
        security_notes.append("✅ Windows система обнаружена")

        if any(x in os_name_lower for x in ['xp', '2000', '2003']):
            security_notes.append("⚠️ Устаревшая версия Windows - высокий риск уязвимостей")
        elif any(x in os_name_lower for x in ['7', 'vista']):
            security_notes.append("🔸 Windows 7/Vista - поддержка прекращена")
        elif any(x in os_name_lower for x in ['10', '11']):
            security_notes.append("✅ Современная версия Windows")

        security_notes.append("💡 Рекомендации: Проверьте обновления безопасности, настройки брандмауэра")

    # Анализ Linux систем
    elif 'linux' in os_name_lower:
        security_notes.append("✅ Linux система обнаружена")

        if 'ubuntu' in os_name_lower or 'debian' in os_name_lower:
            security_notes.append("💡 Дистрибутив на основе Debian")
        elif 'centos' in os_name_lower or 'red hat' in os_name_lower or 'rhel' in os_name_lower:
            security_notes.append("💡 Дистрибутив на основе RHEL")

        security_notes.append("🔍 Проверьте: конфигурацию firewall, обновления ядра")

    # Анализ других систем
    elif 'router' in os_name_lower or 'switch' in os_name_lower:
        security_notes.append("📡 Сетевое оборудование обнаружено")
    elif 'mac' in os_name_lower or 'darwin' in os_name_lower:
        security_notes.append("🍎 macOS система обнаружена")
    elif 'unix' in os_name_lower:
        security_notes.append("🐧 Unix-подобная система обнаружена")
    else:
        security_notes.append("🔍 Тип системы требует дополнительного анализа")

    # Общие рекомендации
    security_notes.append("💡 Общие рекомендации: Регулярно обновляйте систему")

    # Вывод рекомендаций
    for note in security_notes:
        print(f"   • {note}")


def interpret_results(host_info, ip_address):
    """
    Интерпретирует и анализирует результаты сканирования
    """
    print(f"\n📊 РЕЗУЛЬТАТЫ СКАНИРОВАНИЯ {ip_address}")
    print("=" * 50)

    # Статус хоста
    state = host_info.state()
    print(f"📍 Статус хоста: {state}")

    if state != 'up':
        print("💡 Хост не активен - дальнейшее сканирование невозможно")
        return

    # Определение операционной системы
    detect_os(host_info, ip_address)

    # Анализ протоколов
    protocols = host_info.all_protocols()
    print(f"\n📡 Обнаружено протоколов: {len(protocols)}")

    for protocol in protocols:
        print(f"\n🔍 Анализ {protocol.upper()} портов:")
        print("-" * 40)

        ports = host_info[protocol]
        open_ports = [p for p in ports if ports[p]['state'] == 'open']
        filtered_ports = [p for p in ports if ports[p]['state'] == 'filtered']
        closed_ports = [p for p in ports if ports[p]['state'] == 'closed']

        print(f"✅ Открытых портов: {len(open_ports)}")
        print(f"🛡️ Фильтруемых портов: {len(filtered_ports)}")
        print(f"❌ Закрытых портов: {len(closed_ports)}")

        # Детальный анализ открытых портов
        if open_ports:
            print(f"\n📋 Детали открытых портов:")
            for port in sorted(open_ports):
                port_info = ports[port]
                analyze_port(port, port_info, protocol)
        else:
            print("ℹ️ Открытых портов не обнаружено")


def analyze_port(port, port_info, protocol):
    """
    Анализирует конкретный порт и предоставляет информацию о нём
    """
    try:
        service = port_info.get('name', 'unknown')
        product = port_info.get('product', '')
        version = port_info.get('version', '')

        print(f"   🚪 Порт {protocol}/{port}: {service}")

        # Определение типа службы и рекомендации
        service_analysis = analyze_service_type(port, service, product)
        if service_analysis:
            print(f"      💡 {service_analysis}")

        if product or version:
            print(f"      📦 {product} {version}".strip())
    except Exception as e:
        print(f"   ⚠️ Ошибка анализа порта {port}: {e}")


def analyze_service_type(port, service_name, product):
    """
    Анализирует тип службы на основе порта и имени
    """
    try:
        # Веб-сервисы
        web_ports = [80, 443, 8080, 8443, 8000, 3000]
        if port in web_ports or 'http' in str(service_name) or 'apache' in str(product).lower() or 'nginx' in str(
                product).lower():
            return "Веб-сервер - проверьте наличие веб-интерфейса"

        # SSH/SFTP
        if port == 22 or 'ssh' in str(service_name):
            return "SSH сервис - возможен удалённый доступ"

        # Базы данных
        db_ports = [21, 3306, 5432, 27017, 1433]
        db_services = ['ftp', 'mysql', 'postgresql', 'mongodb', 'mssql']
        if port in db_ports or any(db in str(service_name) for db in db_services):
            return "Сервис базы данных - проверьте безопасность"

        # Удалённое управление
        remote_ports = [3389, 5900, 5800, 23]
        if port in remote_ports or 'rdp' in str(service_name) or 'vnc' in str(service_name) or 'telnet' in str(
                service_name):
            return "Сервис удалённого управления - может быть уязвим"

        # Почтовые сервисы
        mail_ports = [25, 110, 143, 465, 587, 993, 995]
        if port in mail_ports or 'smtp' in str(service_name) or 'pop3' in str(service_name) or 'imap' in str(
                service_name):
            return "Почтовый сервис - проверьте конфигурацию"

        return None
    except Exception as e:
        return f"Ошибка анализа службы: {e}"


def generate_security_report(host_info, ip_address):
    """
    Генерирует краткий отчёт о безопасности
    """
    print(f"\n🛡️ ОТЧЁТ БЕЗОПАСНОСТИ ДЛЯ {ip_address}")
    print("=" * 50)

    security_notes = []

    try:
        for protocol in host_info.all_protocols():
            ports = host_info[protocol]
            open_ports = [p for p in ports if ports[p]['state'] == 'open']

            for port in open_ports:
                port_info = ports[port]
                service = port_info.get('name', 'unknown')

                # Проверка потенциально опасных портов
                if port in [21, 23, 135, 139, 445]:
                    security_notes.append(f"⚠️ Порт {port} ({service}) - потенциально уязвим")

                if 'telnet' in str(service) and port == 23:
                    security_notes.append(f"🔓 Telnet на порту 23 - небезопасный протокол")

                if 'ftp' in str(service) and port == 21:
                    security_notes.append(f"📁 FTP на порту 21 - проверьте анонимный доступ")

        if security_notes:
            for note in security_notes:
                print(note)
        else:
            print("✅ Потенциально опасных служб не обнаружено")
    except Exception as e:
        print(f"⚠️ Ошибка генерации отчёта безопасности: {e}")


# Главная функция выполнения
def main():
    ip_address = input("Введите IP-адресс: ")  # Ваш целевой IP

    print("🔍 ИНТЕРПРЕТАТОР NMAP СКАНИРОВАНИЯ С ОПРЕДЕЛЕНИЕМ ОС")
    print("=" * 60)

    # Выполняем сканирование
    results = interpret_nmap_scan(ip_address)

    if results:
        # Генерируем отчёт безопасности
        generate_security_report(results, ip_address)

        # Дополнительная информация
        print(f"\n💾 Сканирование завершено")
        print(f"📧 Хост: {ip_address}")
        print(f"📊 Статус: {results.state()}")

    else:
        print("❌ Сканирование не удалось")


if __name__ == "__main__":
    main()

