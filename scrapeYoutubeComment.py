
import os
import logging
import pandas as pd
from typing import Optional, List, Tuple
from datetime import date
import time
from selenium.webdriver import Edge
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

class YoutubeVideo:
    
    def __init__(self, video_title: str, video_url: str, channel: str, release_date: str, tags: Optional[str] = None):
        self.video_title = video_title
        self.video_url = video_url
        self.channel = channel
        self.release_date = release_date
        self.tags = tags
        
class YoutubeComment:
    
    def __init__(self, comment_text: str, time_elapsed_since_comment: str, author: str, time_of_collection: str, from_video: str, tags: Optional[str] = None) -> None:
        self.comment_text = comment_text
        self.time_elapsed_since_comment = time_elapsed_since_comment
        self.author = author
        self.time_of_collection = time_of_collection
        self.from_video = from_video
        self.tags = tags

class YoutubeCommentScraper:

    def __init__(self, edge_driver_path: str, video_title: str, video_url: str, tags: Optional[str] = None, ) -> None:
        
        self.edge_driver_path = edge_driver_path
        self.video_title = video_title
        self.video_url = video_url
        self.tags = tags
        self.scraped_youtube_comments: List[YoutubeComment] = []
        self.count_of_total_comments: int = 0

    def scrape_comments(self, number_of_comments_to_scrape: int, scrape_method: str = 'simple', scrape_replies: bool = False) -> None:
        
        time_of_collection: str = date.today().strftime('%Y-%m-%d')
        current_height: int = 0
        
        scroll_end_times = int
        
        if len(self.scraped_youtube_comments) > 0:
            
            logging.info('You must clear comments before you can scrape comments')
            
            return

        with Edge(executable_path=self.edge_driver_path) as driver:
            
            driver.get(self.video_url)
            
            while True:
                try:
                    count_of_all_youtube_comments_element = WebDriverWait(driver, 1).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "#count > yt-formatted-string > span:nth-child(1)"))
                    )
                    break
                except:
                    pass
                
                self._scroll_down(driver, 0.5)
                
            self.count_of_total_comments = int(count_of_all_youtube_comments_element.text.replace(',', ''))
            
            scroll_end_times = self._get_scroll_end_times(self.count_of_total_comments, number_of_comments_to_scrape)
            
            logging.info(f'Times to scroll end: {scroll_end_times}')
            
            if scrape_method not in ('simple', 'batched', 'expensive'):
                
                logging.info(f'Scrape method does not exist: {scrape_method}')
                
            elif scrape_method == 'simple':
                
                logging.info('Scrape method starts: simple')
                
                scroll_end_count: int = 0
                
                scroll_down_times = int
                
                logging.info('Started scrolling end...')             
                
                for i in range(scroll_end_times):
                
                    self._scroll_end(driver, 3)
                    scroll_end_count += 1
                    
                    new_height: int = driver.execute_script('return document.documentElement.scrollHeight')
                    
                    if new_height <= current_height:
                        
                        logging.info('Scrolling ends due to reaching end...')
                        
                        break
                    
                    current_height = new_height
                    
                logging.info(f'Scroll end count: {scroll_end_count}')
                        
                if scrape_replies:
                    
                    self._click_to_see_replies(driver)
                    self._click_to_see_more_replies(driver)                
                    
                self._click_to_read_more(driver)
                
                if scrape_replies:
                    
                    scroll_down_times = self._get_scroll_down_times(scroll_end_count=scroll_end_count, scroll_down_from_top=True)
                    
                    logging.info('Started scrolling top...')
                    
                    self._scroll_top(driver, 1)
                    
                    logging.info('Started scrolling down...')
                    
                    for i in range(scroll_down_times):
                        
                        self._scroll_down(driver, 1.5)
                        
                logging.info(f'Scroll down times: {scroll_down_times}')
                
                comment_text_list, time_elapsed_since_comment_list, author_list = self._get_comment_data(driver)
                    
            elif scrape_method == 'batched':
                
                logging.info('Scrape method starts: batched')
                
                comment_text_list: List[str] = []
                time_elapsed_since_comment_list: List[str] = []
                author_list: List[str] = []
                
                scroll_end_count: int = 0
                reached_end: bool = False
                
                scroll_up_times = int
    
                batches: int = (scroll_end_times // 80) + 1
                
                for i in range(batches):
                    
                    if reached_end == True:
                        break
                    
                    logging.info('Entered batch...')
                    
                    scroll_end_count_inner_loop: int = 0
                    
                    logging.info('Started scrolling end...')
                    
                    for j in range(80):
                    
                        self._scroll_end(driver, 3)
                        scroll_end_count_inner_loop += 1  
                        
                        new_height: int = driver.execute_script('return document.documentElement.scrollHeight')
                    
                        if new_height <= current_height:
                            
                            logging.info('Scrolling ends due to reaching end...')
                            
                            reached_end = True
                            
                            break
                    
                        current_height = new_height
                        
                    logging.info(f'scroll_end_count_inner_loop: {scroll_end_count_inner_loop}')
                        
                    if scrape_replies:
                        
                        self._click_to_see_replies(driver)
                        self._click_to_see_more_replies(driver)
                        
                    self._click_to_read_more(driver)
                    
                    if scrape_replies:
                        
                        scroll_up_times = self._get_scroll_up_times(scroll_end_count_inner_loop)
                        
                        logging.info('Started scrolling up...')
                        
                        for i in range(scroll_up_times):
                            
                            self._scroll_up(driver, 1.5)
                    
                    batch_comment_text_list, batch_time_elapsed_since_comment_list, batch_author_list = self._get_comment_data(driver)
                     
                    comment_text_list: List[str] = comment_text_list + batch_comment_text_list
                    time_elapsed_since_comment_list: List[str] = time_elapsed_since_comment_list + batch_time_elapsed_since_comment_list
                    author_list: List[str] = author_list + batch_author_list
                    
                    scroll_end_count += scroll_end_count_inner_loop
                    
            elif scrape_method == 'expensive':
                
                logging.info('Scrape method starts: expensive')
                
                comment_text_list: List[str] = []
                time_elapsed_since_comment_list: List[str] = []
                author_list: List[str] = []
                
                scroll_down_times: int = self._get_scroll_down_times(scroll_end_count=scroll_end_times, scroll_down_from_top=False)
                scroll_down_count: int = 0
                scroll_down_count_inner: int
                
                logging.info(f'scroll_down_times: {scroll_down_times}')
                
                unit: int = 200
                flag: int = 1
                aggressive_scrolling_up_buffer: int = 20
                
                while scroll_down_count < scroll_down_times:
                    
                    logging.info('Started scrolling down...')
                    for i in range(unit * flag):                     
                        
                        self._scroll_down(driver, 1)
                    
                    if scrape_replies:
                            
                        self._click_to_see_replies(driver)
                        self._click_to_see_more_replies(driver)
                        
                    self._click_to_read_more(driver)
                    
                    logging.info('Started scrolling up...')
                    for i in range(unit + aggressive_scrolling_up_buffer):                        
                        
                        self._scroll_up(driver, 1.5)
                        
                    batch_comment_text_list, batch_time_elapsed_since_comment_list, batch_author_list = self._get_comment_data(driver)
                     
                    comment_text_list: List[str] = comment_text_list + batch_comment_text_list
                    time_elapsed_since_comment_list: List[str] = time_elapsed_since_comment_list + batch_time_elapsed_since_comment_list
                    author_list: List[str] = author_list + batch_author_list
                    
                    scroll_down_count += unit
                    flag = 2
                    
            comment_text_list, time_elapsed_since_comment_list, author_list = self._remove_duplicates(comment_text_list, time_elapsed_since_comment_list, author_list)
            
            for c, t, a in zip(comment_text_list, time_elapsed_since_comment_list, author_list):
                
                comment = YoutubeComment(c.text, t.text, a.text, time_of_collection, self.video_title, self.tags)
                self.scraped_youtube_comments.append(comment)

    def clear_comments(self) -> None:
        
        self.scraped_youtube_comments: List[YoutubeComment] = []
        self.count_of_total_comments: int = 0
        
    def _get_scroll_end_times(self, count_of_total_comments: int, number_of_comments_to_scrape: int):
        
        return (min(count_of_total_comments, number_of_comments_to_scrape) // 20)
    
    def _get_scroll_down_times(self, scroll_end_count: int, scroll_down_from_top: bool):
        
        if scroll_down_from_top:
            
            return scroll_end_count * 4 + 11
        
        else:
        
            return scroll_end_count * 4
        
    def _get_scroll_up_times(self, scroll_end_count: int):
        
        return scroll_end_count * 4
    
    def _scroll_down(self, driver: Edge, sleep_time: float) -> None:
        
        wait = WebDriverWait(driver, 10)
                
        wait.until(EC.visibility_of_element_located((By.TAG_NAME, "body"))).send_keys(Keys.PAGE_DOWN)
        time.sleep(sleep_time)

    def _scroll_up(self, driver: Edge, sleep_time: float) -> None:
        
        wait = WebDriverWait(driver, 10)
                
        wait.until(EC.visibility_of_element_located((By.TAG_NAME, "body"))).send_keys(Keys.PAGE_UP)
        time.sleep(sleep_time)
        
    def _scroll_top(self, driver: Edge, sleep_time: float) -> None:
        
        wait = WebDriverWait(driver, 10)
                
        wait.until(EC.visibility_of_element_located((By.TAG_NAME, "body"))).send_keys(Keys.HOME)
        time.sleep(sleep_time)
        
    def _scroll_end(self, driver: Edge, sleep_time: float) -> None:
        
        wait = WebDriverWait(driver, 10)
                
        wait.until(EC.visibility_of_element_located((By.TAG_NAME, "body"))).send_keys(Keys.END)
        time.sleep(sleep_time)
        
    def _click_to_see_replies(self, driver: Edge) -> None:
        
        counter: int = 0
        
        for link in driver.find_elements(By.CSS_SELECTOR, '#more-replies > yt-button-shape > button > yt-touch-feedback-shape > div'):
            
            try:
                
                driver.execute_script("arguments[0].click();", link)
                time.sleep(0.5)
                
                counter += 1

            except:
                pass
            
        logging.info(f'click to see replies: {counter}')
            
    def _click_to_see_more_replies(self, driver: Edge) -> None:
        
        counter: int = 0
        
        for link in driver.find_elements(By.CSS_SELECTOR, '#button > ytd-button-renderer > yt-button-shape > button'):

            try:
                
                driver.execute_script("arguments[0].click();", link)
                time.sleep(0.5)
                
                counter += 1

            except:
                pass
            
        logging.info(f'click to see more replies: {counter}')
        
    def _click_to_read_more(self, driver: Edge) -> None:
        
        counter: int = 0
        
        for link in driver.find_elements(By.XPATH, '//*[@id="more"]/span'):
            
            try:
                
                driver.execute_script("arguments[0].click();", link)
                time.sleep(0.5)
                
                counter += 1

            except:
                pass
            
        logging.info(f'click to read more: {counter}')

    def _get_comment_data(self, driver: Edge) -> Tuple[List[str], List[str], List[str]]:
        
        wait = WebDriverWait(driver, 10)
        
        comment_text_list = wait.until(EC.presence_of_all_elements_located((By.XPATH, '//*[@id="content-text"]')))
        time_elapsed_since_comment_list = wait.until(EC.presence_of_all_elements_located((By.XPATH, '//*[@id="header-author"]/yt-formatted-string/a')))
        author_list = wait.until(EC.presence_of_all_elements_located((By.XPATH, '//*[@id="author-text"]')))
        
        number_of_comments_gotten = len(comment_text_list)
        logging.info(f'got comments this time: {number_of_comments_gotten}')
        
        return comment_text_list, time_elapsed_since_comment_list, author_list           
            
    def _remove_duplicates(self, comment_text_list, time_elapsed_since_comment_list, author_list):
        
        unique_c = []
        unique_t = []
        unique_a = []
        seen = set()
        
        for c, t, a in zip(comment_text_list, time_elapsed_since_comment_list, author_list):
            
            if c not in seen:
                unique_c.append(c)
                unique_t.append(t)
                unique_a.append(a)
                seen.add(c)
                
        number_of_duplicates = len(comment_text_list) - len(seen)
                
        logging.info(f'removed duplicates: {number_of_duplicates}')
                
        return unique_c, unique_t, unique_a

def main():

    log_folder = "log_file_folder"
    script_location = os.path.dirname(os.path.abspath(__file__))
    log_folder_path = os.path.join(script_location, log_folder)
    
    # Create the log_folder if it does not exist
    if not os.path.exists(log_folder_path):
        os.makedirs(log_folder_path)
    
    log_file_path = os.path.join(log_folder_path, "scraper_log.log")
    
    logging.basicConfig(filename=log_file_path, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')    
    logging.info('-----------------------  program begins  -----------------------')
    
    youtube_videos_to_scrape = [
        
        # YoutubeVideo('EXP EDITION - Feel Like This', 'https://www.youtube.com/watch?v=R8_fuXncjDo', 'EXP EDITION TV', 'Apr 17, 2017', 'american, croats, german, japanese, mv'),
        # YoutubeVideo('EXP EDITION - FEEL LIKE THIS Korean Reaction!', 'https://www.youtube.com/watch?v=rse0HGWdZ68', 'DKDKTV', 'Apr 28, 2017', 'american, croats, german, japanese, reaction'),
        
        # YoutubeVideo('SB19 - Alab', 'https://www.youtube.com/watch?v=-tWuVqZnoL4', 'SB19 Official', 'Jan 9, 2020', 'filipino, mv'),
        # YoutubeVideo('kpoper reacts to SB19', 'https://www.youtube.com/watch?v=y7sAKBUkCis', 'Kin Ryan', 'May 14, 2020', 'filipino, reaction'),
        
        # YoutubeVideo('KAACHI - Your Turn', 'https://www.youtube.com/watch?v=1NWzao4xf1E', 'KAACHI', 'Apr 29, 2020', 'venezuelans, spanish, filipino, british, mv'),
        # YoutubeVideo('KAACHI MV REACTION - KOREABOO', 'https://www.youtube.com/watch?v=uYmSCuy94Dg', 'Soo-Ah', 'May 2, 2020', 'venezuelans, spanish, filipino, british, reaction'),

        # YoutubeVideo('BLACKSWAN - Tonight', 'https://www.youtube.com/watch?v=25AwKJD8Wwg', 'Blackswan Official', 'Oct 16, 2020', 'senegalese, belgian, brazilian, japanese, mv'),
        # YoutubeVideo('riVerse Reacts Tonight by BLACKSWAN', 'https://www.youtube.com/watch?v=_TOwDW5LKac', 'RiVerse Live', 'Dec 5, 2020', 'senegalese, belgian, brazilian, japanese, reaction'),
        
        # YoutubeVideo('Cherry Bullet - QA', 'https://www.youtube.com/watch?v=5LCGn9UFNAY', '1theK', 'Jan 21, 2019', 'japanese, taiwanese, mv'),
        # YoutubeVideo('Cherry Bullet QA Reaction', 'https://www.youtube.com/watch?v=HB1N745aulQ', 'ReacttotheK', 'Feb 21, 2019', 'japanese, taiwanese, raction'),

        # YoutubeVideo('FANATICS - SUNDAY', 'https://www.youtube.com/watch?v=NC_-T581Dbs', '1theK', 'Aug 6, 2019', 'japanese, chinese, taiwanese, mv'),
        # YoutubeVideo('The Kulture Study FANATICS Sunday MV', 'https://www.youtube.com/watch?v=fgvG8Cr0RGU', 'Form of Therapy', 'Sep 18, 2019', 'japanese, chinese, taiwanese, mv'),

        # YoutubeVideo('wooah - wooah', 'https://www.youtube.com/watch?v=X2FB37r4Oyw', '1theK', 'May 15, 2020', 'japanese, mv'),
        # YoutubeVideo('wooah - wooah MV Reaction', 'https://www.youtube.com/watch?v=QIw1_Ay-4Cc', 'Birb', 'May 16, 2020', 'japanese, reaction'),

        # YoutubeVideo('Bling Bling - G.G.B', 'https://www.youtube.com/watch?v=4fXYybUXKqA', '1theK', 'Nov 17, 2020', 'japanese, mv'),
        YoutubeVideo('REACTION to BLING BLING - G.G.B OFFICIAL MV', 'https://www.youtube.com/watch?v=5urGs58uyo0', 'Kaia: The Safe Cave', 'Nov 18, 2020', 'japanese, raction')

    ]   

    edge_driver_path = r'C:\Program Files\drivers\msedgedriver_114.exe'

    number_of_comments_to_scrape: int = 100
    scrape_method: str = 'simple'
    
    for youtube_video in youtube_videos_to_scrape:
        
        logging.info(f'-----  Scraping for {youtube_video.video_title} starts  -----')
        
        result_list: List[YoutubeComment] = []
        output = pd.DataFrame()
        
        youtube_comment_scraper = YoutubeCommentScraper(edge_driver_path, youtube_video.video_title, youtube_video.video_url, youtube_video.tags)
        youtube_comment_scraper.clear_comments()
        youtube_comment_scraper.scrape_comments(number_of_comments_to_scrape=number_of_comments_to_scrape, scrape_method=scrape_method, scrape_replies=True)
        
        number_of_scrapped_comments: int = len(youtube_comment_scraper.scraped_youtube_comments)
        
        logging.info(f'{youtube_video.video_title} has {youtube_comment_scraper.count_of_total_comments} comments in total')
        logging.info(f'The youtube_comment_scraper scrapped {number_of_scrapped_comments} for {youtube_video.video_title}')
        
        result_list = youtube_comment_scraper.scraped_youtube_comments
        
        logging.info(f'-----  Scraping for {youtube_video.video_title} ends  -----')
    
        data = {
            'comment_text': [c.comment_text for c in result_list],
            'time_elapsed_since_comment': [c.time_elapsed_since_comment for c in result_list],
            'author': [c.author for c in result_list],
            'time_of_collection': [c.time_of_collection for c in result_list],
            'from_video': [c.from_video for c in result_list],
            'tags': [c.tags for c in result_list]
        }
    
        output = pd.DataFrame(data)
        output.to_csv(f'output_{youtube_video.video_title}.csv', encoding='utf-8-sig')

if __name__ == "__main__":
    main()