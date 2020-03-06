const puppeteer = require('puppeteer');

(async () => {
  const browser = await puppeteer.launch({headless: false});
  const page = await browser.newPage();
  await page.setUserAgent('Mozilla/5.0 (X11; Linux x86_64; rv:71.0) Gecko/20100101 Firefox/71.0');
  
  await page.goto('https://www.bet365.es/#/IP/', {waitUntil: 'load'});
  await page.waitForSelector('.ipo-OverViewView ');

  const cookies = await page.cookies()

  html = await page.content();

  console.log(html);
  console.log(JSON.stringify(cookies));

  await browser.close();

})();