from DrissionPage import ChromiumPage
from DrissionPage import ChromiumOptions
import pandas as pd
import time

# ========== 输入输出文件 ==========
csv_input_file = '小红书_deepseek_帖子详情.csv'
csv_output_file = '小红书_deepseek_用户主页信息.csv'

# ========== 初始化浏览器 ==========
co = ChromiumOptions()
co.set_browser_path(r'C:\Program Files\Google\Chrome\Application\chrome.exe')
dp = ChromiumPage(co)
dp.get('https://www.xiaohongshu.com')
input("🔐 请在弹出的浏览器中手动完成登录，登录成功后按回车继续...")

# ========== 读取用户主页链接 ==========
df = pd.read_csv(csv_input_file, encoding='utf-8-sig')
if '用户主页' not in df.columns:
    raise ValueError("❌ CSV中未找到'用户主页'列")
user_links = df['用户主页'].dropna().unique().tolist()

# ========== 爬取信息 ==========
results = []

for url in user_links:
    try:
        dp.get(url)
        time.sleep(3)

        # 用户名
        nickname_ele = dp.ele('css:div.user-name')
        nickname = nickname_ele.text.strip() if nickname_ele else ''

        # 红书号 + IP属地
        redid_ele = dp.ele('css:span.user-redId')
        red_id = redid_ele.text.replace('小红书号：', '').strip() if redid_ele else ''
        ip_ele = dp.ele('css:span.user-IP')
        ip_location = ip_ele.text.replace('IP属地：', '').strip() if ip_ele else ''

        # 简介
        desc_ele = dp.ele('css:div.user-desc')
        description = desc_ele.text.strip() if desc_ele else ''

        # 标签
        tag_divs = dp.eles('css:div.user-tags div.tag-item')
        tags = [t.text.strip() for t in tag_divs]
        tags_str = ', '.join(tags)

        # 数据信息
        data_spans = dp.eles('css:div.user-interactions > div')
        follows = data_spans[0].ele('tag:span').text if len(data_spans) > 0 else ''
        fans = data_spans[1].ele('tag:span').text if len(data_spans) > 1 else ''
        likes = data_spans[2].ele('tag:span').text if len(data_spans) > 2 else ''

        gender = ''
        gender_icon = dp.ele('css:.user-tags .gender use')
        if gender_icon:
            href = gender_icon.attr('xlink:href')
            if href == '#male':
                gender = '男'
            elif href == '#female':
                gender = '女'

        results.append({
            '用户主页': url,
            '昵称': nickname,
            '小红书号': red_id,
            '性别': gender,
            'IP属地': ip_location,
            '简介': description,
            '标签': tags_str,
            '关注数': follows,
            '粉丝数': fans,
            '获赞与收藏数': likes
        })
        print(f"✔ 成功抓取主页信息：{url}")
    except Exception as e:
        print(f"✘ 抓取失败：{url}，原因：{e}")
        continue

# ========== 保存 ==========
pd.DataFrame(results).to_csv(csv_output_file, index=False, encoding='utf-8-sig')
print(f"✅ 用户主页信息抓取完成，共写入 {len(results)} 条数据 → {csv_output_file}")