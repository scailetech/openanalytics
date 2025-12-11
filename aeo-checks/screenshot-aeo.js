const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();
  
  try {
    console.log('Navigating to http://localhost:3002...');
    await page.goto('http://localhost:3002');
    await page.waitForLoadState('networkidle');
    
    // Take screenshot of homepage
    await page.screenshot({ path: 'homepage.png', fullPage: true });
    console.log('Homepage screenshot saved as homepage.png');
    
    // Look for navigation to AEO mentions check or similar pages
    console.log('Looking for AEO mentions check or analysis pages...');
    
    // Try to find links or buttons that might lead to the AEO mentions check
    const links = await page.$$eval('a', els => els.map(el => ({ text: el.textContent, href: el.href })));
    console.log('Available links:', links);
    
    // Check if there are any forms or buttons related to AEO
    const buttons = await page.$$eval('button', els => els.map(el => el.textContent));
    console.log('Available buttons:', buttons);
    
    // Look for any input fields that might be for entering URLs
    const inputs = await page.$$eval('input', els => els.map(el => ({ type: el.type, placeholder: el.placeholder, name: el.name })));
    console.log('Available inputs:', inputs);
    
    // If there's a URL input, try entering a sample URL
    const urlInput = await page.$('input[type="url"], input[placeholder*="url"], input[placeholder*="URL"], input[name*="url"]');
    if (urlInput) {
      console.log('Found URL input, entering sample URL...');
      await urlInput.fill('https://example.com');
      
      // Look for submit button
      const submitBtn = await page.$('button[type="submit"], input[type="submit"], button:has-text("Check"), button:has-text("Analyze"), button:has-text("Submit")');
      if (submitBtn) {
        console.log('Found submit button, clicking...');
        await submitBtn.click();
        
        // Wait for results
        await page.waitForTimeout(3000);
        
        // Take screenshot of results page
        await page.screenshot({ path: 'aeo-results.png', fullPage: true });
        console.log('Results screenshot saved as aeo-results.png');
        
        // Look specifically for "Query Results" section
        const queryResultsSection = await page.$('text=Query Results');
        if (queryResultsSection) {
          console.log('Found Query Results section, taking focused screenshot...');
          await queryResultsSection.screenshot({ path: 'query-results-section.png' });
          console.log('Query Results section screenshot saved as query-results-section.png');
        }
      }
    }
    
    // Take a final full page screenshot
    await page.screenshot({ path: 'final-page.png', fullPage: true });
    console.log('Final page screenshot saved as final-page.png');
    
  } catch (error) {
    console.error('Error:', error);
    await page.screenshot({ path: 'error-page.png', fullPage: true });
  } finally {
    await browser.close();
  }
})();