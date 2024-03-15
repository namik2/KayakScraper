import pyfiglet
from colorama import Fore, Style, init
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

init()

class KayakScraper:
    def __init__(self):
        self.driver = webdriver.Chrome()
        self.language = 'EN'
        self.texts = {
            'EN': {
                'departure_airport': "Select Departure Airport:",
                'arrival_airport': "Select Arrival Airport:",
                'departure_month': "Select Departure Month:",
                'return_month': "Select Return Month:",
                'day': "Day (DD): ",
                'company': "Company: ",
                'price': "Price: ",
                'error_popup': "Popup close error: ",
                'select_language': "Choose interface language:\n1. English\n2. Türkçe"
            },
            'TR': {
                'departure_airport': "Kalkış Havaalanı Seçin:",
                'arrival_airport': "\nVarış Havaalanı Seçin:",
                'departure_month': "\nGidiş Ayı Seçin:",
                'return_month': "\nDönüş Ayı Seçin:",
                'day': "Gidiş Günü (GG): ",
                'company': "Şirket: ",
                'price': "Fiyat: ",
                'error_popup': "Popup kapatma hatası: ",
                'select_language': "Arayüz dili seçin:\n1. English\n2. Türkçe"
            }
        }
        self.airports = {
            1: {"code": "IST", "description": "Istanbul Turkiye"},
            2: {"code": "GYD", "description": "Baku Azerbaijan"},
            3: {"code": "FRA", "description": "Frankfurt Germany"},
            4: {"code": "FCO", "description": "Roma Italy"},
            5: {"code": "LON", "description": "London England, United Kingdom"},
            6: {"code": "MOW", "description": "Moscow Russia"},
        }
        self.months = {
            1: "January",
            2: "February",
            3: "March",
            4: "April",
            5: "May",
            6: "June",
            7: "July",
            8: "August",
            9: "September",
            10: "October",
            11: "November",
            12: "December"
        }

    def choose_language(self):
        print(self.texts['EN']['select_language'])
        choice = int(input("Selection: "))
        if choice == 2:
            self.language = 'TR'
            self.months = {
                1: "Ocak",
                2: "Şubat",
                3: "Mart",
                4: "Nisan",
                5: "Mayıs",
                6: "Haziran",
                7: "Temmuz",
                8: "Ağustos",
                9: "Eylül",
                10: "Ekim",
                11: "Kasım",
                12: "Aralık"
            }
        
            
            self.base_url = 'https://www.kayak.com.tr'
        else:
            self.base_url = 'https://www.kayak.com'


    def get_user_input(self):
        print(self.texts[self.language]['departure_airport'])
        for key, value in self.airports.items():
            print(f"{key}. {value['code']} - {value['description']}")
        from_selection = int(input("Selection: "))
        self.from_location = self.airports[from_selection]['code']
        
        print( Fore.GREEN + '====================' + Style.RESET_ALL)

        print(self.texts[self.language]['arrival_airport'])
        for key, value in self.airports.items():
            print(f"{key}. {value['code']} - {value['description']}")
        to_selection = int(input("Selection: "))
        self.to_location = self.airports[to_selection]['code']

        print( Fore.GREEN + '====================' + Style.RESET_ALL)

        print(self.texts[self.language]['departure_month'])
        self.display_months_in_table()
        start_month_selection = int(input("Selection: "))
        self.start_month = "{:02d}".format(start_month_selection)
        self.start_day = input(self.texts[self.language]['day'])

        print( Fore.GREEN + '====================' + Style.RESET_ALL)


        print(self.texts[self.language]['return_month'])
        self.display_months_in_table()
        end_month_selection = int(input("Selection: "))
        self.end_month = "{:02d}".format(end_month_selection)
        self.end_day = input(self.texts[self.language]['day'])
        self.year = "2024"

        print( Fore.GREEN + '====================' + Style.RESET_ALL)

    def display_months_in_table(self):
        month_items = list(self.months.items())
        for i in range(0, len(month_items), 3): 
            print(" | ".join(f"{key}. {value}" for key, value in month_items[i:i+3]))



    def build_url(self):
        self.url = f'{self.base_url}/flights/{self.from_location}-{self.to_location}/{self.year}-{self.start_month}-{self.start_day}/{self.year}-{self.end_month}-{self.end_day}?fs=stops=~0&sort=bestflight_a'



    def open_browser(self):
        self.driver.get(self.url)



    def close_popup(self):
        try:
            pop_window_xpath = '//*[@id="portal-container"]/div/div[2]/div/div/div[3]/div/div[1]/button[1]/div'
            pop_window = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, pop_window_xpath)))
            pop_window.click()
        except Exception as e:
            print(f"{self.texts[self.language]['error_popup']}{e}")



    def scrape_flight_data(self):
        flight_rows = WebDriverWait(self.driver, 10).until(EC.presence_of_all_elements_located((By.XPATH, '//div[@class="nrc6-content-section"]')))
        lst_prices = []
        lst_company_names = []



        for index, element in enumerate(flight_rows):
            try:
                price_script = f"return document.querySelectorAll('div.f8F1-price-text')[{index}].innerText;"
                price = self.driver.execute_script(price_script)
                price = f"\033[91m{price}\033[0m"
            except Exception as e:
                price = "\033[91mN/A\033[0m"  
            lst_prices.append(price)

            elementHTML = element.get_attribute('outerHTML')
            elementSoup = BeautifulSoup(elementHTML, 'html.parser')

            if self.language == 'EN':
                company_names_element = elementSoup.select_one(".c_cgF.c_cgF-mod-variant-default")
            else:
                company_names_element = elementSoup.select_one(".J0g6-operator-text")

            company_names = company_names_element.text.strip() if company_names_element else "N/A"
            lst_company_names.append(company_names)

        if len(lst_prices) == len(lst_company_names):
                for i in range(len(lst_prices)):
                    print(f"{i+1}. {self.texts[self.language]['company']}: {lst_company_names[i]}, {self.texts[self.language]['price']}: {lst_prices[i]}")
        else:
            print("Error: Lists have different lengths.")




    def close_browser(self):
        self.driver.quit()

if __name__ == "__main__":
    ascii_art = pyfiglet.figlet_format("github - namik2", font="slant")
    print(Fore.RED + ascii_art + Style.RESET_ALL)
    scraper = KayakScraper()
    scraper.choose_language()
    scraper.get_user_input()
    scraper.build_url()
    scraper.open_browser()
    scraper.close_popup()
    scraper.scrape_flight_data()
    scraper.close_browser()
