"""Defined a robot model"""
from models import handling

class Robot(object):
    """Base model for Robot."""
    def __init__(self,speak_color='green'):
        self.speak_color = speak_color

class ScrapingRobot(Robot):
    """Scrape company information"""

    def read_company_list(self):
        print('read_company_list')
    
    def scrape_company(self):
        print('scrape_company')

    def write_data(self):
        print('write_data')