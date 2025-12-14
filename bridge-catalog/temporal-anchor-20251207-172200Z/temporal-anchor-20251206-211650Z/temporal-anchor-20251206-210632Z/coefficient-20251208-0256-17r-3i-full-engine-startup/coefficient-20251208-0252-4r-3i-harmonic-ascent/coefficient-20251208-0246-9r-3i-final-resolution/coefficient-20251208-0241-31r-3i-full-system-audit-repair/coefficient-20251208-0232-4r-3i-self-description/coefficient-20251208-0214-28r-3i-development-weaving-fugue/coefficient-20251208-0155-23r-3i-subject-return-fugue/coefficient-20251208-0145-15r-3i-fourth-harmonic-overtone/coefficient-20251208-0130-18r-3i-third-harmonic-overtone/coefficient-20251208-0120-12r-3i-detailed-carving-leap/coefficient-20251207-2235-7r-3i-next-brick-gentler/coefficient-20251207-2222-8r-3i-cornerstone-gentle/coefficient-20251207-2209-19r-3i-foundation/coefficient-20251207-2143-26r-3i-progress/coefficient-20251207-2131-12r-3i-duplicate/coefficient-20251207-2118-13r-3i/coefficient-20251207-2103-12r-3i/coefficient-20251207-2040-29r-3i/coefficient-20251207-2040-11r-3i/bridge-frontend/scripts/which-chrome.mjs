#!/usr/bin/env node
/**
 * Which Chrome - Chrome/Chromium Location Detector
 * Part of Firewall Harmony v1.7.6
 * 
 * Detects available Chrome/Chromium installations
 */

import { execSync } from 'child_process';

/**
 * Find all available Chrome/Chromium installations
 */
function findChromeInstallations() {
  const chromePaths = [
    '/usr/bin/google-chrome',
    '/usr/bin/chromium-browser',
    '/usr/bin/chromium',
    '/snap/bin/chromium',
    '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    '/Applications/Chromium.app/Contents/MacOS/Chromium'
  ];

  const found = [];

  console.log('🔍 Searching for Chrome/Chromium installations...\n');

  for (const chromePath of chromePaths) {
    try {
      execSync(`test -f "${chromePath}" || which ${chromePath.split('/').pop()}`, { stdio: 'pipe' });
      
      // Try to get version
      try {
        const version = execSync(`"${chromePath}" --version`, { stdio: 'pipe', encoding: 'utf8' }).trim();
        found.push({ path: chromePath, version });
        console.log(`✅ Found: ${chromePath}`);
        console.log(`   Version: ${version}\n`);
      } catch {
        found.push({ path: chromePath, version: 'Unknown' });
        console.log(`✅ Found: ${chromePath}`);
        console.log(`   Version: Unknown\n`);
      }
    } catch {
      // Not found, continue
    }
  }

  return found;
}

/**
 * Main function
 */
function main() {
  console.log('\n🌐 Chrome/Chromium Location Detector\n');
  console.log('=' .repeat(50) + '\n');

  const installations = findChromeInstallations();

  if (installations.length === 0) {
    console.log('❌ No Chrome/Chromium installations found\n');
    console.log('💡 Tip: Install Chrome or Chromium:');
    console.log('   Ubuntu/Debian: sudo apt install chromium-browser');
    console.log('   macOS: brew install --cask google-chrome\n');
    process.exit(1);
  }

  console.log('=' .repeat(50));
  console.log(`\n✅ Found ${installations.length} installation(s)\n`);
  console.log('📋 Summary:\n');
  
  installations.forEach((inst, idx) => {
    console.log(`${idx + 1}. ${inst.path}`);
    console.log(`   ${inst.version}\n`);
  });

  // Output as JSON for scripting
  if (process.argv.includes('--json')) {
    console.log('\n📄 JSON Output:\n');
    console.log(JSON.stringify(installations, null, 2));
  }

  process.exit(0);
}

main();
