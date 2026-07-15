import logging

from tracking.tracker import Tracker


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)


def main() -> None:
    tracker = Tracker()
    tracker.run()


if __name__ == "__main__":
    main()
