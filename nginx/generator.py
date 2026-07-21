import os 
from string import Template 
import yaml
import sys
import shutil

# для докера 

CONFIG_PATH = "/app/config/sites.yaml"
NGINX_TEMPLATE = "/etc/nginx/templates/nginx.conf.template"
HTML_TEMPLATE = "/etc/nginx/templates/index.html.template"
NGINX_CONF_DIR = "/etc/nginx/conf.d"
HTML_PATH = "/var/www"

# для тестов на себе

# CONFIG_PATH = "../config/sites.yaml"
# NGINX_TEMPLATE = "templates/nginx.conf.template"
# HTML_TEMPLATE = "templates/index.html.template"
# NGINX_CONF_DIR = "/etc/nginx/conf.d"
# HTML_PATH = "/var/www"

def error_exit(message):
    sys.stderr.write(f'Error: {message}\n')
    sys.exit(1)


def check_path():
    if not os.path.exists(CONFIG_PATH):
        error_exit(f"{CONFIG_PATH} не найден")
    if not os.path.exists(NGINX_TEMPLATE):
        error_exit(f"{NGINX_TEMPLATE} не найден")
    if not os.path.exists(HTML_TEMPLATE):
        error_exit(f"{HTML_TEMPLATE} не найден")
    if not os.path.exists(NGINX_CONF_DIR):
        error_exit(f"{NGINX_CONF_DIR} не найден")

def check_valid(sites):
    for site in sites['sites']:

        required_fields = ['name', 'port', 'root']

        for field in required_fields:
            if not site.get(field):
                error_exit(
                    f"Пустое поле {field} в {CONFIG_PATH}"
                )

        
def read_files():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        sites_data = yaml.safe_load(f)

    with open(NGINX_TEMPLATE, "r", encoding="utf-8") as f:
        nginx_tmpl_obj = Template(f.read())
    with open(HTML_TEMPLATE, "r", encoding="utf-8") as f:
        html_tmpl_obj = Template(f.read())

    return sites_data, nginx_tmpl_obj, html_tmpl_obj


def generate_files_nginx(sites, nginx_template, html_template):
    for site in sites['sites']:
        
        nginx_conf = nginx_template.safe_substitute( # юзаем safe_substitute чтобы не падать в ошибку от '$uri'
            port=site.get('port'), # .get() чтобы не упасть в KeyError
            name=site.get('name'),
            root_dir=site.get('root')
        )

        nginx_conf_path = os.path.join(NGINX_CONF_DIR,f"{site.get('name')}.conf")

        write_config(
            nginx_conf_path,
            nginx_conf,
        )

        generate_html(
            site,
            html_template
        )


def generate_html(site, html_template):

    html_content = html_template.safe_substitute(
        name=site.get('name'),
        port=site.get('port'),
        content=site.get('content', '')
    )

    root_dir = site.get('root')

    os.makedirs(
        root_dir,
        exist_ok=True
    )

    html_path = os.path.join(
        site.get('root'),
        "index.html"
    )

    write_config(
        html_path,
        html_content,
    )
    print("=" * 50)


def write_config(path, content):
    # Проверяем существование файла
    file_exists = os.path.exists(path)

    if file_exists:
        with open(path, "r", encoding="utf-8") as f:
            old_content = f.read()

        if old_content == content:
            print(f"Без изменений: {path}")
            return


    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

    filename = os.path.basename(path)

    if file_exists:
        print(f"Обновлен: {path}")
    else:
        print(f"Создан: {path}")


def delete_unused_configs(sites):
    needed_configs = {
        f"{site['name']}.conf"
        for site in sites['sites']
    }

    existing_configs = {
        file for file in os.listdir(NGINX_CONF_DIR)
        if file.endswith(".conf") and file != "default.conf"
    }

    unused_configs = existing_configs - needed_configs

    # deleted_configs = []

    for file in unused_configs:
        path = os.path.join(NGINX_CONF_DIR, file)
        os.remove(path)

        # deleted_configs.append(file)

        print(f"Удален: {path}")
    
    print("=" * 50)
    print()


def delete_unused_html(sites):
    needed_dirs = {(site["root"]) for site in sites['sites']}
    
    existing_dirs = {
        os.path.join(HTML_PATH, directory)
        for directory in os.listdir(HTML_PATH)
        if os.path.isdir(os.path.join(HTML_PATH, directory))
        }

    unused_dirs = existing_dirs - needed_dirs

    for directory in unused_dirs:
        shutil.rmtree(directory)

        print(f"Удален: {directory}")
    
    print("=" * 50)
    print()


def main():
    check_path()

    sites, nginx_template, html_template = read_files()

    check_valid(sites)

    delete_unused_configs(sites) 

    generate_files_nginx(
        sites,
        nginx_template,
        html_template,
    )


# main()
sites, nginx_template, html_template = read_files()
delete_unused_html(sites)