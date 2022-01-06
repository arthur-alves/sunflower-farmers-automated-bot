"""SUNFLOWER FARMERS BOT."""
import os
import time

from selenium import webdriver, common

from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

from logger import log
from settings import settings, plants_type


log('[STARTING SUNFLOWER FARMERS AUTOMATED BOT...] \n')
OPTIONS = webdriver.ChromeOptions()
OPTIONS.add_argument("--disable-blink-features=AutomationControlled")
OPTIONS.add_extension("MetaMask.crx")
OPTIONS.add_argument("--disable-gpu")
OPTIONS.add_argument("--disable-software-rasterizer")

S = Service(ChromeDriverManager().install())
DRIVER = webdriver.Chrome(service=S, options=OPTIONS)
GLOBAL_SLEEP = settings['time_monitor']
SELECTED_PLANT = settings['selected_plant']
MAX_WAIT_TIME = settings['max_wait_time']

# ACC VARIABLES
PHRASE = ''
PASSWD = ''

# CHECK multi_acc_list option in config.yaml
MULTI_ACC_TOTAL = 0
MULTI_ACC_CURRENT = 0


def start_game():
    """Starting the game process."""
    log('\nCleaning unused tabs...')
    close_unused_tabs()
    log('Log in to MetaMask...')
    login_metamask()
    log('Installing Polygon Network...')
    install_polygon_network()
    log('Starting the game...')
    tries = 0
    DRIVER.get('https://sunflower-farmers.com/play/')
    time.sleep(3)
    xpath('//*[@id="welcome"]/div[1]').click()
    main_window_handle = None
    while not main_window_handle:
        main_window_handle = DRIVER.current_window_handle
    signin_window_handle = None
    while not signin_window_handle:
        for handle in DRIVER.window_handles:
            if handle != main_window_handle:
                signin_window_handle = handle
                break
    DRIVER.switch_to.window(signin_window_handle)
    xpath('//*[@id="app-content"]/div/div[2]/div/div[2]/div[4]/div[2]/button[2]').click()
    time.sleep(1)
    xpath('//*[@id="app-content"]/div/div[2]/div/div[2]/div[2]/div[2]/footer/button[2]').click()
    DRIVER.switch_to.window(main_window_handle)
    while is_loading():
        if tries >= MAX_WAIT_TIME:
            log('Max tries to open the game, please try again some time later.')
            raise ValueError('[Application closed]')
        tries += 1
        time.sleep(1)

    log('Select Item to plant...')
    select_basket()
    time.sleep(3)
    if not settings['use_multi_acc']:
        while True:
            in_game_process()
            time.sleep(GLOBAL_SLEEP * 60)
    else:
        in_game_process()


def in_game_process():
    """Main loop process."""
    progress_plants = count_progress_plants()
    log('Harvest in progress ---------- Total: [%s]' % progress_plants)
    log('Checking empty places...')
    if progress_plants == total_harvest_able():
        log('Maximum capacity reached. No places to plant.', 'red')
        log('So ok...')
        if not settings['use_multi_acc']:
            log('Checking again in %s minutes...' % GLOBAL_SLEEP)
            log('No Worries. You can change it on config.yaml!')
        else:
            log('Switching to next account...', 'yellow')
        log('☕ Take some coffee and fresh air...')
        return None

    log('Checking collectables items...', 'white')
    collect_plant()
    time.sleep(1)
    log('Places available to plant: %s.' % plant_seed(), 'white')
    time.sleep(1)
    log('Planting selected Seed...', 'white')
    plant_seed()
    time.sleep(1)
    log('Saving...', 'white')
    save()
    while is_saving():
        time.sleep(3)
    log('Saved!')


def count_free_slots():
    """Count Free slots to plant."""
    log('Counting free slots...', 'yellow')
    return len(css('.plant-hint'))


def plant_seed():
    """Plant selected vegetable."""
    log('Planting...', 'white')
    to_plant = css('.plant-hint')
    for place in to_plant:
        js_click(place)
        time.sleep(0.5)
    log('[DONE]')


def total_harvest_able():
    """Total harvest capacity."""
    return len(css('.harvest'))


def collect_plant():
    """Check collectible plant."""
    all_collectible = css('.harvest')
    log('Places founded: %s. \nCollecting...' % len(all_collectible), 'white')
    for idx, collect in enumerate(all_collectible):
        js_click(collect)
        time.sleep(0.5)


def save():
    """Save harvest."""
    save_btn = xpath('//*[@id="timer"]/img')
    js_click(save_btn)
    js_click(xpath('//*[@id="save-error-buttons"]/div'))
    main_window_handle = None
    while not main_window_handle:
        main_window_handle = DRIVER.current_window_handle
    signin_window_handle = None
    while not signin_window_handle:
        for handle in DRIVER.window_handles:
            if handle != main_window_handle:
                signin_window_handle = handle
                break
    DRIVER.switch_to.window(signin_window_handle)
    metamask_btn = xpath('//*[@id="app-content"]/div/div[2]/div/div[4]/div[3]/footer/button[2]')
    metamask_btn.click()
    DRIVER.switch_to.window(main_window_handle)


def select_basket():
    """Select fruit on basket."""
    js_click(xpath('//*[@id="basket"]/img[2]'))
    time.sleep(2)
    js_click(xpath(plants_type[SELECTED_PLANT]))
    time.sleep(2)
    js_click(xpath('/html/body/div[3]/div/div/div/div/div/div/img'))
    time.sleep(2)


def count_progress_plants():
    """Count all plants in progress."""
    progress_plants = css('span.progress-text')
    for idx, plant in enumerate(progress_plants):
        log('Plants slot %s: %s left.' % (idx + 1, plant.text), 'white')
    return len(progress_plants)


def close_unused_tabs():
    """Close initial metamask plugin tab."""
    main_window_handle = None
    while not main_window_handle:
        main_window_handle = DRIVER.current_window_handle

    for handle in DRIVER.window_handles:
        if handle != main_window_handle:
            DRIVER.switch_to.window(handle)
            DRIVER.close()
            break
    DRIVER.switch_to.window(main_window_handle)


def is_loading():
    """Show Sunflower farmers loading modal."""
    try:
        return 'loading' in xpath('//*[@id="welcome"]/h1', False).text.lower()
    except:
        return None


def is_saving():
    """Check if is saving your farm."""
    try:
        return 'saving' in xpath('//*[@id="saving"]/h4').text.lower()
    except:
        return None


def js_click(element):
    """Execute a JS click on browser."""
    DRIVER.execute_script("arguments[0].click();", element)


def xpath(path, raise_error=True):
    """Find by xpath."""
    found_element = False
    tries = 5
    while not found_element and tries > 0:
        try:
            found_element = DRIVER.find_element(By.XPATH, path)
            return found_element
        except common.exceptions.NoSuchElementException:
            tries -= 1
            time.sleep(1)
    if not raise_error:
        return None
    raise ValueError('Element Not found, Max tries reached.')


def css(css_selector, raise_error=True):
    """Find elements by css."""
    found_elements = False
    tries = 5
    while not found_elements and tries > 0:
        try:
            found_elements = DRIVER.find_elements(By.CSS_SELECTOR, css_selector)
            return found_elements
        except common.exceptions.NoSuchElementException:
            tries -= 1
            time.sleep(1)
    if not raise_error:
        return None
    raise ValueError('Element Not found, Max tries reached.')


def login_metamask():
    """Start login into metamask, see config.yaml for more infor."""
    time.sleep(3)
    DRIVER.get('chrome-extension://nkbihfbeogaeaoehlefnkodbefgpgknn/home.html#initialize/create-password/import-with-seed-phrase')
    secret_xpath = '//*[@id="app-content"]/div/div[2]/div/div/form/div[4]/div[1]/div/input'
    secret_element = xpath(secret_xpath)
    secret_element.send_keys(PHRASE)
    passwd_field = xpath('//*[@id="password"]')
    confirm_passwd_field = xpath('//*[@id="confirm-password"]')
    passwd_field.send_keys(PASSWD)
    confirm_passwd_field.send_keys(PASSWD)
    xpath('//*[@id="app-content"]/div/div[2]/div/div/form/div[7]/div').click()
    xpath('//*[@id="app-content"]/div/div[2]/div/div/form/button').click()
    xpath('//*[@id="app-content"]/div/div[2]/div/div/button').click()
    xpath('//*[@id="popover-content"]/div/div/section/header/div/button', False).click()


def install_polygon_network():
    """Instaling Polygon network on Metamask."""
    xpath('/html/body').send_keys(Keys.CONTROL + Keys.HOME)
    xpath('//*[@id="app-content"]/div/div[1]/div/div[2]/div[1]/div/span').click()
    xpath('//*[@id="app-content"]/div/div[2]/div/button').click()
    name = 'Polygon'
    rpc_url = 'https://polygon-rpc.com'
    chain_id = '137'
    symbol = 'MATIC'
    block_explorer_url = 'https://polygonscan.com/'
    xpath('//*[@id="app-content"]/div/div[3]/div/div[2]/div[2]/div/div[2]/div/div[2]/div[1]/label/input').send_keys(name)
    xpath('//*[@id="app-content"]/div/div[3]/div/div[2]/div[2]/div/div[2]/div/div[2]/div[2]/label/input').send_keys(rpc_url)
    xpath('//*[@id="app-content"]/div/div[3]/div/div[2]/div[2]/div/div[2]/div/div[2]/div[3]/label/input').send_keys(chain_id)
    xpath('//*[@id="app-content"]/div/div[3]/div/div[2]/div[2]/div/div[2]/div/div[2]/div[4]/label/input').send_keys(symbol)
    xpath('//*[@id="app-content"]/div/div[3]/div/div[2]/div[2]/div/div[2]/div/div[2]/div[5]/label/input').send_keys(block_explorer_url)
    xpath('//*[@id="app-content"]/div/div[3]/div/div[2]/div[2]/div/div[2]/div/div[3]/button[2]').click()


def setup_linux_env():
    """Setup based in os.env variables.

    Please check config.yaml file if this option is activated.
    Usage (config.yaml):
        set_linux_env: true
    """
    if os.name == 'posix':
        global PHRASE
        global PASSWD
        PHRASE = os.environ['SUNFLOWER']
        PASSWD = os.environ['PASSWD']


def setup_single_acc():
    """Setup single Account."""
    global PHRASE
    global PASSWD
    PHRASE = settings['private']['secret_phrase']
    PASSWD = settings['private']['passwd']


def multi_acc_change():
    """Change accounts."""
    login_list = settings['multi_acc_list']
    global MULTI_ACC_TOTAL
    global PHRASE
    global PASSWD
    global MULTI_ACC_CURRENT
    MULTI_ACC_TOTAL = len(login_list)
    selected_acc = login_list[MULTI_ACC_CURRENT]
    PHRASE = selected_acc[0]
    PASSWD = selected_acc[0]
    MULTI_ACC_CURRENT += 1
    if MULTI_ACC_CURRENT < MULTI_ACC_TOTAL:
        MULTI_ACC_CURRENT = 0


def get_new_driver():
    DRIVER.close()
    return webdriver.Chrome(service=S, options=OPTIONS)

def main():
    """Main Process."""
    if not settings['use_multi_acc']:
        log(['SINGLE ACCOUNT MODE SELECTED...'])
        if settings['set_linux_env']:
            setup_linux_env()
        else:
            setup_single_acc()
        start_game()
    else:
        log(['MULTI ACCOUNT MODE SELECTED...'])
        while True:
            multi_acc_change()
            start_game()
            global DRIVER
            DRIVER = get_new_driver()

    time.sleep(3)


if __name__ == '__main__':
    main()
