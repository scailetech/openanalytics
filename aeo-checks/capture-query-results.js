const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();
  
  try {
    console.log('Navigating to homepage...');
    await page.goto('http://localhost:3002');
    await page.waitForLoadState('networkidle');
    
    // Click Generate Keywords to open the interface
    console.log('Clicking Generate Keywords...');
    const generateBtn = await page.$('button:has-text("Generate Keywords")');
    if (generateBtn) {
      await generateBtn.click();
      await page.waitForTimeout(2000);
      
      // Take screenshot of the opened interface
      await page.screenshot({ path: 'keywords-interface.png', fullPage: true });
      
      // Look for any input fields in the form
      const companyInputSelectors = [
        'input[placeholder*="company" i]',
        'input[placeholder*="brand" i]',
        'input[placeholder*="business" i]',
        'input[name*="company" i]',
        'input[type="text"]',
        'input:not([type="hidden"]):not([type="submit"]):not([type="button"])',
        'textarea'
      ];
      
      let companyInput = null;
      for (const selector of companyInputSelectors) {
        companyInput = await page.$(selector);
        if (companyInput) {
          console.log(`Found input with selector: ${selector}`);
          break;
        }
      }
      
      if (!companyInput) {
        // Try to find any visible input
        const allInputs = await page.$$('input');
        for (const input of allInputs) {
          const isVisible = await input.isVisible();
          if (isVisible) {
            companyInput = input;
            console.log('Found visible input element');
            break;
          }
        }
      }
      
      if (companyInput) {
        console.log('Filling company input with SCAILE...');
        await companyInput.fill('SCAILE');
        await page.waitForTimeout(1000);
        
        // Look for submit/run button
        const submitSelectors = [
          'button[type="submit"]',
          'button:has-text("Run")',
          'button:has-text("Check")',
          'button:has-text("Generate")',
          'button:has-text("Start")',
          'button:has-text("Analyze")',
          'button:has-text("Search")',
          'form button'
        ];
        
        let submitBtn = null;
        for (const selector of submitSelectors) {
          submitBtn = await page.$(selector);
          if (submitBtn) {
            const isVisible = await submitBtn.isVisible();
            if (isVisible) {
              console.log(`Found submit button with selector: ${selector}`);
              break;
            }
          }
        }
        
        if (submitBtn) {
          console.log('Setting up API response monitoring...');
          
          // Monitor API responses
          page.on('response', response => {
            const url = response.url();
            if (url.includes('mentions-check') || url.includes('aeo') || url.includes('api')) {
              console.log(`API Response: ${url} - Status: ${response.status()}`);
            }
          });
          
          console.log('Clicking submit button...');
          await submitBtn.click();
          
          // Take screenshot immediately after clicking
          await page.waitForTimeout(2000);
          await page.screenshot({ path: 'after-submit.png', fullPage: true });
          
          // Wait for loading to complete (mentions check takes ~40 seconds based on logs)
          console.log('Waiting for analysis to complete...');
          for (let i = 0; i < 8; i++) {
            await page.waitForTimeout(5000);
            console.log(`Waiting... ${(i + 1) * 5} seconds elapsed`);
            
            // Check if results appeared
            const hasResults = await page.$('text=Query Results');
            if (hasResults) {
              console.log('Query Results section found!');
              break;
            }
          }
          
          // Take final screenshot
          await page.screenshot({ path: 'analysis-complete.png', fullPage: true });
          
          // Look specifically for Query Results section
          const queryResultsElement = await page.$('text=Query Results');
          if (queryResultsElement) {
            console.log('Found Query Results section!');
            
            // Take focused screenshot of Query Results
            await queryResultsElement.screenshot({ path: 'query-results-element.png' });
            
            // Get the parent container to see formatting
            const parentContainer = await queryResultsElement.evaluateHandle(el => {
              // Look for the containing section/div
              let parent = el.parentElement;
              while (parent && !parent.className.includes('section') && !parent.className.includes('container') && parent.tagName !== 'SECTION') {
                parent = parent.parentElement;
                if (!parent || parent === document.body) break;
              }
              return parent || el.parentElement;
            });
            
            if (parentContainer) {
              await parentContainer.screenshot({ path: 'query-results-container.png' });
            }
            
            // Get all text content around Query Results to see the formatting
            const contextText = await page.evaluate(() => {
              const queryEl = Array.from(document.querySelectorAll('*')).find(el => 
                el.textContent && el.textContent.includes('Query Results')
              );
              if (queryEl) {
                return {
                  element: queryEl.outerHTML.slice(0, 500),
                  textContent: queryEl.textContent,
                  computedStyle: window.getComputedStyle(queryEl),
                  parentHTML: queryEl.parentElement ? queryEl.parentElement.outerHTML.slice(0, 800) : null
                };
              }
              return null;
            });
            
            console.log('Query Results context:', contextText);
          }
          
          // Look for elements with counts like "(8)"
          const countElements = await page.$$eval('*', els => 
            els.filter(el => /\(\d+\)/.test(el.textContent))
              .map(el => ({
                text: el.textContent.trim().slice(0, 100),
                tagName: el.tagName,
                className: el.className,
                style: window.getComputedStyle(el).textAlign + ' | margin:' + window.getComputedStyle(el).marginLeft + ' | padding:' + window.getComputedStyle(el).paddingLeft
              }))
              .slice(0, 5)
          );
          console.log('Elements with counts (potential formatting issues):', countElements);
          
        } else {
          console.log('No submit button found');
          // List all visible buttons for debugging
          const allButtons = await page.$$eval('button', els => 
            els.filter(el => el.offsetParent !== null)
              .map(el => ({
                text: el.textContent.trim(),
                type: el.type,
                className: el.className.slice(0, 50)
              }))
          );
          console.log('All visible buttons:', allButtons);
        }
      } else {
        console.log('No input field found');
        // List all visible form elements for debugging
        const formElements = await page.$$eval('input, textarea, select', els => 
          els.filter(el => el.offsetParent !== null)
            .map(el => ({
              tagName: el.tagName,
              type: el.type,
              placeholder: el.placeholder,
              name: el.name,
              id: el.id
            }))
        );
        console.log('All visible form elements:', formElements);
      }
    }
    
  } catch (error) {
    console.error('Error:', error);
    await page.screenshot({ path: 'error-capture.png', fullPage: true });
  } finally {
    await browser.close();
  }
})();