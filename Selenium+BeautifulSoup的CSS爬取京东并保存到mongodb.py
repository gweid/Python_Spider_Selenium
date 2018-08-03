import time
import pymongo
from urllib.parse import urlencode
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 构造无界面谷歌浏览器
chrome_options = Options()
chrome_options.add_argument('--headless')
browser = webdriver.Chrome(chrome_options=chrome_options)
wait = WebDriverWait(browser, 50)


# 获取网页源码
def indext_page(page):
    print('正在爬取第', page, '页...')
    # 构造网页url
    params = {
        'keyword': '机械表',
        'enc': 'utf-8',
        'wq': '机械表'
    }
    url = 'https://search.jd.com/Search?' + urlencode(params)
    # 进行异常处理会避免一条爬取出错程序退出退出
    try:
        '''
        京东没打开一页不会加载完信息，需要往下拉才会逐步加载；所以这里模拟下拉进度条，并提供延时等待'''
        browser.get(url)
        browser.execute_script('window.scrollTo(0,document.body.scrollTop=2000)')
        time.sleep(2)
        browser.execute_script('window.scrollTo(2500,document.body.scrollTop=5000)')
        time.sleep(2)
        browser.execute_script('window.scrollTo(5000,document.body.scrollTop=7500)')
        time.sleep(2)
        '''
        如果页码大于一，将点击下一页进行跳转'''
        if page > 1:
            submit = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#J_bottomPage > span.p-num > a.pn-next')))
            submit.click()
        wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.gl-warp .gl-item')))
        parse_html(browser.page_source)
    except TimeoutException:
        print('超时')


# 进行数据的提取
def parse_html(html):
    soup = BeautifulSoup(html, 'lxml')
    names = soup.select('.gl-item .p-name')
    prices = soup.select('.gl-item .p-price')
    commits = soup.select('.gl-item .p-commit')
    shops = soup.select('.gl-item .curr-shop')
    for name, price, commit, shop in zip(names, prices, commits, shops):
        data = {
            '商品': name.get_text().strip(),
            '价格': price.get_text().strip(),
            '评论数': commit.get_text().strip(),
            '商店名': shop.get_text()
        }
        save_to_mongodb(data)


# 数据的存储
def save_to_mongodb(data):
    client = pymongo.MongoClient(host='localhost', port=27017)
    db = client.jingdong
    collection = db.all_jixiebiao2
    try:
        if collection.insert(data):
            print('存储成功')
    except Exception:
        print('存储失败')


def main():
    for i in range(1, 101):
        indext_page(i)


if __name__ == '__main__':
    main()
    browser.close()
