import requests
from bs4 import BeautifulSoup
import time
import hmac
import hashlib
import base64
import urllib.parse

# ===== 配置区（必须修改）=====
WEBHOOK_URL = "https://oapi.dingtalk.com/robot/send?access_token=6bb889caeaf95be483506d6745260224d958cd00737cd174c46f607c49154f34"
SECRET = "SEC0412df4f205069a3182f4de9ceed52159b572037b0115d7b6458ae83d951b257"
# ===========================

HEADERS = {'User-Agent': 'Mozilla/5.0'}

def fetch_tax_policy():
    """获取国家税务总局政策"""
    try:
        url = "http://www.chinatax.gov.cn/chinatax/n810341/n810825/index.html"
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        news_list = []
        
        # 提取最新3条政策
        for item in soup.select('.list-content li')[:3]:
            title = item.a.text.strip()
            link = "http://www.chinatax.gov.cn" + item.a['href']
            news_list.append(f"▸ {title}\n🔗 {link}")
        
        return "\n\n".join(news_list) if news_list else "暂无最新政策"
    except Exception as e:
        return f"税务政策获取失败: {str(e)}"

def fetch_stock_news():
    """获取财经新闻（会计关注版）"""
    try:
        url = "https://finance.eastmoney.com/"
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        news_list = []
        
        # 只保留含财税关键词的新闻
        for item in soup.select('.news_item')[:5]:
            title = item.a.text.strip()
            link = item.a['href']
            if any(kw in title for kw in ["税", "政策", "财报", "会计", "财政"]):
                news_list.append(f"▸ {title}\n🔗 {link}")
        
        return "\n\n".join(news_list[:3]) if news_list else "暂无相关财经新闻"
    except Exception as e:
        return f"财经新闻获取失败: {str(e)}"

def send_dingtalk(content):
    """发送钉钉消息（加签版）"""
    timestamp = str(round(time.time() * 1000))
    secret_enc = SECRET.encode('utf-8')
    string_to_sign = f"{timestamp}\n{SECRET}"
    hmac_code = hmac.new(secret_enc, string_to_sign.encode('utf-8'), 
                        digestmod=hashlib.sha256).digest()
    sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
    
    url = f"{WEBHOOK_URL}&timestamp={timestamp}&sign={sign}"
    data = {
        "msgtype": "markdown",
        "markdown": {
            "title": "财经财税早报",
            "text": f"### 📊 会计专属财经早报 {time.strftime('%Y-%m-%d %H:%M')}\n\n"
                    f"**🏛️ 税务政策**\n{content.split('---')[0]}\n\n"
                    f"**💹 财经要闻**\n{content.split('---')[1]}\n\n"
                    f"> 数据来源：国家税务总局、东方财富网"
        }
    }
    requests.post(url, json=data)

def main():
    # 获取最新政策
    tax_news = fetch_tax_policy()
    # 获取财经新闻
    stock_news = fetch_stock_news()
    # 发送消息
    send_dingtalk(f"{tax_news}\n---\n{stock_news}")

if __name__ == "__main__":
    main()