import os
import sys
import json
from openai import OpenAI
from dotenv import load_dotenv

# 動態添加項目根目錄到模塊搜索路徑
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)
from config.common import setup_logger

# 設置日誌記錄器
logger = setup_logger()


# 加载 .env 文件中的 API Key
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    logger.error("OPENAI_API_KEY is not set in the environment variables.")
    sys.exit("API Key not found.")

logger.info("OpenAI API key has been loaded successfully.")


def chat_with_openai(client: OpenAI, prompt: str, model: str = "gpt-4o") -> str:
    """
    调用 OpenAI ChatCompletion 接口生成响应文本。

    Args:
        client (OpenAI): OpenAI 客户端实例。
        prompt (str): 用户输入的提示内容。
        model (str): GPT 模型名称，默认为 "gpt-4o"。

    Returns:
        str: 模型生成的响应文本。

    Raises:
        Exception: 捕获所有异常并记录日志。
    """
    try:
        logger.info(f"Sending prompt to OpenAI: {prompt[:100]}...")
        # 调用 ChatCompletion 接口
        response = client.chat.completions.create(
            model=model,
            store=True,
            messages=[{"role": "user", "content": prompt}]
        )
        # 通过属性访问响应内容
        content = response.choices[0].message.content
        logger.info("Received response from OpenAI.")
        return content
    except Exception as e:
        logger.error(f"An error occurred while communicating with OpenAI: {e}")
        raise


def generate_rsa_text(client: OpenAI, keywords: list) -> dict:
    """
    调用 OpenAI API 生成 RSA 广告文案。
    """
    try:
        prompt = f"""
        **Objective**
        - Generate 15 unique headlines and 4 unique descriptions for a Google Ads Responsive Search Ad (RSA).

        **Rules for Headlines**
        - Maximum length: 30 characters (including spaces).
        - Must be short, clear, and engaging.
        - Avoid duplication.
        - Do not use special characters like `!`, `?`, or newline breaks.

        **Rules for Descriptions**
        - Maximum length: 90 characters (including spaces).
        - Must clearly communicate product benefits.
        - Include a strong call-to-action.
        - Avoid duplication and maintain relevance.

        **Ad Policy Compliance**
        - Avoid excessive punctuation or symbols.
        - Follow Google Ads policies on language and formatting.
        - Do not use prohibited words or phrases.

        **Best Practices**
        - Focus on clarity and relevance.
        - Ensure all text aligns with user intent.
        - Use strong value propositions in descriptions.

        **Keyword Optimization**
        - Optimize headlines and descriptions for provided keywords.
        {', '.join(keywords)}. 

        ***Return the response in JSON format as follows:
        {{
            "headlines": [
                "headline 1",
                "headline 2",
                ...
            ],
            "descriptions": [
                "description 1",
                "description 2",
                ...
            ]
        }}
        """
        # 调用 OpenAI API
        rsa_text = chat_with_openai(client, prompt)

        # 记录完整响应内容
        logger.debug(f"Full response content: {rsa_text}")

        # 如果内容以 Markdown 格式返回，去除包裹的标记符
        if rsa_text.strip().startswith("```json"):
            rsa_text = rsa_text.strip("```json").strip("```")

        # 解析返回的 JSON 文本
        rsa_data = json.loads(rsa_text)
        logger.info(f"Generated RSA Data: {rsa_data}")
        return rsa_data
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON response: {e}")
        raise ValueError("Invalid JSON format returned by OpenAI.")
    except Exception as e:
        logger.error(f"Error generating RSA text: {e}")
        raise


if __name__ == "__main__":
    """
    测试程序，演示 generate_rsa_text 的功能。
    """
    logger.info("Starting main testing program.")
    try:
        # 创建 OpenAI 客户端实例
        client = OpenAI(api_key=api_key)

        # 示例关键词
        test_keywords = ["compost bags", "eco-friendly", "13 gallon", "kitchen trash"]

        # 调用 generate_rsa_text 函数
        rsa_data = generate_rsa_text(client, test_keywords)

        # 打印生成的结果
        if rsa_data:
            logger.info("Generated RSA Data:")
            logger.info(json.dumps(rsa_data, indent=4))
        else:
            logger.warning("Failed to generate RSA data.")
    except Exception as e:
        logger.critical(f"Critical error occurred during testing: {e}")
