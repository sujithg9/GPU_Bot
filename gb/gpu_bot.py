#!/usr/bin/env python3
import re
import json
import time
import logging
import logging.config
import numpy as np
import asyncio
import argparse
import functools
import tornado.ioloop
import requests
import multiprocessing
from multiprocessing import Pool
from tornado.platform.asyncio import AnyThreadEventLoopPolicy

import latest_user_agents
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions

from notify_run import Notify

import constants

log = logging.getLogger(__name__)


def get_random_ua_proxy(ua_proxy_file):
    random_ua_proxy = ''
    try:
        with open(ua_proxy_file) as f:
            lines = f.readlines()
        if len(lines):
            prng = np.random.RandomState()
            index = prng.permutation(len(lines) - 1)
            idx = np.asarray(index, dtype=np.integer)[0]
            random_ua_proxy = lines[int(idx)]
    except Exception as ex:
        log.exception(f'Exception in random_ua : {str(ex)}')

    finally:
        return random_ua_proxy.strip()


def get_user_details():
    f = open(constants.BB_USR_DTLS_FILE, )
    usr_data = json.load(f)
    return usr_data


def web_bot(gpu_data):
    options = webdriver.ChromeOptions()
    user_agent = latest_user_agents.get_random_user_agent()  # get_random_ua_proxy(constants.USER_AGENTS_FILE)
    options.add_argument(f'user-agent={user_agent}')
    driver = webdriver.Chrome(chrome_options=options, executable_path=constants.CHROME_DRIVER_PATH)
    driver.get(gpu_data["link"])

    try:
        add_to_cart_button = WebDriverWait(driver, 10).until(
            expected_conditions.element_to_be_clickable((By.CSS_SELECTOR, ".add-to-cart-button"))
        )
        add_to_cart_button.click()
        log.info(f"Product {gpu_data['name']} is added to card using link {gpu_data['link']}")
        time.sleep(constants.TIME_BEFORE_WINDOW_IS_CLOSED)
    except Exception as ex:
        log.exception("Failed to find add to card : %s", str(ex.__str__()))
        driver.close()
    finally:
        driver.close()


def web_scraper(gpu_data):
    source_url = gpu_data["link"]
    available = False
    try:
        headers = {
            'user-agent': latest_user_agents.get_random_user_agent(),  # get_random_ua_proxy(constants.USER_AGENTS_FILE)
        }
        proxies = {
            'http': get_random_ua_proxy(constants.PROXIES_FILE)
        }
        source_page_data = requests.get(source_url, headers=headers, proxies=proxies)
        scrapper = BeautifulSoup(source_page_data.content, 'html.parser')
        if "bestbuy.com" in source_url:
            button_elements = scrapper.find_all('button', attrs={"class", re.compile("add-to-cart-button", re.I)})
            if len(button_elements) > 0:
                for button_element in button_elements:
                    button_attrs = button_element.attrs
                    if button_attrs["data-sku-id"] in source_url and button_attrs["data-button-state"] == "ADD_TO_CART":
                        available = True
        if available:
            log.info(f"GPU - {source_url} is Available. Trying to add the item to the cart in the browser")
            send_push_notifications_android(f"GPU {gpu_data['name']} is available look up under {gpu_data['link']}")
            web_bot(gpu_data)
        else:
            log.info(f"GPU - {source_url} is not Available.")
    except Exception as ex:
        log.exception(f"Failed while Web Scraping Site - {source_url} : {str(ex)}")
    return available


def send_push_notifications_android(message):
    notify = Notify()
    notify.send(message)


def configure_logger():
    logging_config = dict({
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "simple": {'format': '%(asctime)s [%(levelname)s] <%(processName)s:%(process)s> '
                                 '[%(name)s(%(filename)s:%(lineno)d)] - %(message)s',
                       'datefmt': '%Y-%m-%d %H:%M:%S'
                       },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": "INFO",
                "formatter": "simple",
                "stream": "ext://sys.stdout"
            },
            "file_handler": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "INFO",
                "formatter": "simple",
                "filename": constants.BBB_LOG,
                "maxBytes": 100 * pow(1024, 3),
                "backupCount": 1,
                "encoding": "utf8"
            }
        },
        "loggers": {
            "default": {
                "level": "INFO",
                "handlers": ["console", "file_handler"],
                "propagate": False
            }
        },
        "root": {
            "level": "INFO",
            "handlers": ["console", "file_handler"]
        }
    })
    return logging_config


def gpu_hunter(args=None):
    log.info("Looking up for GPUs availability ...")
    gpus_data = constants.NVIDIA_3060_TI_DETAILS if not args.test else constants.TEST_DATA
    pool = Pool(min(len(gpus_data), multiprocessing.cpu_count()))
    result = pool.map(web_scraper, gpus_data)
    if len(gpus_data) == len(result):
        pool.terminate()

    log.info("One or more GPUs are available.") if any(r is True for r in result) \
        else log.info("No GPUs are available, keep trying ...")


def initialize_bbb_lookup_loop(args=None):
    logging.config.dictConfig(configure_logger())
    main_event_loop = tornado.ioloop.IOLoop()
    asyncio.set_event_loop_policy(AnyThreadEventLoopPolicy())
    main_event_loop.make_current()

    lookup_cb = tornado.ioloop.PeriodicCallback(functools.partial(gpu_hunter, args),
                                                constants.CHECK_FREQUENCY)
    log.info("Initializing GPU hunt bot ...")
    lookup_cb.start()
    main_event_loop.start()


def main(argv=None):
    parser = argparse.ArgumentParser(prog="bbb-cli", description="CLI for looking up for GPUs on Bestbuy.")
    subparsers = parser.add_subparsers(help="commands")

    lookup = subparsers.add_parser("lookup", help="BBB Lookup sub-commands for looking up for GPUs")
    lookup_commands = lookup.add_subparsers(help="lookup operations")

    initialize = lookup_commands.add_parser("initialize", help="Initial bbb gpu lookup loop.")
    initialize.add_argument("--test", action="store_true", help="Use a product that is available.")
    initialize.set_defaults(func=initialize_bbb_lookup_loop)

    check = lookup_commands.add_parser("check", help="Check if there are any gpus right now (One-time).")
    check.add_argument("--test", action="store_true", help="Use a product that is available.")
    check.set_defaults(func=gpu_hunter)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == '__main__':
    main()
