"""Controller for scraping company infomation"""
from models import scraping

def get_company_infomation():
    """Function to scrape company information"""
    scraping_robot = scraping.ScrapingRobot()
    # scraping_robot.read_company_list()
    scraping_robot.scrape_company()
    # scraping_robot.write_data()