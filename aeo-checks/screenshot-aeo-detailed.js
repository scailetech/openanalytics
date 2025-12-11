const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();
  
  try {
    console.log('Navigating to http://localhost:3002...');
    await page.goto('http://localhost:3002');
    await page.waitForLoadState('networkidle');
    
    // Take screenshot of homepage
    await page.screenshot({ path: 'homepage-detailed.png', fullPage: true });
    console.log('Homepage screenshot saved');
    
    // Navigate to auth page
    console.log('Clicking Sign In...');
    await page.click('a[href="/auth"]');
    await page.waitForLoadState('networkidle');
    
    // Take screenshot of auth page
    await page.screenshot({ path: 'auth-page.png', fullPage: true });
    console.log('Auth page screenshot saved');
    
    // Try to bypass auth if there's a demo mode or skip option
    const skipButtons = await page.$$eval('button', els => 
      els.filter(el => 
        el.textContent.toLowerCase().includes('demo') ||
        el.textContent.toLowerCase().includes('skip') ||
        el.textContent.toLowerCase().includes('guest') ||
        el.textContent.toLowerCase().includes('try')
      ).map(el => el.textContent)
    );
    
    console.log('Available auth bypass options:', skipButtons);
    
    // Check if there are any direct links to AEO tools
    const allLinks = await page.$$eval('a', els => 
      els.map(el => ({ text: el.textContent, href: el.href }))
        .filter(link => 
          link.text.toLowerCase().includes('aeo') ||
          link.text.toLowerCase().includes('check') ||
          link.text.toLowerCase().includes('mention') ||
          link.text.toLowerCase().includes('analysis')
        )
    );
    
    console.log('AEO-related links found:', allLinks);
    
    // Try direct navigation to common AEO tool paths
    const possiblePaths = [
      '/dashboard',
      '/aeo-check',
      '/mentions',
      '/analysis',
      '/tools',
      '/aeo-mentions',
      '/health-check'
    ];
    
    for (const path of possiblePaths) {
      try {
        console.log(`Trying direct navigation to ${path}...`);
        await page.goto(`http://localhost:3002${path}`);
        await page.waitForLoadState('networkidle', { timeout: 3000 });
        
        // Check if page loaded successfully (not redirected back to auth)
        const currentUrl = page.url();
        if (!currentUrl.includes('/auth') && !currentUrl.includes('404')) {
          console.log(`Successfully accessed ${path}`);
          
          // Take screenshot of this page
          await page.screenshot({ path: `${path.replace('/', '')}-page.png`, fullPage: true });
          
          // Look for Query Results section
          const queryResults = await page.$('text=Query Results');
          if (queryResults) {
            console.log('Found Query Results section!');
            
            // Take screenshot of the entire page with query results
            await page.screenshot({ path: 'query-results-full-page.png', fullPage: true });
            
            // Try to find the specific "Query Results (8)" element
            const queryResultsWithCount = await page.$('text=/Query Results.*\\(\\d+\\)/');
            if (queryResultsWithCount) {
              console.log('Found Query Results with count');
              
              // Take a focused screenshot of this section
              await queryResultsWithCount.screenshot({ path: 'query-results-section.png' });
              
              // Get the parent container to capture formatting issues
              const parentSection = await queryResultsWithCount.$('xpath=..');
              if (parentSection) {
                await parentSection.screenshot({ path: 'query-results-container.png' });
              }
            }
            
            // Look for any elements with formatting issues
            const formattingElements = await page.$$eval('*', els => 
              els.filter(el => {
                const style = window.getComputedStyle(el);
                return style.textAlign === 'left' || 
                       style.textAlign === 'right' || 
                       style.marginLeft || 
                       style.paddingLeft ||
                       el.classList.contains('text-left') ||
                       el.classList.contains('text-right') ||
                       el.classList.contains('ml-') ||
                       el.classList.contains('pl-');
              }).map(el => ({
                tagName: el.tagName,
                className: el.className,
                textContent: el.textContent.slice(0, 50)
              }))
            );
            
            console.log('Elements with potential alignment issues:', formattingElements.slice(0, 10));
            
            break;
          }
        }
      } catch (error) {
        console.log(`Path ${path} not accessible:`, error.message);
        continue;
      }
    }
    
    // Take final screenshot
    await page.screenshot({ path: 'final-state.png', fullPage: true });
    
  } catch (error) {
    console.error('Error:', error);
    await page.screenshot({ path: 'error-state.png', fullPage: true });
  } finally {
    await browser.close();
  }
})();