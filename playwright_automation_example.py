#!/usr/bin/env python3
"""
Playwright MCP 自动化脚本示例
这个脚本展示了如何使用 Python 代码操作 Playwright MCP
"""

from playwright.sync_api import sync_playwright
import time
import json

class PlaywrightAutomation:
    def __init__(self):
        self.browser = None
        self.page = None
    
    def start_browser(self, headless=False):
        """启动浏览器"""
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=headless)
        self.page = self.browser.new_page()
    
    def close_browser(self):
        """关闭浏览器"""
        if self.browser:
            self.browser.close()
        if hasattr(self, 'playwright'):
            self.playwright.stop()
    
    def navigate_to(self, url):
        """导航到指定URL"""
        self.page.goto(url)
        self.page.wait_for_load_state('networkidle')
    
    def search_baidu(self, search_term):
        """在百度搜索指定内容"""
        # 导航到百度
        self.navigate_to('https://www.baidu.com')
        
        # 等待搜索框加载
        self.page.wait_for_selector('#kw')
        
        # 执行搜索
        self.page.evaluate(f"""
            document.querySelector('#kw').value = '{search_term}';
            document.querySelector('#su').click();
        """)
        
        # 等待搜索结果
        self.page.wait_for_selector('.result')
        
        # 获取搜索结果
        results = self.page.evaluate("""
            () => {
                const resultElements = document.querySelectorAll('.result h3 a');
                return Array.from(resultElements).map(el => ({
                    title: el.textContent,
                    url: el.href
                }));
            }
        """)
        
        return results
    
    def login_automation(self, login_url, username, password):
        """自动化登录"""
        self.navigate_to(login_url)
        
        # 填写登录表单
        self.page.evaluate(f"""
            document.querySelector('#username').value = '{username}';
            document.querySelector('#password').value = '{password}';
            document.querySelector('#login-button').click();
        """)
        
        # 等待登录完成
        self.page.wait_for_selector('.dashboard', timeout=10000)
        print("登录成功！")
    
    def fill_form(self, form_data):
        """动态填写表单"""
        self.page.evaluate(f"""
            (data) => {{
                Object.keys(data).forEach(key => {{
                    const element = document.querySelector(`[name="${{key}}"]`);
                    if (element) {{
                        element.value = data[key];
                    }}
                }});
                
                const submitButton = document.querySelector('button[type="submit"]');
                if (submitButton) {{
                    submitButton.click();
                }}
            }}
        """, form_data)
    
    def scrape_data(self, selector='.item'):
        """数据抓取"""
        data = self.page.evaluate(f"""
            () => {{
                const items = document.querySelectorAll('{selector}');
                return Array.from(items).map(item => ({{
                    title: item.querySelector('.title')?.textContent,
                    price: item.querySelector('.price')?.textContent,
                    link: item.querySelector('a')?.href
                }}));
            }}
        """)
        return data
    
    def take_screenshot(self, filename='screenshot.png'):
        """截图"""
        self.page.screenshot(path=filename)
        print(f"截图已保存: {filename}")
    
    def wait_for_element(self, selector, timeout=30000):
        """等待元素出现"""
        self.page.wait_for_selector(selector, timeout=timeout)
    
    def click_element(self, selector):
        """点击元素"""
        self.page.click(selector)
    
    def type_text(self, selector, text):
        """输入文本"""
        self.page.fill(selector, text)
    
    def get_text(self, selector):
        """获取元素文本"""
        return self.page.text_content(selector)
    
    def execute_js(self, js_code):
        """执行自定义JavaScript代码"""
        return self.page.evaluate(js_code)

def main():
    """主函数示例"""
    automation = PlaywrightAutomation()
    
    try:
        # 启动浏览器
        automation.start_browser(headless=False)
        
        # 示例1: 百度搜索
        print("开始百度搜索...")
        results = automation.search_baidu('cursor')
        print(f"找到 {len(results)} 个搜索结果")
        for i, result in enumerate(results[:3], 1):
            print(f"{i}. {result['title']}")
        
        # 示例2: 截图
        automation.take_screenshot('baidu_search_results.png')
        
        # 示例3: 执行自定义JavaScript
        page_title = automation.execute_js("document.title")
        print(f"页面标题: {page_title}")
        
    except Exception as e:
        print(f"发生错误: {e}")
    
    finally:
        # 关闭浏览器
        automation.close_browser()

if __name__ == "__main__":
    main()


