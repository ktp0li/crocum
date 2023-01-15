# Netlab
## RU:
### Концепция:
Ресурс для подготовки сетевых инженеров, содержащий текстовые обучающие материалы и лабораторные работы.
### Реализация:
Система виртуализации — OpenNebula. Виртуальные машины создаются посредством Terraform. Уровень готовности лабораторной работы определяется через тесты, написанные на pytest с модулем testinfra, запускаемые через гостевой агент QEMU. Конечная форма — API.
### Cхема тестовой лабораторной:
![alt text](netplan.svg)
### Todo:
- [X] Написать tf-конфиги и отладить
- [X] Разобраться с QEMU guest agent и написать скрипты для автоматизации работы с ним
- [X] Написать пробный тест, проверить на работоспособность
- [ ] Написать тесты для лабораторной
- [ ] Написать документацию для лабораторной
- [ ] Написать обвязку для работы контекстуализации Opennebula на OPNsense
- [ ] Перенести тестовый экземпляр OpenNebula с linux bridge на Open vSwitch
- [ ] Настроить Seph
- [ ] Закончить образы ОС
- [ ] Написать базовый рабочий API, создающий и уничтожающий лабораторку
- [ ] Добавить БД для работы с пользователями
- [ ] Создать примитивный фронт
