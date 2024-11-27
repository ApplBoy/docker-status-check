#!/usr/bin/env python3
import subprocess
import time
import requests
import os
import json

# Refactored code from bash
# To be simpler
# Don't be afraid to change the code bellow the config warning/section


################################################################################
#                    ALL YOU NEED TO DO IS DOWN FROM HERE                      #
################################################################################


### CONFIGURATION ###
# Declare them as environment variables or hardcode them here
class CONFIG:

    # Discord
    DISCORD_WEBHOOK_URL = os.environ.get(
        "DISCORD_WEBHOOK_URL",
        "",
    )
    DISCORD_BOT_USERNAME = os.environ.get(
        "DISCORD_BOT_USERNAME", "Docker Status Monitor"
    )

    # Docker
    DOCKER_BIN = os.environ.get("DOCKER_BIN", "docker")
    # Obs: If you let partialy named, it'll ignore all containers with the substring you provided
    # It'll try to find the container by name, if it doesn't find, it'll try to find by ID
    IGNORED_CONTAINERS = [
        item
        for item in os.environ.get("IGNORED_CONTAINERS", "").split("," or "\n")
        if item.strip()
    ]

    # Monitor
    REFRESH_INTERVAL = os.environ.get("REFRESH_INTERVAL", 2)
    LANG = os.environ.get("LANG", "en")
    DETACHED_MODE = False
    QUIET_MODE = False

    def __setattr__(self, name, value):
        raise AttributeError("Cannot modify configuration values at runtime.")


### LANGUAGE STRINGS ###
# You can change the strings by language here
class LANG_STRINGS:
    # This is the only exception, for this class
    def SEND_TO_DISCORD(container_name, image, status):

        yellow = 16776960
        red = 15158332
        blue = 3447003

        if (
            status.startswith("Exited")
            or status.startswith("Created")
            or status.startswith("Stopping")
        ):
            return [
                blue,
                LANG_STRINGS.WARNING_CONTAINER_EXIT_WITH_STOPPED_STATUS(
                    container_name, image, status
                ),
            ]
        elif status.startswith("Error"):
            return [
                red,
                LANG_STRINGS.WARNING_CONTAINER_EXIT_WITH_ERROR_STATUS(
                    container_name, image, status
                ),
            ]
        else:
            return [
                yellow,
                LANG_STRINGS.WARNING_CONTAINER_EXIT(container_name, image, status),
            ]

    def STARTUP_MESSAGE():
        if CONFIG.LANG.startswith("fr"):
            return "Langue détectée: \033[3mFrançais\033[0m\nVeuillez configurer les paramètres de votre webhook Discord.\nPour obtenir de l'aide, consultez le fichier README.md.\nPour quitter, appuyez sur CTRL+C.\n\n"
        elif CONFIG.LANG.startswith("pt"):
            return "Língua detectada: \033[3mPortuguês\033[0m\nPor favor, configure os parâmetros do seu webhook do Discord.\nPara obter ajuda, consulte o arquivo README.md.\nPara sair, pressione CTRL+C.\n\n"
        else:
            return "Language detected: \033[3mEnglish\033[0m\nPlease configure your Discord webhook settings.\nFor help, see the README.md file.\nTo quit, press CTRL+C.\n\n"

    def WARNING_CONTAINER_EXIT_WITH_STOPPED_STATUS(container_name, image, status):
        if CONFIG.LANG.startswith("fr"):
            return f":warning:\n - CONTENEUR **`{container_name}`**\n - AVEC IMAGE `{image}`\n - ARRÊTÉ AVEC LE STATUT `{status}`."
        if CONFIG.LANG.startswith("pt"):
            return f":warning:\n - CONTAINER **`{container_name}`**\n - COM IMAGEM `{image}`\n - PARADO COM STATUS `{status}`."
        else:
            return f":warning:\n - CONTAINER **`{container_name}`**\n - WITH IMAGE `{image}`\n - STOPPED WITH STATUS `{status}`."

    def WARNING_CONTAINER_EXIT_WITH_ERROR_STATUS(container_name, image, status):
        if CONFIG.LANG.startswith("fr"):
            return f":x: :x: :x: :x: :x:\n - CONTENEUR **`{container_name}`**\n - AVEC IMAGE `{image}`\n - ARRÊTÉ AVEC LE STATUT `{status}`.\n:x: :x: :x: :x: :x:"
        if CONFIG.LANG.startswith("pt"):
            return f":x: :x: :x: :x: :x:\n - CONTAINER **`{container_name}`**\n - COM IMAGEM `{image}`\n - PARADO COM STATUS `{status}`.\n:x: :x: :x: :x: :x:"
        else:
            return f":x: :x: :x: :x: :x:\n - CONTAINER **`{container_name}`**\n - WITH IMAGE `{image}`\n - STOPPED WITH STATUS `{status}`.\n:x: :x: :x: :x: :x:"

    def WARNING_CONTAINER_EXIT(container_name, image, status):
        if CONFIG.LANG.startswith("fr"):
            return f":warning:\n - CONTENEUR **`{container_name}`**\n - AVEC IMAGE `{image}`\n - ARRÊTÉ AVEC LE STATUT `{status}`."
        if CONFIG.LANG.startswith("pt"):
            return f":warning:\n - CONTAINER **`{container_name}`**\n - COM IMAGEM `{image}`\n - PARADO COM STATUS `{status}`."
        else:
            return f":warning:\n - CONTAINER **`{container_name}`**\n - WITH IMAGE `{image}`\n - STOPPED WITH STATUS `{status}`."

    def ERROR_SENDING_DISCORD(status_code, response_text):
        if CONFIG.LANG.startswith("fr"):
            return f"Échec de l'envoi de la notification Discord: {status_code}, {response_text}"
        elif CONFIG.LANG.startswith("pt"):
            return (
                f"Falha ao enviar notificação Discord: {status_code}, {response_text}"
            )
        else:
            return (
                f"Failed to send Discord notification: {status_code}, {response_text}"
            )

    def CONTAINER_RESTARTED(container_id):
        if CONFIG.LANG.startswith("fr"):
            return f"Conteneur {container_id} redémarré, retrait de la liste de surveillance"
        elif CONFIG.LANG.startswith("pt"):
            return (
                f"Contêiner {container_id} reiniciado, removendo da lista monitorada."
            )
        else:
            return f"Container {container_id} restarted, removing from monitored list."

    def CONTAINER_NO_LONGER_EXISTS(container_id):
        if CONFIG.LANG.startswith("fr"):
            return f"Conteneur {container_id} n'existe plus, retrait de la liste de surveillance."
        elif CONFIG.LANG.startswith("pt"):
            return f"Contêiner {container_id} não existe mais, removendo da lista monitorada."
        else:
            return f"Container {container_id} no longer exists, removing from monitored list."

    def CONTAINER_STOPPED(container_id, name, image, status):
        if CONFIG.LANG.startswith("fr"):
            return f"Conteneur {name} arrêté avec statut {status}"
        elif CONFIG.LANG.startswith("pt"):
            return f"Contêiner {name} parado com status {status}"
        else:
            return f"Container {name} stopped with status {status}"

    def MAYBE_ITS_AN_ID(container_id):
        if CONFIG.LANG.startswith("fr"):
            return f"Peut-être que {container_id} est un ID de conteneur"
        elif CONFIG.LANG.startswith("pt"):
            return f"Talvez {container_id} seja um ID de contêiner"
        else:
            return f"Maybe {container_id} is a container ID"

    def NO_WEBHOOK_PROVIDED():
        if CONFIG.LANG.startswith("fr"):
            return "Aucun webhook Discord fourni."
        elif CONFIG.LANG.startswith("pt"):
            return "Nenhum webhook do Discord fornecido."
        else:
            return "No Discord webhook provided."

    def GET_PID(pid):
        if CONFIG.LANG.startswith("fr"):
            return f"Le PID du processus est {pid}"
        elif CONFIG.LANG.startswith("pt"):
            return f"O PID do processo é {pid}"
        else:
            return f"The process PID is {pid}"

    def __setattr__(self, name, value):
        raise AttributeError("Cannot modify language strings at runtime.")


################################################################################
#                    ALL YOU NEED TO DO IS UP FROM HERE                        #
################################################################################


def print_error(message):
    print(f"\033[91m{message}\033[0m")


def print_log(message):
    print(message)


def print_startup():
    print_log(LANG_STRINGS.STARTUP_MESSAGE())


def shell_run(command):
    if (
        command is None
        or command == ""
        or command.isspace()
        or type(command) is not str
    ):
        return "NO_COMMAND_PROVIDED"

    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.stdout.strip()
    except Exception as e:
        return {e}


def send_to_discord(container_name, image, status, logs):
    [color, text] = LANG_STRINGS.SEND_TO_DISCORD(container_name, image, status)

    # Prepare the payload
    payload = {
        "username": f"{CONFIG.DISCORD_BOT_USERNAME}",
        "embeds": [
            {
                "description": text,
                "title": "Docker Status Error",
                "color": color,
            }
        ],
    }

    payload_json = json.dumps(payload)
    files = {"file": ("logs.log", logs)}

    try:
        response = requests.post(
            CONFIG.DISCORD_WEBHOOK_URL,
            data={"payload_json": payload_json},
            files=files,
        )

        if response.status_code != 200:
            print_error(
                LANG_STRINGS.ERROR_SENDING_DISCORD(response.status_code, response.text)
            )
    except Exception as e:
        print_error(LANG_STRINGS.ERROR_SENDING_DISCORD("N/A", e))
        exit(1)


def find_container_id(container_name):
    results = shell_run(
        f"{CONFIG.DOCKER_BIN} ps -a -q -f name={container_name}",
    )

    if results == "":
        print_log(LANG_STRINGS.MAYBE_ITS_AN_ID(container_name))
        return shell_run(
            f"{CONFIG.DOCKER_BIN} ps -a -q --format id={container_name}",
        )
    return results


ignored_ids = set()
stopped_ids = set()


def monitor_docker():
    while True:
        running_ids = set(shell_run(f"{CONFIG.DOCKER_BIN} ps -q").splitlines())
        all_ids = set(shell_run(f"{CONFIG.DOCKER_BIN} ps -aq").splitlines())

        if any(
            x and isinstance(x, str) and x.startswith("Error")
            for x in [running_ids, all_ids]
        ):
            print_error(x)
            time.sleep(CONFIG.REFRESH_INTERVAL * 2)
            continue

        stopped_ids = all_ids - running_ids

        for container_id in stopped_ids:
            if container_id in ignored_ids or container_id not in stopped_ids:
                continue

            name = shell_run(
                f"{CONFIG.DOCKER_BIN} ps -a --format '{{{{.Names}}}}' -f id={container_id}",
            )

            image = shell_run(
                f"{CONFIG.DOCKER_BIN} ps -a --format '{{{{.Image}}}}' -f id={container_id}",
            )

            status = shell_run(
                f"{CONFIG.DOCKER_BIN} ps -a --format '{{{{.Status}}}}' -f id={container_id}",
            )

            logs = shell_run(
                f"{CONFIG.DOCKER_BIN} logs {container_id} 2>&1 | tail -n 1000",
            )

            if any(
                x and isinstance(x, str) and x.startswith("Error")
                for x in [name, image, status, logs]
            ):
                print_error(x)
                break

            print_log(LANG_STRINGS.CONTAINER_STOPPED(container_id, name, image, status))

            send_to_discord(name, image, status, logs)

            ignored_ids.add(container_id)

        # Handle restarted containers
        for container_id in stopped_ids.copy():
            if container_id in running_ids and container_id in ignored_ids:
                print_log(LANG_STRINGS.CONTAINER_RESTARTED(container_id))
                ignored_ids.remove(container_id)

        for container_id in ignored_ids.copy():
            if container_id not in all_ids.copy():
                print_log(LANG_STRINGS.CONTAINER_NO_LONGER_EXISTS(container_id))
                ignored_ids.remove(container_id)

        time.sleep(CONFIG.REFRESH_INTERVAL)


if __name__ == "__main__":

    if CONFIG.DETACHED_MODE:
        if os.fork():
            exit(0)
        print(LANG_STRINGS.GET_PID(os.getpid()))

    if CONFIG.QUIET_MODE:

        def print_log(message):
            pass

    print_startup()
    if not CONFIG.DISCORD_WEBHOOK_URL:
        print_error(LANG_STRINGS.NO_WEBHOOK_PROVIDED())
        exit(1)

    ignored_ids = set(
        find_container_id(container) for container in CONFIG.IGNORED_CONTAINERS
    )

    monitor_docker()
