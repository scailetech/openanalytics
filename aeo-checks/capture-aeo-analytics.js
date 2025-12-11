const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();
  
  try {
    // Navigate directly to the AEO analytics page
    console.log('Navigating to AEO Analytics page...');
    await page.goto('http://localhost:3002/aeo-analytics');
    await page.waitForLoadState('networkidle');
    
    // Take screenshot of the page
    await page.screenshot({ path: 'aeo-analytics-page.png', fullPage: true });
    console.log('Screenshot saved: aeo-analytics-page.png');
    
    // Fill in the mentions check form
    console.log('Filling in the mentions check form...');
    
    // Add a sample OpenRouter key (you can replace with real one if available)
    const openrouterInput = await page.$('#openrouter-key');
    if (openrouterInput) {
      await openrouterInput.fill('sk-or-v1-sample-key-for-testing');
    }
    
    // Fill company name
    const companyInput = await page.$('#mentions-company');
    if (companyInput) {
      await companyInput.fill('SCAILE');
    }
    
    // Fill industry
    const industryInput = await page.$('#mentions-industry');
    if (industryInput) {
      await industryInput.fill('Generative Engine Optimization');
    }
    
    await page.waitForTimeout(1000);
    
    // Take screenshot after filling form
    await page.screenshot({ path: 'form-filled.png', fullPage: true });
    console.log('Screenshot saved: form-filled.png');
    
    // Click the "Check Mentions" button
    const checkMentionsBtn = await page.$('button:has-text("Check Mentions")');
    if (checkMentionsBtn) {
      console.log('Clicking Check Mentions button...');
      
      // Monitor network responses
      page.on('response', response => {
        const url = response.url();
        if (url.includes('mentions-check')) {
          console.log(`Mentions API Response: ${response.status()}`);
        }
      });
      
      await checkMentionsBtn.click();
      
      // Take screenshot of loading state
      await page.waitForTimeout(2000);
      await page.screenshot({ path: 'loading-mentions.png', fullPage: true });
      console.log('Screenshot saved: loading-mentions.png');
      
      // Wait for the API response (this might take 30-40 seconds based on logs)
      console.log('Waiting for mentions check to complete...');
      
      // Check periodically for results
      let resultsFound = false;
      for (let i = 0; i < 12; i++) { // Wait up to 60 seconds
        await page.waitForTimeout(5000);
        console.log(`Waiting... ${(i + 1) * 5} seconds elapsed`);
        
        // Check if results appeared by looking for the "Query Results" text
        const queryResultsText = await page.$('text=Query Results');
        if (queryResultsText) {
          console.log('Query Results section appeared!');
          resultsFound = true;
          break;
        }
        
        // Also check if any error occurred
        const errorMessage = await page.$('.text-destructive');
        if (errorMessage) {
          const errorText = await errorMessage.textContent();
          console.log('Error found:', errorText);
          break;
        }
      }
      
      // Take final screenshot
      await page.screenshot({ path: 'mentions-results-final.png', fullPage: true });
      console.log('Screenshot saved: mentions-results-final.png');
      
      if (resultsFound) {
        // Look specifically for the "Query Results (X)" element with formatting issues
        console.log('Looking for Query Results section with formatting issues...');
        
        const queryResultsElement = await page.$('h3:has-text("Query Results")');
        if (queryResultsElement) {
          // Take focused screenshot of the title
          await queryResultsElement.screenshot({ path: 'query-results-title.png' });
          console.log('Screenshot saved: query-results-title.png');
          
          // Get the styling information
          const titleInfo = await page.evaluate(() => {
            const titleEl = document.querySelector('h3:has-text("Query Results"), [class*="CardTitle"]:has-text("Query Results")');
            if (titleEl) {
              const style = window.getComputedStyle(titleEl);
              return {
                textAlign: style.textAlign,
                marginLeft: style.marginLeft,
                paddingLeft: style.paddingLeft,
                marginRight: style.marginRight,
                paddingRight: style.paddingRight,
                textContent: titleEl.textContent,
                className: titleEl.className,
                outerHTML: titleEl.outerHTML
              };
            }
            return null;
          });
          
          console.log('Query Results title styling:', titleInfo);
          
          // Take screenshot of the parent container to show context
          const parentContainer = await queryResultsElement.evaluateHandle(el => el.parentElement);
          if (parentContainer) {
            await parentContainer.screenshot({ path: 'query-results-container.png' });
            console.log('Screenshot saved: query-results-container.png');
          }
        }
      }
    } else {
      console.log('Check Mentions button not found');
    }
    
  } catch (error) {
    console.error('Error:', error);
    await page.screenshot({ path: 'error-aeo-analytics.png', fullPage: true });
  } finally {
    await browser.close();
  }
})();