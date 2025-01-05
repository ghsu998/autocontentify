from modules.api.shopify_api import get_shopify_blogs, create_or_update_shopify_blog
from modules.database.db_connection import connect_db
from datetime import datetime
import pymysql

def sync_shopify_to_db():
    """同步 Shopify 博客到本地数据库"""
    articles = get_shopify_blogs()
    if not articles:
        print("No blogs fetched from Shopify.")
        return

    conn = connect_db()
    cursor = conn.cursor()

    for article in articles:
        shopify_article_id = article["id"]
        title = article["title"]
        content = article["body_html"]
        updated_at = datetime.strptime(article["updated_at"], "%Y-%m-%dT%H:%M:%S%z")

        cursor.execute("""
            INSERT INTO blogs (shopify_article_id, title, content, last_updated_at, synced_to_shopify)
            VALUES (%s, %s, %s, %s, TRUE)
            ON DUPLICATE KEY UPDATE
                title = VALUES(title),
                content = VALUES(content),
                last_updated_at = VALUES(last_updated_at),
                synced_to_shopify = TRUE
        """, (shopify_article_id, title, content, updated_at))

    conn.commit()
    cursor.close()
    conn.close()
    print("Shopify blogs synchronized to database successfully.")

def sync_db_to_shopify():
    """同步本地数据库博客到 Shopify"""
    conn = connect_db()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    cursor.execute("""
        SELECT * FROM blogs
        WHERE synced_to_shopify = FALSE
    """)
    unsynced_blogs = cursor.fetchall()

    for blog in unsynced_blogs:
        blog_data = {
            "title": blog["title"],
            "body_html": blog["content"]
        }

        success, shopify_article_id = create_or_update_shopify_blog(
            shopify_article_id=blog.get("shopify_article_id"),
            blog_data=blog_data
        )

        if success:
            print(f"Successfully synced blog: {blog['title']}")
            cursor.execute("""
                UPDATE blogs
                SET shopify_article_id = %s, synced_to_shopify = TRUE, last_updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
            """, (shopify_article_id, blog["id"]))
        else:
            print(f"Failed to sync blog: {blog['title']}")

    conn.commit()
    cursor.close()
    conn.close()
    print("Database blogs synchronized to Shopify successfully.")

if __name__ == "__main__":
    print("Starting Shopify and Database Blog Synchronization...")
    sync_shopify_to_db()  # 从 Shopify 同步到本地数据库
    sync_db_to_shopify()  # 从本地数据库同步到 Shopify
    print("Synchronization completed successfully.")