const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();
  
  try {
    console.log('Navigating to homepage...');
    await page.goto('http://localhost:3002');
    await page.waitForLoadState('networkidle');
    
    // Look for any forms or interfaces that might trigger an AEO check
    console.log('Looking for AEO check interfaces...');
    
    // Check if there are any input fields that might be for entering company names or URLs
    const inputs = await page.$$eval('input', els => 
      els.map(el => ({ 
        type: el.type, 
        placeholder: el.placeholder, 
        name: el.name, 
        id: el.id,
        className: el.className
      }))
    );
    console.log('All inputs found:', inputs);
    
    // Look for buttons that might trigger AEO analysis
    const buttons = await page.$$eval('button', els => 
      els.map(el => ({ 
        text: el.textContent.trim(), 
        className: el.className,
        id: el.id
      })).filter(btn => btn.text.length > 0)
    );
    console.log('All buttons found:', buttons);
    
    // Try to find any interface that mentions "Generate Keywords", "AEO", "mentions", etc.
    const aeoButtons = buttons.filter(btn => 
      btn.text.toLowerCase().includes('generate') ||
      btn.text.toLowerCase().includes('keyword') ||
      btn.text.toLowerCase().includes('aeo') ||
      btn.text.toLowerCase().includes('check') ||
      btn.text.toLowerCase().includes('analyze')
    );
    console.log('AEO-related buttons:', aeoButtons);
    
    // Try clicking the "Generate Keywords" button if it exists
    const generateKeywordsBtn = await page.$('button:has-text("Generate Keywords")');
    if (generateKeywordsBtn) {
      console.log('Found Generate Keywords button, clicking it...');
      await generateKeywordsBtn.click();
      await page.waitForTimeout(2000);
      
      // Take screenshot after clicking
      await page.screenshot({ path: 'after-generate-click.png', fullPage: true });
      
      // Look for any forms or inputs that appear
      const newInputs = await page.$$eval('input', els => 
        els.map(el => ({ 
          type: el.type, 
          placeholder: el.placeholder, 
          name: el.name,
          visible: el.offsetParent !== null
        })).filter(input => input.visible)
      );
      console.log('Visible inputs after clicking Generate Keywords:', newInputs);
      
      // Try entering a company name
      const companyInput = await page.$('input[placeholder*="company" i], input[placeholder*="brand" i], input[placeholder*="business" i], input[name*="company" i]');
      if (companyInput) {
        console.log('Found company input, entering SCAILE...');
        await companyInput.fill('SCAILE');
        
        // Look for submit button
        const submitBtn = await page.$('button[type="submit"], button:has-text("Check"), button:has-text("Generate"), button:has-text("Run"), button:has-text("Start")');
        if (submitBtn) {
          console.log('Found submit button, clicking and waiting for results...');
          
          // Set up response listener to catch API calls
          page.on('response', response => {
            if (response.url().includes('mentions-check') || response.url().includes('aeo')) {
              console.log(`API Response: ${response.url()} - Status: ${response.status()}`);
            }
          });
          
          await submitBtn.click();
          
          // Wait for results to load
          console.log('Waiting for results...');
          await page.waitForTimeout(5000);
          
          // Take screenshot of loading state
          await page.screenshot({ path: 'loading-results.png', fullPage: true });
          
          // Wait longer for the API to complete (we saw it takes ~38 seconds from logs)
          console.log('Waiting for API to complete (this may take up to 40 seconds)...');
          await page.waitForTimeout(40000);
          
          // Take screenshot of final results
          await page.screenshot({ path: 'final-results.png', fullPage: true });
          
          // Look specifically for "Query Results" section
          const queryResults = await page.$('text=Query Results');
          if (queryResults) {
            console.log('Found Query Results section!');
            await queryResults.screenshot({ path: 'query-results-found.png' });
            
            // Get the parent container
            const parentElement = await queryResults.evaluateHandle(el => el.parentElement);
            if (parentElement) {
              await parentElement.screenshot({ path: 'query-results-parent.png' });
            }
          }
          
          // Look for any element that contains "(8)" or similar count
          const countElements = await page.$$eval('*', els => 
            els.filter(el => /\(\d+\)/.test(el.textContent))
              .map(el => ({
                text: el.textContent.trim(),
                tagName: el.tagName,
                className: el.className
              }))
              .slice(0, 10)
          );
          console.log('Elements with counts found:', countElements);
          
          // Look for any alignment issues
          const alignmentElements = await page.$$eval('*', els => 
            els.filter(el => {
              const style = window.getComputedStyle(el);
              return el.textContent.includes('Query Results') && (
                style.textAlign !== 'center' ||
                style.marginLeft !== '0px' ||
                parseFloat(style.paddingLeft) > 0
              );
            }).map(el => ({
              text: el.textContent.slice(0, 100),
              textAlign: window.getComputedStyle(el).textAlign,
              marginLeft: window.getComputedStyle(el).marginLeft,
              paddingLeft: window.getComputedStyle(el).paddingLeft
            }))
          );
          console.log('Elements with potential alignment issues:', alignmentElements);
        }
      }
    }
    
  } catch (error) {
    console.error('Error:', error);
    await page.screenshot({ path: 'error-finding-interface.png', fullPage: true });
  } finally {
    await browser.close();
  }
})();