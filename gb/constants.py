import os
import pathlib

CHECK_FREQUENCY = 60000 * 2
TIME_BEFORE_WINDOW_IS_CLOSED = 60 * 15
USER_AGENTS_FILE = os.path.join(pathlib.Path(__file__).parent.absolute(), "data", "user_agents.txt")
PROXIES_FILE = os.path.join(pathlib.Path(__file__).parent.absolute(), "data", "proxies.txt")
BB_USR_DTLS_FILE = os.path.join(pathlib.Path(__file__).parent.absolute(), "data", "bb_usr_details.json")
CHROME_DRIVER_PATH = os.path.join(pathlib.Path(__file__).parent.absolute(), "data", "chromedriver")
BBB_LOG = "/home/sujithg9/PycharmProjects/BestBuyBot/BB_Bot/bbb.log"
NVIDIA_3060_TI_DETAILS = [
    {
        "name": "NVIDIA RTX 3060 Ti FE",
        "link": "https://www.bestbuy.com/site/nvidia-geforce-rtx-3060-ti-"
                "8gb-gddr6-pci-express-4-0-graphics-card-steel-and-black/6439402.p?skuId=6439402"},
    {
        "name": "ASUS TUF RTX 3060 Ti",
        "link": "https://www.bestbuy.com/site/asus-tuf-rtx3060ti-"
                "8gb-gddr6-pci-express-4-0-graphics-card/6452573.p?skuId=6452573",
    },
    {
        "name": "EVGA NVIDIA RTX 3060 Ti",
        "link": "https://www.bestbuy.com/site/evga-nvidia-geforce-rtx-3060-ti-"
                "ftw3-gaming-8gb-gddr6-pci-express-4-0-graphics-card/6444444.p?skuId=6444444",
    }
]
TEST_DATA = [
    {
        "name": "Corsair Dominator Platinum RGB 16GB",
        "link": "https://www.bestbuy.com/site/corsair-dominator-platinum-rgb-16gb-2x8gb-3-6-ghz-ddr4-"
                "c18-desktop-memory-kit-amd-optimized/6450423.p?skuId=6450423",
    }
]
