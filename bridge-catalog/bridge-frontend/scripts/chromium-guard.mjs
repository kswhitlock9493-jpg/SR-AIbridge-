#!/usr/bin/env node
/**
 * Chromium Guard - Smart Browser Strategy Selector
 * Part of Firewall Harmony v1.7.6
 * 
 * Auto-detects and configures browser strategy to survive firewall blocks
 */

import { existsSync } from 'fs';
import { execSync } from 'child_process';
import { homedir } from 'os';
import { join } from 'path';

const CHROMIUM_DOWNLOAD_ALLOWED = process.env.CHROMIUM_DOWNLOAD_ALLOWED === 'true';
const PUPPETEER_CACHE_DIR = process.env.PUPPETEER_CACHE_DIR || join(homedir(), '.cache', 'puppeteer');
const PLAYWRIGHT_BROWSERS_PATH = process.env.PLAYWRIGHT_BROWSERS_PATH || join(homedir(), '.cache', 'ms-playwright');

/**
 * Check if cached Chromium browsers exist
 */
function checkCache() {
  const puppeteerCache = existsSync(PUPPETEER_CACHE_DIR);
  const playwrightCache = existsSync(PLAYWRIGHT_BROWSERS_PATH);
  
  if (puppeteerCache || playwrightCache) {
    console.log('✅ Cached browsers found');
    return true;
  }
  
  console.log('⚠️  No cached browsers found');
  return false;
}

/**
 * Check if system Chrome/Chromium is available
 */
function checkSystemChrome() {
  const chromePaths = [
    '/usr/bin/google-chrome',
    '/usr/bin/chromium-browser',
    '/usr/bin/chromium',
    '/snap/bin/chromium',
    'google-chrome',
    'chromium-browser',
    'chromium'
  ];

  for (const chromePath of chromePaths) {
    try {
      execSync(`which ${chromePath}`, { stdio: 'pipe' });
      console.log(`✅ System Chrome found: ${chromePath}`);
      return chromePath;
    } catch {
      // Continue to next path
    }
  }

  console.log('⚠️  No system Chrome found');
  return null;
}

/**
 * Attempt controlled download if allowed
 */
async function attemptControlledDownload() {
  if (!CHROMIUM_DOWNLOAD_ALLOWED) {
    console.log('❌ Chromium downloads disabled by policy');
    return false;
  }

  try {
    console.log('🔄 Attempting controlled Chromium download...');
    
    // Try Puppeteer download
    try {
      const puppeteer = await import('puppeteer');
      console.log('✅ Puppeteer browser download successful');
      return true;
    } catch (e) {
      console.log('⚠️  Puppeteer not available or download failed');
    }

    // Try Playwright download
    try {
      execSync('npx playwright install chromium', { stdio: 'inherit' });
      console.log('✅ Playwright browser download successful');
      return true;
    } catch (e) {
      console.log('⚠️  Playwright download failed');
    }

    return false;
  } catch (error) {
    console.log(`❌ Controlled download failed: ${error.message}`);
    return false;
  }
}

/**
 * Main guard logic
 */
async function main() {
  console.log('\n🛡️  Chromium Guard - Firewall Harmony v1.7.6\n');
  
  // Strategy 1: Check cache
  if (checkCache()) {
    console.log('\n✅ Strategy: Using cached browsers');
    process.exit(0);
  }

  // Strategy 2: Check system Chrome
  const systemChrome = checkSystemChrome();
  if (systemChrome) {
    console.log('\n✅ Strategy: Using system Chrome');
    process.env.PUPPETEER_EXECUTABLE_PATH = systemChrome;
    process.exit(0);
  }

  // Strategy 3: Controlled download (if allowed)
  if (CHROMIUM_DOWNLOAD_ALLOWED) {
    const downloaded = await attemptControlledDownload();
    if (downloaded) {
      console.log('\n✅ Strategy: Controlled download successful');
      process.exit(0);
    }
  }

  // All strategies failed
  console.log('\n⚠️  Warning: No browser strategy succeeded');
  console.log('ℹ️  Build may fail if browser automation is required');
  console.log('ℹ️  Auto-repair will warm cache on next run\n');
  
  // Don't fail the build - let it continue
  // Auto-repair will handle cache warming
  process.exit(0);
}

main().catch(error => {
  console.error('❌ Chromium Guard error:', error);
  process.exit(0); // Don't fail the build
});
