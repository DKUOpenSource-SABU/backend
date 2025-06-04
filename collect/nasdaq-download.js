const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');

// 다운로드 경로 설정
const downloadPath = path.resolve(__dirname, '../data/downloads');
if (!fs.existsSync(downloadPath)) fs.mkdirSync(downloadPath);

// Nasdaq ETF 데이터를 다운로드하는 스크립트
// 작성자 : 김태형
async function run() {
  // Puppeteer를 사용하여 NASDAQ ETF Screener 페이지에 접속
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

  // User-Agent 설정
  await page.setUserAgent(
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML,\
    like Gecko) Chrome/118.0.0.0 Safari/537.36'
  );

  console.log('NASDAQ 접속 중...');
  await page.goto('https://www.nasdaq.com/market-activity/etf/screener', {
    waitUntil: 'networkidle2',
    timeout: 0
  });

  // 다운로드 버튼을 기다리고 클릭 (ETF Screener)
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
  console.log('다운로드된 파일 업데이트 중...');
  const downloadedFiles = fs.readdirSync(downloadPath);
  const latestFile = downloadedFiles
    .map(file => ({
      name: file,
      time: fs.statSync(path.join(downloadPath, file)).mtime.getTime()
    }))
    .sort((a, b) => b.time - a.time)[0]?.name;
  if (latestFile) {
    const sourceFile = path.join(downloadPath, latestFile);
    const destinationFile = path.resolve(__dirname, '../data/ticker_etf.csv');
    fs.copyFileSync(sourceFile, destinationFile);
  }
  console.log('다운로드된 파일 이름:', latestFile);

  await browser.close();
}

// Nasdaq Stock 데이터를 다운로드하는 스크립트
// 작성자 : 김태형
async function run2() {
  // Puppeteer를 사용하여 NASDAQ Stock Screener 페이지에 접속
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

  // User-Agent 설정
  await page.setUserAgent(
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36'
  );

  console.log('NASDAQ Stock Screener 접속 중...');
  await page.goto('https://www.nasdaq.com/market-activity/stocks/screener', {
    waitUntil: 'networkidle2',
    timeout: 0
  });

  // 다운로드 버튼을 기다리고 클릭 (Stock Screener)
  console.log('다운로드 버튼 대기 중...');
  const selector = 'body > div.dialog-off-canvas-main-canvas > div > main > \
                    div.page__content > article > div > div.nsdq-bento-layout__main.nsdq-c-band.nsdq-c-band--white.nsdq-u-padding-top-md.\
                    nsdq-u-padding-bottom-md.nsdq-c-band__overflow_hidden > div.nsdq-l-layout-container.nsdq-l-layout-container--contained.\
                    nsdq-bento-ma.nsdq-u-padding-top-none.nsdq-u-padding-bottom-none.nsdq-u- > div > div.nsdq-sticky-container > div > div > \
                    div:nth-child(2) > div > div.jupiter22-c-symbol-screener__container > div.jupiter22-c-table-container > div.jupiter22-c-table__download > \button';

  const exportBtn = await page.waitForSelector(selector, { timeout: 20000 });
  await exportBtn.click();

  console.log('다운로드 대기...');
  await new Promise(resolve => setTimeout(resolve, 10000));

  console.log('다운로드 완료!');
  console.log('다운로드된 파일 업데이트 중...');
  const downloadedFiles = fs.readdirSync(downloadPath);
  const latestFile = downloadedFiles
    .map(file => ({
      name: file,
      time: fs.statSync(path.join(downloadPath, file)).mtime.getTime()
    }))
    .sort((a, b) => b.time - a.time)[0]?.name;
  if (latestFile) {
    const sourceFile = path.join(downloadPath, latestFile);
    const destinationFile = path.resolve(__dirname, '../data/ticker_stock.csv');
    fs.copyFileSync(sourceFile, destinationFile);
  }
  console.log('다운로드된 파일 이름:', latestFile);

  await browser.close();
}

// 2개의 스크립트를 순차적으로 실행
run().catch(console.error);
run2().catch(console.error);
