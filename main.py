import streamlit as st
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from typing import List
from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from xiaohongshu_prompt_template import system_template_text
from xiaohongshu_prompt_template import user_template_text
from langchain.output_parsers import PydanticOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field


st.markdown("<div style='text-align:center;'>作者：xcxxcxcc</div>", unsafe_allow_html=True)

user_dict = {"admin": "123456", "徐余佳": "13921957690",
             "顾洁": "18051848683", "徐超": "15262321283"}  # 存储用户名和密码的字典

# 定义应用程序可用页面及其对应标识符的字典
PAGES = {
    '✨ 爆款小红书 AI 写作助手': 'page_1',
    '💬 聊天机器人': 'page_2',
    '🎬 视频脚本生成器': 'page_3',
}

# 默认显示登录表单
show_login_form = True

# 检查session状态以判断用户是否已登录，若已登录则隐藏登录表单
if "is_logged_in" in st.session_state:
    show_login_form = not st.session_state.is_logged_in

# 若需要显示登录表单
if show_login_form:
    # 创建登录表单：用户名输入框、密码（类型为password）输入框及登录按钮
    st.title("✨欢迎使用AI大模型应用小程序")
    username = st.text_input("请输入你的名字：")
    password = st.text_input("请输入密码：", type="password")
    login_button = st.button("🚀 登录")

    # 用户点击登录按钮后进行验证
    if login_button:
        # 验证用户名和密码是否匹配（假设存在预定义的user_dict）
        if username in user_dict and password == user_dict[username]:
            # 登录成功，更新session状态
            st.session_state.is_logged_in = True
            st.success("用户验证成功，请再点击一次登录键！")
            st.success("在左侧菜单栏选择您需要访问的程序。")

        else:
            # 登录失败，显示警告消息
            st.warning("用户名或密码错误，请重试。")
else:
    # 用户已登录，显示页面选择侧边栏
    selected_page = st.sidebar.selectbox('请选择您需要访问的程序', list(PAGES.keys()))

    # 显示加载提示并根据用户选择动态插入相应页面的HTML元素
    with st.spinner('加载中...'):
        st.markdown(f'<div id="{PAGES[selected_page]}">', unsafe_allow_html=True)

        if selected_page == '🎬 视频脚本生成器':
            # 在此处添加写作助手的相关组件、图表、文本等
            def generate_script(subject, video_length,
                                creativity, api_key):
                """
                生成指定主题视频的脚本和标题。

                参数:
                - subject: 视频的主题。
                - video_length: 视频的长度（单位未指定，如分钟、秒等）。
                - creativity: 用于生成脚本的创意级别，影响生成结果的多样性。
                - api_key: 使用的API密钥，用于访问生成脚本所需的AI服务。

                返回值:
                - script: 生成的视频脚本。
                - title: 生成的视频标题。
                """
                # 定义标题和脚本的模板
                title_template = ChatPromptTemplate.from_messages(
                    [
                        ("human", "请为'{subject}'这个主题的视频想一个吸引人的标题")
                    ]
                )
                script_template = ChatPromptTemplate.from_messages(
                    [
                        ("human",
                         """你是一位短视频频道博主，根据以下标题和相关信息，为短视频频道
                         写一个视频脚本。
                         视频标题：{title}，视频时长：{duration}，生成的脚本长度尽量
                         遵循视频时长的要求。
                         要求开头抓住眼球，中间提供干货内容，结尾有惊喜，脚本格式也请按照
                         【开头、中间、结尾】分隔。
                         整体内容的表达方式尽量要轻松有趣，吸引年轻人。
                         请确保所有输入内容均为中文。
                         开头、中间、结尾均分段，如：
                            '''
                            【开头】...
                            【中间】...
                            【结尾】...
                            '''
                         """)
                    ]
                )

                # 初始化用于生成标题和脚本的AI模型
                model = ChatOpenAI(temperature=creativity,
                                   model_name="gpt-3.5-turbo",
                                   openai_api_key=api_key,
                                   openai_api_base="https://api.aigc369.com/v1")

                # 使用AI模型根据主题生成标题
                title_chain = title_template | model
                script_chain = script_template | model

                title = title_chain.invoke({"subject": subject}).content

                # 根据标题和视频长度生成脚本
                script = script_chain.invoke({"title": title, "duration": video_length}).content

                return title, script


            # 设置页面标题
            st.title("🎬 视频脚本生成器")

            # 在侧边栏接收用户输入的OpenAI API秘钥
            with st.sidebar:
                openai_api_key = st.text_input("请输入OpenAI API秘钥", type="password")
                st.markdown("[若无秘钥，请点此获取](https://api.aigc369.com/register)")

            # 添加分隔线
            st.divider()

            # 接收用户输入的视频脚本主题
            subject = st.text_input("💡 请输入视频脚本主题")

            # 添加分隔线
            st.divider()

            # 接收用户输入的视频长度（单位：分钟）
            video_length = st.number_input("⏱️ 请输入视频长度（单位：分钟）", min_value=0.1,
                                           max_value=10.0, value=5.0, step=0.1)

            # 添加分隔线
            st.divider()

            # 接收用户选择的创意程度
            creativity = st.slider("✨ 请选择创意程度", min_value=0.0, max_value=1.0,
                                   value=0.2, step=0.1)

            # 创建生成脚本按钮
            button_script = st.button("🚀 生成脚本", key='key_1')

            # 按钮点击后执行逻辑
            if button_script:
                # 检查是否输入了OpenAI API秘钥和主题
                if not openai_api_key:
                    st.error("请输入OpenAI API秘钥")
                    st.stop()
                if not object:
                    st.error("请输入主题")
                    st.stop()

                # 显示加载提示并开始生成脚本
                try:
                    with st.spinner("⏳ 正在生成脚本..."):
                        title, script = generate_script(subject, video_length,
                                                        creativity, openai_api_key)

                        # 展示生成的标题和脚本
                        st.subheader("💡 标题：")
                        st.write(title)
                        st.subheader("💡 视频脚本：")
                        st.write(script)

                        # 显示生成成功提示
                        st.success("✅ 脚本生成成功")
                except Exception as e:
                    # 处理生成脚本过程中出现的异常
                    st.error(f"❌ 脚本生成失败❗️❗️❗")
                    st.error(f"错误内容：{e}")

        elif selected_page == '💬 聊天机器人':
            # 在此处添加聊天机器人的相关组件、图表、文本等
            def chat_with_gpt(prompt, memory, openai_api_key):
                """
                使用GPT-3.5 Turbo模型与用户进行聊天交互。

                参数:
                - prompt: 用户输入的聊天内容
                - memory: 对话记忆对象，用于记录对话历史
                - openai_api_key: OpenAI API密钥

                返回:
                - response: GPT模型生成的聊天回复
                """
                # 初始化ChatOpenAI模型
                model = ChatOpenAI(model_name="gpt-3.5-turbo",
                                   openai_api_key=openai_api_key,
                                   openai_api_base="https://api.aigc369.com/v1")

                # 创建ConversationChain对象，结合模型和对话记忆进行聊天
                chain = ConversationChain(llm=model, memory=memory)

                # 发起聊天请求，获取模型回复
                response = chain.invoke({"input": prompt})
                return response["response"]


            st.title("💬 聊天机器人")

            # 在侧边栏接收用户输入的OpenAI API秘钥
            with st.sidebar:
                openai_api_key = st.text_input("请输入OpenAI API秘钥", type="password")
                st.markdown("[若无秘钥，请点此获取](https://api.aigc369.com/register)")

            # 初始化会话状态中的对话记忆和消息记录
            if "memory" not in st.session_state:
                st.session_state["memory"] = ConversationBufferMemory(return_messages=True)
                st.session_state["messages"] = [{"role": "ai",
                                                 "content": "我是您的AI聊天助手，请问有什么可以帮您？"}]

            # 展示已有的对话消息
            for message in st.session_state["messages"]:
                st.chat_message(message["role"]).write(message["content"])

            # 创建聊天输入框，接收用户输入
            prompt = st.chat_input("💬 ")

            # 新增：创建清空历史问答按钮
            clear_history_button = st.button("清空历史问答", key="key_3")
            if clear_history_button:
                st.session_state["messages"] = []

            # 处理用户输入的聊天内容
            if prompt:
                # 检查是否输入了OpenAI API秘钥
                if not openai_api_key:
                    st.error("请输入OpenAI API秘钥")
                    st.stop()

                # 将用户输入添加至消息记录，并在聊天界面展示
                st.session_state["messages"].append({"role": "human", "content": prompt})
                st.chat_message("human").write(prompt)

                try:
                    # 显示加载提示并开始生成回复
                    with st.spinner("⏳ 正在生成回答..."):
                        # 使用chat_with_gpt函数与GPT模型进行交互，生成回复
                        response = chat_with_gpt(prompt, st.session_state["memory"], openai_api_key)

                    # 将生成的回复添加至消息记录，并在聊天界面展示
                    msg = {"role": "ai", "content": response}
                    st.session_state["messages"].append(msg)
                    st.chat_message("ai").write(response)
                except Exception as e:
                    # 处理生成回复过程中出现的异常
                    st.error(f"✖️ 回答生成失败❗️❗️❗️")
                    st.error(f"错误内容：{e}")

        elif selected_page == '✨ 爆款小红书 AI 写作助手':
            # 在此处添加视频脚本生成器的相关组件、图表、文本等.
            def generate_xiaohongshu(theme, openai_api_key):
                """
                使用GPT-3.5 Turbo模型生成小红书内容。

                参数:
                - theme: 小红书的主题

                返回:
                - Xiaohongshu: 根据主题生成的小红书内容模型对象
                """

                # 定义用于生成小红书内容的ChatPromptTemplate和ChatOpenAI对象
                prompt = ChatPromptTemplate.from_messages([
                    ("system", system_template_text),
                    ("user", user_template_text)
                ])
                model = ChatOpenAI(model_name="gpt-3.5-turbo",
                                   openai_api_key=openai_api_key,
                                   openai_api_base="https://api.aigc369.com/v1")
                output_parser = PydanticOutputParser(pydantic_object=Xiaohongshu)

                # 构建链式调用并使用提供的主题生成小红书内容
                chain = prompt | model | output_parser
                result = chain.invoke({
                    "parser_instructions": output_parser.get_format_instructions(),
                    "theme": theme})
                return result


            class Xiaohongshu(BaseModel):
                """
                小红书内容模型，用于定义小红书发布的内容结构。

                属性:
                - titles: 包含小红书五个标题的列表。每个标题应为字符串，且列表长度必须为5。
                - content: 小红书的内容，为字符串。应进行适当地处理以避免过长或包含特殊字符。
                """
                titles: List[str] = Field(description="小红书的五个标题",
                                          min_items=5, max_items=5)
                content: str = Field(description="小红书的内容")


            # 设置页面标题
            st.title("✨ 爆款小红书 AI 写作助手")

            # 在侧边栏接收用户输入的OpenAI API秘钥
            with st.sidebar:
                openai_api_key = st.text_input("请输入OpenAI API秘钥", type="password")
                st.markdown("[若无秘钥，请点此获取](https://api.aigc369.com/register)")

            # 添加分隔线
            st.divider()

            # 接收用户输入的小红书文案主题
            theme = st.text_input("💡 请输入小红书文案主题")

            # 添加分隔线
            st.divider()

            # 创建生成文案按钮
            button_xiaohongshu = st.button("🚀 生成文案", key='key_2')

            # 按钮点击后执行逻辑
            if button_xiaohongshu:
                # 检查是否输入了OpenAI API秘钥和主题
                if not openai_api_key:
                    st.error("请输入OpenAI API秘钥")
                    st.stop()
                if not theme:
                    st.error("请输入主题")
                    st.stop()

                # 显示加载提示并开始生成小红书内容
                try:
                    with st.spinner("⏳ 正在生成文案..."):
                        # 使用输入的主题生成小红书内容
                        result = generate_xiaohongshu(theme, openai_api_key)

                        # 在左右两列分别展示小红书标题和内容
                        left_column, right_column = st.columns(2)
                        with left_column:
                            st.markdown("##### 小红书标题1")
                            st.write(result.titles[0])
                            st.markdown("##### 小红书标题2")
                            st.write(result.titles[1])
                            st.markdown("##### 小红书标题3")
                            st.write(result.titles[2])
                            st.markdown("##### 小红书标题4")
                            st.write(result.titles[3])
                            st.markdown("##### 小红书标题5")
                            st.write(result.titles[4])
                        with right_column:
                            st.markdown("##### 小红书内容正文")
                            st.write(result.content)

                        # 显示生成成功提示
                        st.success("✅ 文案生成成功")
                except Exception as e:
                    # 处理生成小红书内容过程中出现的异常
                    st.error(f"✖️ 文案生成失败❗️❗️❗️")
                    st.error(f"错误内容：{e}")
        st.markdown('</div>', unsafe_allow_html=True)
