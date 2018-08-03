from pyquery import PyQuery as pq
from urllib.parse import quote
from pymongo import MongoClient
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# 构造无界面谷歌浏览器
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
browser = webdriver.Chrome(chrome_options=chrome_options)


# 获取网页源码
def index_page(page):
    print('正在爬取第', page, '页')
    wait = WebDriverWait(browser, 20)
    # 构造网页链接
    keyword = "ipad"
    url = "https://s.taobao.com/search?q=" + quote(keyword)
    try:
        browser.get(url)
        if page > 1:
            input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,
                                                               '#mainsrp-pager > div > div > div > div.form > input')))
            submit = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, '#mainsrp-pager > div > div > div > div.form > '
                                                             'span.btn.J_Submit')))
            input.clear()  # 清空
            input.send_keys(page)  # 输入
            submit.click()  # 点击
        wait.until(EC.text_to_be_present_in_element(
            (By.CSS_SELECTOR, '#mainsrp-pager > div > div > div > ul > li.item.active > span'), str(page)))
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#mainsrp-itemlist .m-itemlist .items .item')))
        get_results()
    except TimeoutException:
        print('Timeout')


# 信息提取
def get_results():
    html = browser.page_source
    doc = pq(html)
    items = doc('#mainsrp-itemlist .m-itemlist .items .item').items()
    for item in items:
        data = {
            '商品': item.find('.title').text(),
            '图片链接': item.find('.pic .img').attr('data-src'),
            '价格': item.find('.price').text(),
            '购买人数': item.find('.deal-cnt').text(),
            '店铺名称': item.find('.shop').text(),
            '店铺地址': item.find('.location').text()
        }
        save_to_mongodb(data)


# 数据存储
def save_to_mongodb(data):
    client = MongoClient(host='localhost', port=27017)
    db = client.taobao
    collection = db.data_3
    try:
        if collection.insert(data):
            print('存储成功')
    except Exception:
        print('存储失败')


def main():
    for i in range(1, 101):
        index_page(i)


if __name__ == '__main__':
    main()
