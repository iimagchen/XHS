from DrissionPage import ChromiumPage, ChromiumOptions
from DrissionPage.common import Keys
import pandas as pd
import time
import os

# ========== 更健壮的 CSV 读取函数 ==========
def robust_read_csv(file_path):
    try:
        df = pd.read_csv(file_path, encoding='utf-8-sig')
        print("📌 使用 utf-8-sig 成功读取文件")
        return df
    except Exception:
        try:
            df = pd.read_csv(file_path, encoding='gb18030')
            print("📌 使用 gb18030 成功读取文件")
            return df
        except Exception as e:
            print(f"❌ 无法读取 CSV：{e}")
            raise e

# ========== 浏览器配置 ==========
co = ChromiumOptions()
co.set_browser_path(r'C:\Program Files\Google\Chrome\Application\chrome.exe')

# ========== 参数设置 ==========
scroll_pause = 2.0
max_scroll_attempts = 50
output_file = '小红书_汇总详情链接.csv'

# ========== 加载关键词 ==========
keyword_file = 'keywords.csv'
df_keywords = robust_read_csv(keyword_file)

if '关键词' not in df_keywords.columns:
    raise ValueError("❌ CSV 文件中缺少 '关键词' 列")
keywords = df_keywords['关键词'].dropna().drop_duplicates().astype(str).tolist()
print(f"✅ 成功读取 {len(keywords)} 个关键词：{keywords}")

# ========== 初始化浏览器 ==========
dp = ChromiumPage(co)
dp.get('https://www.xiaohongshu.com')
input("请在弹出的浏览器中手动完成登录，登录成功后按回车键继续...")

# ========== 初始化输出文件 ==========
if os.path.exists(output_file):
    os.remove(output_file)
first_write = True

# ========== 爬取每个关键词 ==========
for search_keyword in keywords:
    print(f"\n======= 正在搜索关键词：{search_keyword} =======")

    search_box = dp.ele('css:#search-input')
    search_box.clear()
    time.sleep(0.5)
    search_box.input(search_keyword)
    search_box.input(Keys.ENTER)
    time.sleep(4)

    seen_links = set()
    results = []

    for attempt in range(max_scroll_attempts):
        a_tags = dp.eles('tag:a')
        new_count = 0

        for a in a_tags:
            try:
                href = a.attrs.get('href', '')
                if href.startswith('/search_result/') and href not in seen_links:
                    seen_links.add(href)
                    full_url = 'https://www.xiaohongshu.com' + href
                    results.append({'话题标签': search_keyword, '帖子链接': full_url})
                    print(f"[+] {full_url}")
                    new_count += 1
            except Exception as e:
                print(f"[-] 跳过一个链接，原因：{e}")

        print(f"第 {attempt + 1} 次滚动，新增链接数：{new_count}")

        is_bottom = dp.run_js(
            'return (window.innerHeight + window.scrollY) >= document.body.scrollHeight - 2'
        )
        if is_bottom:
            print("✅ 页面已滚动到底，结束爬取。")
            break

        dp.run_js('window.scrollTo(0, document.body.scrollHeight);')
        time.sleep(scroll_pause)

    # ========== 写入当前关键词结果 ==========
    if results:
        df = pd.DataFrame(results)
        df.to_csv(output_file, mode='a', index=False, encoding='utf-8-sig', header=first_write)
        first_write = False
        print(f"✅ [{search_keyword}] 写入 {len(results)} 条数据")
    else:
        print(f"⚠️ [{search_keyword}] 未提取到有效链接，跳过写入")
