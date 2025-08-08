from invoke import task
import logging
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)

@task
def run_pato_bot(c):
    c.run("python patobot/main.py")

@task
def run_pato_bot_pool(c):
    try:
        with ThreadPoolExecutor(max_workers=18) as executor:
            executor.submit(run_pato_bot, c)

    except KeyboardInterrupt:
        logger.warning("Shutting down...")


if __name__ == '__main__':
    run_pato_bot_pool()
