# riceshine
Первый в мире (не уверен) `fetch` с центрированной информацией о системе, использует **rich, toml и psutil**

## Описание
Файлы конфигурации хранятся по пути `$HOME/.config/riceshine`:
- **ascii.txt** - ASCII арт, по умолчанию это бабочка
- **config.toml** - удобный конфиг, можно открыть введя `riceshine --settings`

## Конфигруация
Файл конфигурации состоит из трех секций. Здесь можно изменить стиль и цвет отображаемого текста, выключить или включить строки, изменить путь к ASCII арту
```toml
[colors]
ascii_art = "bold magenta"
title = "bold blue"
memory = "bold cyan"
disk = "bold cyan"
temp = "bold cyan"
ip = "bold green"
tcp = "bold green"
value = "white"

[display]
date_format = "%a %d %b %Y | %H:%M:%S"
show_uptime = true
show_load = true
show_memory = true
show_disk = true
show_temp = true
show_ip = true
show_tcp = true
expand_ascii = false

[paths]
ascii_art = "$HOME/.config/riceshine/ascii.txt"
```