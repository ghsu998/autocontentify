import json
from modules.api.openai_api import chat_with_openai
from modules.database.db_connection import connect_db

def fetch_keywords_from_database():
    """直接從數據庫獲取關鍵詞列表，並只選擇 avg_monthly_searches >= 100 的關鍵字"""
    try:
        connection = connect_db()
        cursor = connection.cursor()
        # 加入條件：選擇 avg_monthly_searches >= 100 的關鍵字
        cursor.execute("SELECT keyword FROM ecommerce_data_db.keywords WHERE avg_monthly_searches >= 100")
        result = cursor.fetchall()
        cursor.close()
        connection.close()

        # 提取關鍵詞為列表
        keywords = [row["keyword"] for row in result]
        if not keywords:
            print("關鍵詞列表為空，請檢查數據庫內容。")
        return keywords
    except Exception as e:
        print(f"無法從數據庫加載關鍵詞: {e}")
        return []

def generate_blog_titles(keywords):
    """基於關鍵詞生成博客標題"""
    prompt = f"基於以下關鍵詞生成5個博客標題，返回格式為JSON數組：{', '.join(keywords)}。"
    response = chat_with_openai(prompt)
    try:
        titles = json.loads(response)
        if isinstance(titles, list):
            return titles
        elif isinstance(titles, dict):  # If response is a dictionary, handle it
            print("Response is a dictionary, extracting titles.")
            return [{"title": titles.get("title", "")}]  # Assuming the dictionary contains a title key
        else:
            print("生成的結果不是有效的JSON數組，請檢查API提示設計。")
            return []
    except json.JSONDecodeError:
        print("無法解析生成的標題為JSON格式，請檢查API響應。")
        return []

def main():
    keywords = fetch_keywords_from_database()
    if keywords:
        print(f"加載的關鍵詞: {keywords}")
        titles = generate_blog_titles(keywords)
        print(f"生成的博客標題: {titles}")
        for title in titles:
            # Extract the title string from the dictionary and ensure it's a valid string
            if isinstance(title, dict) and "title" in title and title["title"].strip():  # Ensure it's a valid string
                blog_content = generate_seo_blog_content(title["title"], keywords)
                if blog_content:
                    print(f"生成的博客內容: {blog_content}")
                    save_blog_to_database(title["title"], blog_content)
            else:
                print("Invalid title or empty title skipped.")
    else:
        print("未能加載關鍵詞，請檢查數據庫配置或數據表。")

def generate_seo_blog_content(title, keywords):
    """基於標題和關鍵詞生成SEO友好的博客內容"""
    prompt = (
        f"请根据以下标题编写一篇SEO优化的博客文章，内容包括引言、正文（分段落）、结论以及FAQ部分。\n"
        f"文章内容应满足以下要求：\n"
        f"1. 文章必须基于经验证的数据或行业公认的标准，确保准确无误。\n"
        f"2. 文章的结构应包括：一个引人入胜的引言部分，正文应分为几个清晰的章节，每个章节使用<h2>标签。\n"
        f"3. 生成的内容应不包含数字序列或编号、<h1>标签等不适合的结构。仅使用<h2>作为章节标题，确保内容的结构清晰，易于阅读。\n"
        f"4. 文章应避免推测，确保内容的深度和信息性，避免表面性的回答。\n"
        f"5. 请使用HTML格式返回内容，开头是<p>标签作为引言，之后使用<h2>标签为每一章标题，正文部分按段落清晰编排。\n"
        f"6. 为FAQ部分提供三个相关的常见问题与回答，确保每个问题都与博客标题相关，并且回答简洁明了。\n"
        f"7. 字數在1500字以上。\n\n"
        f"標題：{title}\n"
        f"關鍵詞：{', '.join(keywords)}\n"
        f"文章需有引人入勝的開頭段落和分段內容。"
    )
    content = chat_with_openai(prompt)
    # 簡單檢查返回的HTML內容
    if content.strip().startswith("<p>") and len(content) > 1500:
        return content
    else:
        print("生成的博客內容不符合要求，請檢查API提示設計。")
        return ""

def save_blog_to_database(title, content):
    """將生成的博客保存到數據庫"""
    try:
        connection = connect_db()
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO blogs (title, content) VALUES (%s, %s)",
            (title, content),
        )
        connection.commit()
        cursor.close()
        connection.close()
        print(f"成功將博客保存到數據庫: {title}")
    except Exception as e:
        print(f"保存博客到數據庫時發生錯誤: {e}")

if __name__ == "__main__":
    main()