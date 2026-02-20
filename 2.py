import asyncio
from playwright.async_api import async_playwright


async def run(playwright):
    browser = await playwright.chromium.launch(headless=True)  # 启用无头模式
    page = await browser.new_page()

    # 监听页面的控制台输出并打印到 Python 控制台
    page.on("console", lambda msg: print(f"Console message: {msg.text()}"))

    # 在页面上下文中创建 WebSocket 连接并处理消息
    await page.evaluate("""
        () => {
            const ws = new WebSocket('wss://ws.gmgn.ai/stream?_t=true');

            ws.onopen = () => {
                console.log('Connected to WebSocket server');
                ws.send('ping');
                console.log('Sent: ping');
            };

            ws.onmessage = (event) => {
                console.log(`Received: ${event.data}`);
                // 根据需要处理接收到的消息
                if (event.data === 'pong') {
                    console.log('Received pong, closing WebSocket.');
                    ws.close();
                }
            };

            ws.onclose = () => {
                console.log('WebSocket connection closed');
            };
        }
    """)

    # 保持页面打开，等待消息处理完成
    await page.wait_for_timeout(5000)

    await browser.close()


async def main():
    async with async_playwright() as playwright:
        await run(playwright)


# 运行异步主程序
asyncio.run(main())