const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');

const downloadPath = path.resolve(__dirname, 'downloads');
if (!fs.existsSync(downloadPath)) fs.mkdirSync(downloadPath);

async function run() {
  const browser = await puppeteer.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });

  const page = await browser.newPage();

  const client = await page.target().createCDPSession();
  await client.send('Page.setDownloadBehavior', {
    behavior: 'allow',
    downloadPath: downloadPath
  });

  await page.setUserAgent(
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML,\
    like Gecko) Chrome/118.0.0.0 Safari/537.36'
  );

  console.log('NASDAQ 접속 중...');
  await page.goto('https://www.nasdaq.com/market-activity/etf/screener', {
    waitUntil: 'networkidle2',
    timeout: 0
  });

  console.log('다운로드 버튼 대기 중...');
  const selector = 'body > div.dialog-off-canvas-main-canvas > div > main > \
                    div.page__content > div.layout.layout--2-col-large > div > \
                    section > div.symbol-screener__content > \
                    div.symbol-screener__results > header > div > div > button';
  const exportBtn = await page.waitForSelector(selector, { timeout: 20000 });
  await exportBtn.click();

  console.log('다운로드 대기...');
  await new Promise(resolve => setTimeout(resolve, 10000));

  console.log('다운로드 완료!');
  await browser.close();
}

run().catch(console.error);
