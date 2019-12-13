""" Main script to sync/save datadog config """
import json
import os

from enum import Enum
from typing import Dict, Callable

import click
from click import Choice
from datadiff import diff as dict_diff

from .datadog_client import DatadogClient

DATADOG_CLIENT = DatadogClient()

CONFIG_DIR = DATADOG_CLIENT.config_dir

ACCEPTABLE_TYPES = ["monitor", "dashboard"]
FILES = [f"{type_}s" for type_ in ACCEPTABLE_TYPES]
PUSH_CONFIG: Dict[str, Callable] = {k: lambda x: x for k in FILES}


class StorageLocation(Enum):
    """ Where the config should be saved to """

    s3 = "s3"
    git = "git"


def push_monitors(config, datadog_client):
    results = []
    for monitor in config:
        to_push = monitor
        monitor_id = to_push["id"]
        del to_push["id"]
        results.append(datadog_client.update_monitor(monitor_id, **to_push))


def push_dashboards(config, datadog_client):
    results = []
    for dashboard in config:
        to_push = dashboard
        dashboard_id = to_push["id"]
        del to_push["id"]  # so we don't send it twice
        del to_push["author_name"]  # doesn't like this
        results.append(datadog_client.update_dashboard(dashboard_id, **to_push))


PUSH_CONFIG["dashboards"] = push_dashboards
PUSH_CONFIG["monitors"] = push_monitors


def push_configs(location: str = "."):
    """ Pushes config objects to Datadog retrieved from a local file"""
    config = get_local_config(location)
    for item_name, config in config.items():
        if not config:
            continue
        click.echo(f"\n🚀 Pushing {item_name} config ... ")
        PUSH_CONFIG[item_name](config=config, datadog_client=DATADOG_CLIENT)


def save_configs(configs: dict, location: str = "."):
    """ Save a successful api response to json"""
    click.echo(f"\n 💾 Saving configs to {location}: ")
    for item_type, api_response in configs.items():
        click.echo(f" - {item_type}")
        with open(f"{location}/{item_type}.json", "wb+") as config_file:
            config_file.write(json.dumps(api_response, indent=2).encode("utf-8"))


def get_all_config():
    dashboard_details = []
    click.echo("\nRetrieving dashboards: ")
    for dashboard in DATADOG_CLIENT.get_dashboards():
        click.echo(f" - {dashboard['title']}")
        dashboard_details.append(DATADOG_CLIENT.get_dashboard_detail(dashboard["id"]))

    return {"monitors": DATADOG_CLIENT.get_monitors(), "dashboards": dashboard_details}


def get_local_config(location: str = "."):
    local_config = {file_: None for file_ in FILES}

    for file_ in FILES:
        try:
            with open(f"{location}/{file_}.json") as json_file:
                local_config[file_] = json.load(json_file)
        except FileNotFoundError:
            click.echo(f"No {file_}.json file - skipping ... ")
            continue
    return local_config


def _save(location):
    click.echo(f"\n🐶 Saving datadog config to {location}... (this might take a while)")
    all_config = get_all_config()
    save_configs(all_config, location)
    click.echo(f"\n✨ All done! ✨")


@click.group()
def main():
    pass


@main.command()
@click.argument("folder", default=CONFIG_DIR)
@click.option("-l", "--location", default=StorageLocation.git.value)
def save(folder, location):
    click.echo(f"---- Datadog -> {location} ---- ")
    if location == StorageLocation.s3.value:
        click.echo("Saving all config to S3 is not yet supported! :( ")
        return
    elif location == StorageLocation.git.value:
        _save(folder)
    else:
        click.echo(f"Unknown storage location: {location}")


@main.command()
@click.argument("folder", default="../config")
def diff(folder):
    click.echo("🐶 Generating diff of Datadog Config from local -> remote ...")
    remote_config = get_all_config()
    try:
        local_config = get_local_config(folder)
    except FileNotFoundError as ex:
        print(f"Missing file - try running `save` first. {ex}")
        return
    result = dict_diff(local_config, remote_config)
    if not result.diffs:
        click.echo("No difference - nothing to do!")
        return
    click.echo(result)


@main.command()
@click.option(
    "-c", "--config", default="", help="Sync a single config file up to Datadog"
)
@click.argument("location", default=CONFIG_DIR)
def sync(config, location):
    if config:
        single_config = get_local_config(location)[config]
        click.echo(f"🚀 Pushing {config} config ... ")
        PUSH_CONFIG[config](single_config, datadog_client=DATADOG_CLIENT)
        return
    if (
        click.prompt(
            "\nAre you sure you wish to sync Datadog config from the files on disk? "
            "This will clobber over any changes someone else has made !!\n",
            type=Choice(["y", "n"]),
        )
        == "y"
    ):
        push_configs(location)
        click.echo(f"✨\n All done! ✨")
    else:
        click.echo("✨\n Not pushing any changes today! ✨")


def save_object(id_, config_dir: str = CONFIG_DIR, type_: str = "dashboard"):
    obj = getattr(DATADOG_CLIENT, f"get_{type_}_detail")(id_)
    if obj.get("errors"):
        click.echo(f"😥 {obj['errors']}: {id_}")
        return
    local_config = get_local_config(config_dir)[f"{type_}s"]
    to_write = []
    overwritten = False
    for existing_obj in local_config:
        if existing_obj["id"] == id_:
            if (
                click.prompt(
                    f"This {type_} already exists in the master file - overwrite? y/n",
                    type=Choice(["y", "n"]),
                )
                == "y"
            ):
                to_write.append(obj)
                overwritten = True
            else:
                continue
        else:
            to_write.append(existing_obj)
    if not overwritten:
        to_write.append(obj)
    config = {f"{type_}s": to_write}
    save_configs(config, config_dir)


def save_dashboard(dashboard_id, config_dir: str = CONFIG_DIR):
    save_object(dashboard_id, config_dir, "dashboard")


def save_monitor(monitor_id, config_dir: str = CONFIG_DIR):
    save_object(monitor_id, config_dir, "monitor")


if __name__ == "__main__":
    main()
