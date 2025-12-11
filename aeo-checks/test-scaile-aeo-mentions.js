const { chromium } = require('playwright');

async function testSCAILEAEOMentions() {
    console.log('🚀 Starting SCAILE AEO Mentions Test...\n');
    
    // Launch browser
    const browser = await chromium.launch({ 
        headless: false,
        devtools: true 
    });
    
    const context = await browser.newContext();
    const page = await context.newPage();
    
    // Capture console logs
    const consoleLogs = [];
    page.on('console', msg => {
        const logText = msg.text();
        consoleLogs.push(logText);
        
        // Print important logs in real-time
        if (logText.includes('[FALLBACK]') || 
            logText.includes('Generated pain points:') ||
            logText.includes('Generated use cases:') ||
            logText.includes('Geography-aware') ||
            logText.includes('hyperniche')) {
            console.log(`📝 CONSOLE LOG: ${logText}`);
        }
    });
    
    try {
        console.log('📍 Step 1: Navigating to http://localhost:3002/aeo-analytics');
        await page.goto('http://localhost:3002/aeo-analytics', { 
            waitUntil: 'networkidle',
            timeout: 60000 
        });
        
        // Wait for page to load and take a screenshot
        await page.waitForTimeout(2000);
        await page.screenshot({ 
            path: '/Users/federicodeponte/openanalytics/aeo-checks/test-step1-navigation.png',
            fullPage: true 
        });
        
        console.log('✅ Successfully navigated to AEO Analytics page');
        
        console.log('\n📍 Step 2: Entering "SCAILE" as company name');
        
        // Look for company name input field
        const companyInput = await page.locator('input[placeholder*="company" i], input[name*="company" i], input[id*="company" i]').first();
        
        if (await companyInput.count() > 0) {
            await companyInput.fill('SCAILE');
            console.log('✅ Entered "SCAILE" in company name field');
        } else {
            // Try alternative selectors
            const altSelectors = [
                'input[type="text"]',
                'input:not([type="submit"]):not([type="button"])',
                'input'
            ];
            
            let found = false;
            for (const selector of altSelectors) {
                const elements = await page.locator(selector).all();
                for (const element of elements) {
                    const placeholder = await element.getAttribute('placeholder') || '';
                    const label = await element.getAttribute('aria-label') || '';
                    
                    if (placeholder.toLowerCase().includes('company') || 
                        label.toLowerCase().includes('company') ||
                        placeholder.toLowerCase().includes('name')) {
                        await element.fill('SCAILE');
                        console.log('✅ Found and filled company input field');
                        found = true;
                        break;
                    }
                }
                if (found) break;
            }
            
            if (!found) {
                console.log('⚠️ Could not find company input field, trying first text input');
                const firstInput = await page.locator('input[type="text"]').first();
                if (await firstInput.count() > 0) {
                    await firstInput.fill('SCAILE');
                }
            }
        }
        
        await page.screenshot({ 
            path: '/Users/federicodeponte/openanalytics/aeo-checks/test-step2-company-filled.png',
            fullPage: true 
        });
        
        console.log('\n📍 Step 3: Running AEO mentions check');
        
        // Look for the run/submit button
        const runButton = await page.locator('button:has-text("Run"), button:has-text("Submit"), button:has-text("Check"), button:has-text("Analyze"), button[type="submit"]').first();
        
        if (await runButton.count() > 0) {
            await runButton.click();
            console.log('✅ Clicked AEO mentions run button');
        } else {
            console.log('⚠️ Could not find run button, trying form submission');
            await page.press('input', 'Enter');
        }
        
        await page.screenshot({ 
            path: '/Users/federicodeponte/openanalytics/aeo-checks/test-step3-after-submit.png',
            fullPage: true 
        });
        
        console.log('\n📍 Step 4: Waiting for processing and monitoring console logs...');
        
        // Wait for processing - look for loading indicators or results
        let processingComplete = false;
        let attempts = 0;
        const maxAttempts = 60; // 60 seconds
        
        while (!processingComplete && attempts < maxAttempts) {
            attempts++;
            
            // Check for loading indicators
            const loadingElements = await page.locator('*:has-text("loading"), *:has-text("processing"), .spinner, .loading').count();
            
            // Check for results or completion indicators
            const resultsElements = await page.locator('*:has-text("results"), *:has-text("complete"), *:has-text("generated"), *:has-text("queries")').count();
            
            // Check console logs for fallback indicators
            const hasFallbackLogs = consoleLogs.some(log => 
                log.includes('[FALLBACK]') || 
                log.includes('Generated pain points:') ||
                log.includes('Generated use cases:')
            );
            
            if (loadingElements === 0 && (resultsElements > 0 || hasFallbackLogs)) {
                processingComplete = true;
                console.log('✅ Processing appears to be complete');
            } else {
                await page.waitForTimeout(1000);
            }
            
            // Take periodic screenshots
            if (attempts % 10 === 0) {
                await page.screenshot({ 
                    path: `/Users/federicodeponte/openanalytics/aeo-checks/test-progress-${attempts}s.png`,
                    fullPage: true 
                });
                console.log(`⏱️ Still processing... ${attempts}s elapsed`);
            }
        }
        
        await page.screenshot({ 
            path: '/Users/federicodeponte/openanalytics/aeo-checks/test-step4-final-results.png',
            fullPage: true 
        });
        
        console.log('\n📍 Step 5: Analyzing console logs and results');
        
        // Filter and analyze console logs
        const fallbackLogs = consoleLogs.filter(log => 
            log.includes('[FALLBACK]') || 
            log.includes('Generated pain points:') ||
            log.includes('Generated use cases:') ||
            log.includes('Geography-aware') ||
            log.includes('hyperniche')
        );
        
        console.log('\n🔍 ANALYSIS RESULTS:');
        console.log('===================');
        
        if (fallbackLogs.length > 0) {
            console.log('\n✅ FALLBACK LOGIC DETECTED:');
            fallbackLogs.forEach((log, index) => {
                console.log(`${index + 1}. ${log}`);
            });
        } else {
            console.log('\n❌ NO FALLBACK LOGS FOUND');
            console.log('Looking for any geography or query-related logs...');
            
            const queryLogs = consoleLogs.filter(log => 
                log.toLowerCase().includes('query') ||
                log.toLowerCase().includes('geography') ||
                log.toLowerCase().includes('us') ||
                log.toLowerCase().includes('american') ||
                log.toLowerCase().includes('chatgpt') ||
                log.toLowerCase().includes('perplexity')
            );
            
            if (queryLogs.length > 0) {
                console.log('\nQuery-related logs found:');
                queryLogs.forEach((log, index) => {
                    console.log(`${index + 1}. ${log}`);
                });
            }
        }
        
        // Look for generated queries on the page
        console.log('\n📋 CHECKING PAGE CONTENT FOR GENERATED QUERIES:');
        
        const pageText = await page.textContent('body');
        const geographyPatterns = [
            /US companies?/gi,
            /American businesses?/gi,
            /ChatGPT.*US/gi,
            /Perplexity.*American/gi,
            /search rankings.*US/gi,
            /online visibility.*American/gi
        ];
        
        const foundGeographyQueries = [];
        geographyPatterns.forEach(pattern => {
            const matches = pageText.match(pattern);
            if (matches) {
                foundGeographyQueries.push(...matches);
            }
        });
        
        if (foundGeographyQueries.length > 0) {
            console.log('✅ GEOGRAPHY-AWARE QUERIES FOUND:');
            foundGeographyQueries.forEach((query, index) => {
                console.log(`${index + 1}. "${query}"`);
            });
        } else {
            console.log('❌ No geography-aware queries found in page content');
        }
        
        // Check for generic vs specific query patterns
        const genericPatterns = [
            /best software tools 2024/gi,
            /SCAILE vs alternatives/gi,
            /software comparison/gi
        ];
        
        const specificPatterns = [
            /improve search rankings.*ChatGPT/gi,
            /increase online visibility.*Perplexity/gi,
            /hyperniche/gi,
            /geography.aware/gi
        ];
        
        const foundGeneric = [];
        const foundSpecific = [];
        
        genericPatterns.forEach(pattern => {
            const matches = pageText.match(pattern);
            if (matches) foundGeneric.push(...matches);
        });
        
        specificPatterns.forEach(pattern => {
            const matches = pageText.match(pattern);
            if (matches) foundSpecific.push(...matches);
        });
        
        console.log('\n📊 QUERY ANALYSIS:');
        console.log(`Generic queries found: ${foundGeneric.length}`);
        console.log(`Specific queries found: ${foundSpecific.length}`);
        
        if (foundSpecific.length > foundGeneric.length) {
            console.log('✅ SUCCESS: More specific queries than generic ones detected');
        } else if (foundGeneric.length > 0) {
            console.log('⚠️ WARNING: Generic queries still detected');
            foundGeneric.forEach(query => console.log(`  - "${query}"`));
        }
        
        // Print all console logs for debugging
        console.log('\n📝 ALL CONSOLE LOGS:');
        console.log('===================');
        consoleLogs.forEach((log, index) => {
            console.log(`${index + 1}. ${log}`);
        });
        
        console.log('\n🎯 TEST SUMMARY:');
        console.log('================');
        console.log(`✓ Successfully navigated to AEO Analytics page`);
        console.log(`✓ Entered "SCAILE" as company name`);
        console.log(`✓ Initiated AEO mentions check`);
        console.log(`✓ Monitored processing for ${attempts} seconds`);
        console.log(`📊 Total console logs captured: ${consoleLogs.length}`);
        console.log(`🔄 Fallback logs detected: ${fallbackLogs.length}`);
        console.log(`🌍 Geography-aware queries found: ${foundGeographyQueries.length}`);
        console.log(`🎯 Specific queries vs Generic: ${foundSpecific.length} vs ${foundGeneric.length}`);
        
        const testPassed = fallbackLogs.length > 0 && foundGeographyQueries.length > 0;
        console.log(`\n🏆 OVERALL TEST RESULT: ${testPassed ? '✅ PASSED' : '❌ FAILED'}`);
        
        if (testPassed) {
            console.log('The enhanced geography-aware targeting is working correctly!');
        } else {
            console.log('The enhanced geography-aware targeting may need further investigation.');
        }
        
    } catch (error) {
        console.error('❌ Test failed with error:', error);
        await page.screenshot({ 
            path: '/Users/federicodeponte/openanalytics/aeo-checks/test-error.png',
            fullPage: true 
        });
    } finally {
        // Keep browser open for manual inspection
        console.log('\n🔍 Browser will remain open for manual inspection...');
        console.log('Press Ctrl+C to close when done.');
        
        // Wait indefinitely until user closes
        await page.waitForTimeout(300000); // 5 minutes max
        await browser.close();
    }
}

// Run the test
testSCAILEAEOMentions().catch(console.error);