import requests
from pprint import  pprint
from bs4 import BeautifulSoup
grouplink = 'https://www.douban.com/group/explore?start={}&tag=%E7%A7%9F%E6%88%BF'
import requests
import sqlite3
import multiprocessing
from tqdm import tqdm
import time
import asyncio
from collections import namedtuple
import aiohttp
burp0_headers = {"Connection": "close", "Upgrade-Insecure-Requests": "1",
                 "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36",
                 "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                 "Sec-Fetch-Site": "none", "Sec-Fetch-Mode": "navigate", "Sec-Fetch-Dest": "document",
                 "Accept-Language": "zh-CN,zh;q=0.9"}


async def async_get_response(url,headers):
    async with aiohttp.ClientSession() as session:
        async with session.get(url,timeout=30,headers=burp0_headers) as response:
            # assert response.status == 200
            # html = await response.read()
            content = await response.text()
            return content
def city_group(city=None):


    group_list = '//*[@id="content"]/div/div[1]/div[1]/div[1]'
    # content > div > div.article > div.group-list > div:nth-child(1)
    results = []
    # pbar = tqdm(range(22))
    print('Scrapy groups........')
    for i in range(0,440,20):

        response = requests.get(grouplink.format(i), headers=burp0_headers)
        # print(response.text)
        soup = BeautifulSoup(response.text,'html.parser')

        # pbar.update(1)
        print('Page:{}'.format(i//20))
        for group_info in soup.find_all('div',attrs={"class":"result"}):
            group_dict = {
                'group_link':group_info.find('a')['href'],
                'group_name':group_info.find('a')['title'],
                'group_intruduction':group_info.find('p').text
            }
            if city is not None:
                if group_dict['group_name'].find(city) != -1:
                    results.append(group_dict)
            else:
                results.append(group_dict)


    pprint(results)
    print('-------end')
    return results

def save_group(results):
    connection = sqlite3.connect('doubanzf.db', check_same_thread=False)
    connection.executescript("""
            CREATE TABLE IF NOT EXISTS group_info(
                _id INTEGER PRIMARY KEY,
                group_link TEXT UNIQUE,
                group_name TEXT NOT NULL,
                group_intruduction TEXT

            )
            """
                             )
    sql = "insert or replace into group_info(group_link,group_name,group_intruduction) values('{}','{}','{}')"
    for group in results:
        connection.execute(sql.format(group['group_link'],group['group_name'], group['group_intruduction']))
        connection.commit()

async def _content(link):
    """
    获取帖子内容
    :param link:
    :return:
    """
    # response = requests.get(link,headers=burp0_headers)
    content = await async_get_response(link,headers=burp0_headers)
    soup = BeautifulSoup(content,'html.parser')
    imgs = []
    content = ''
    for div in soup.find_all('div',attrs={'class':'rich-content topic-richtext'}):
        content = div.text
        for i in div.find_all('div',attrs={'class':'image-wrapper'}):
            img_path = i.img['src']
            imgs.append(img_path)

    return (content,imgs)

async def _topics(text):
    soup = BeautifulSoup(text, 'html.parser')
    topic_list = []
    post_detail = namedtuple('POST',['topic_link','topic_title','topic_date','topic_content','topic_imgs'])
    for topic in soup.find_all('tr', attrs={'class': ''}):
        topic_content, topic_imgs = await _content(topic.a['href'])
        # topic_dict = {
        #     'topic_link': topic.a['href'],
        #     'topic_title': topic.a['title'],
        #     'topic_date': topic.find('td', attrs={'class': 'time'}).text,
        #     'topic_content':topic_content,
        #     'topic_imgs':topic_imgs
        # }
        post = post_detail(topic.a['href'],topic.a['title'],topic.find('td', attrs={'class': 'time'}).text,topic_content,topic_imgs)
        topic_list.append(post)

    return topic_list

def _topic_page_2(text):
    soup = BeautifulSoup(text, 'html.parser')
    page_2_link = ''
    for more in soup.find_all('div', attrs={'class': 'group-topics-more'}):
        page_2_link = more.a['href']

    return page_2_link

# def post_get(grouplist):
#     """
#     :param grouplist: group's link list
#     :return:default 20 page's posts in group
#     """
#     topic_list = []
#     for link in grouplist:
#         crawler_page = 0
#         topic_list.append(_topics(link))
#         page_2_link = _topic_page_2(link)
#         page_2 = BeautifulSoup(requests.get(page_2_link,headers=burp0_headers).text, 'html.parser')
#         next_page = [ span.a['href'] for span in page_2.find_all('link',attrs={'rel':'next'})][0]
#         while True:
#             if crawler_page >= 20:
#                 break
#             if next_page:
#                 topic_list.append(_topics(next_page))
#                 page_next = BeautifulSoup(requests.get(next_page, headers=burp0_headers).text, 'html.parser')
#                 next_page = [span.a['href'] for span in page_next.find_all('link', attrs={'rel': 'next'})][0]
#             else:
#                 break
#             crawler_page += 1
#         pprint(topic_list)
#     return topic_list


def worker(group_links):
    """
    :param grouplist: group's link list
    :return:default 20 page's posts in group
    """
    # for group_link in group_links:
    async def run(work_queue,res_queue,sleep_time=3):
        while not work_queue.empty():
            group_link = work_queue.get_nowait()
            topic_list = []
            crawler_page = 0
            print(group_link)
            # topic_list.append(_topics(group_link))

            page_1 = await async_get_response(group_link,headers=burp0_headers)
            topics = await _topics(page_1)
            topic_list.extend(topics)
            print(page_1)
            page_2_link = _topic_page_2(page_1)
            # print('2 link is              ',page_1,page_2_link)
            page_2_content = await async_get_response(page_2_link,burp0_headers)
            page_2 = BeautifulSoup(page_2_content, 'html.parser')

            next_page = [ span.a['href'] for span in page_2.find_all('link',attrs={'rel':'next'})][0]
            while True:
                if crawler_page >= 5:
                    break
                if next_page:
                    time.sleep(sleep_time)
                    # page_2 = requests.get(next_page, headers=burp0_headers)
                    page_2 = await async_get_response(next_page,headers=burp0_headers)
                    topics = await _topics(page_2)
                    topic_list.extend(topics)
                    pprint(topics)
                    # topic_list.extend(await _topics(page_2.text))
                    page_next = BeautifulSoup(page_2, 'html.parser')
                    next_page = [span.a['href'] for span in page_next.find_all('link', attrs={'rel': 'next'})][0]
                else:
                    break
                crawler_page += 1
            res_queue.put_nowait(topic_list)
            return topic_list
    put_q = asyncio.Queue()
    res_q = asyncio.Queue()
    [put_q.put_nowait(group_link) for group_link in group_links]
    loop = asyncio.get_event_loop()
    tasks = [run(put_q,res_q) for task_id in range(1) ]
    loop.run_until_complete(asyncio.wait(tasks))
    loop.close()
    res_return = []


def crawler(grouplist):
    pool = multiprocessing.Pool(3)
    results = []
    for group_link in grouplist:
        results.append(pool.apply_async(worker,args=(group_link,)))
    for r in results:
        print(r.get())



# results = city_group()
# save_group(results)

group_test =['https://www.douban.com/group/257523/']
#
# group_test = ['https://www.douban.com/group/atlaslj/', 'https://www.douban.com/group/254559/',
#               'https://www.douban.com/group/263734/', 'https://www.douban.com/group/bpiao/']

# _content('https://www.douban.com/group/topic/179904848/')
# topic_page_link = 'https://www.douban.com/group/topic/183147721/'
# post_get(group_test)


def make_get_or_rotate_series(group_links):
    current_series = worker(group_links)
    def get_or_rotate_series(current_day=None):
        return current_series
    return get_or_rotate_series

if __name__ == '__main__':
    start = time.time()
    # # crawler(group_test)
    num = 0

    topics = worker(group_test)


    end = time.time()
    print('cost time is {}'.format(end-start))