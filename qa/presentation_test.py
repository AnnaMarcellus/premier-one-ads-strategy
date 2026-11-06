"""Brian-facing presentation acceptance tests. Run: python qa/presentation_test.py"""
from pathlib import Path
import json
import math
import re
from datetime import datetime, timezone
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = Path.home() / 'AppData/Local/hermes/cache/scratch/premier-one-presentation'
EVIDENCE.mkdir(parents=True, exist_ok=True)
RESULTS = ROOT / 'qa/presentation-results.json'
checks = []
errors = []
screenshots = []

def check(name, condition, detail=None):
    checks.append({'name': name, 'passed': bool(condition), 'detail': detail})
    if not condition:
        raise AssertionError(f'{name}: {detail}')

def approximately(a, b):
    return math.isclose(a, b, rel_tol=1e-12, abs_tol=1e-12)

def main():
    source = json.loads((ROOT / 'research/keyword_planner_presentation_data.json').read_text(encoding='utf-8'))
    competitors = (ROOT / 'research/competitors.md').read_text(encoding='utf-8')
    report = {'tested_at_utc': datetime.now(timezone.utc).isoformat(), 'target': str(ROOT / 'index.html'), 'checks': checks, 'javascript_errors': errors, 'screenshots': screenshots, 'status': 'failed'}
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            report['browser'] = {'engine': 'Chromium', 'version': browser.version, 'executable': p.chromium.executable_path}
            page = browser.new_page(viewport={'width': 1440, 'height': 1000}, device_scale_factor=1)
            page.on('pageerror', lambda e: errors.append(str(e)))
            page.on('console', lambda msg: errors.append(msg.text) if msg.type == 'error' else None)
            page.goto((ROOT / 'index.html').as_uri(), wait_until='load')
            check('title', page.title() == 'Premier One Google Ads Plan | Greenville, SC')
            check('single h1', page.locator('h1').count() == 1)
            body = page.locator('body').inner_text()
            for bad in ['internal review', 'pending research', 'earlier page', 'previous errors', 'capture file', 'Print / PDF', '30-40', '$1,500', '$2,500', '$5,000']:
                check('removed internal or over-budget text: ' + bad, bad.lower() not in body.lower())
            check('no private/raw research links', page.locator('a[href*="research/"],a[href^="tel:"],a[href*="ads.google.com/aw/"]').count() == 0)
            expected_counts = source['settings']['export_counts']
            check('source counts agree', expected_counts['total_rows_with_batch_duplicates'] == 2574 and expected_counts['unique_keyword_strings'] == 2510 and source['selected_rows_count'] == 41)
            note = page.locator('#research-note').inner_text()
            check('county source and radius distinction', all(v in note for v in ['Greenville County', 'October 2025–September 2026', 'English', 'Google network', 'USD', '2,574', '2,510', '41', 'not estimates for the proposed 60-mile radius']))
            dom_rows = page.locator('tr[data-keyword]').evaluate_all('(rows)=>rows.map(r=>({keyword:r.dataset.keyword,cells:Array.from(r.cells,c=>c.textContent.trim())}))')
            expected = {r['Keyword']: r for r in source['selected_rows']}
            check('all 41 exact keywords and no duplicates', len(dom_rows) == len(expected) == 41 and {r['keyword'] for r in dom_rows} == set(expected))
            def bid(v):
                return 'N/A' if v is None else f'${v:.2f}'
            for r in dom_rows:
                s = expected[r['keyword']]
                cells = [s['Keyword'], str(s['avg_monthly_searches']), s['Competition'], bid(s['bid_low_usd']) + ' / ' + bid(s['bid_high_usd'])]
                check('source metrics: ' + r['keyword'], r['cells'] == cells, r['cells'])
            check('19 core rows visible', page.locator('tr[data-keyword]:visible').count() == 19)
            check('22 additional rows collapsed', not page.locator('#keyword-details').evaluate('(e)=>e.open') and page.locator('#keyword-details tr[data-keyword]').count() == 22)
            page.locator('#keyword-details summary').focus()
            page.keyboard.press('Enter')
            check('keyboard details opens all 41', page.locator('tr[data-keyword]:visible').count() == 41)
            page.keyboard.press('Space')
            check('keyboard details closes', not page.locator('#keyword-details').evaluate('(e)=>e.open'))
            for url in ['https://threlkelddemolitionllc.com/greenville-sc/', 'https://upstatedemolition.com/', 'https://rocksolidearthworks.net/']:
                check('competitor link agrees with research: ' + url, url in competitors and page.locator(f'#competitors a[href="{url}"]').count() == 1)
            check('competitor positioning caveat', 'not verified ad creatives' in page.locator('#competitors').inner_text() and 'activity is unconfirmed' in page.locator('#competitors').inner_text())
            budget_copy = page.locator('#budget').inner_text()
            check('total ceiling includes approved fees/tools', 'Deduct any agreed fees or tools before allocating spend' in budget_copy and 'within the ceiling' in budget_copy and 'authorizes no spending' in budget_copy)
            check('daily arithmetic', round(32.89 * 30.4, 2) == 999.86 and '$999.86' in budget_copy)
            fixed = page.locator('#scenario-table tbody tr').evaluate_all('(rows)=>rows.map(r=>({cpc:Number(r.dataset.cpc),cells:Array.from(r.cells,c=>c.textContent.trim())}))')
            check('three fixed CPC scenarios', [r['cpc'] for r in fixed] == [10,15,20])
            for row in fixed:
                c = row['cpc']
                want = [f'${c:.2f}', f'{1000/c:.2f}', f'{1000/c*.1:.2f}–{1000/c*.15:.2f}', f'${c/.15:.2f}–${c/.1:.2f}']
                check('fixed scenario arithmetic ' + str(c), row['cells'] == want, row['cells'])
            check('budget HTML max', page.locator('#budget-input').get_attribute('max') == '1000')
            for b,c in [(1000,10),(1000,15),(1000,20),(750,12),(0,15),(1000,.01)]:
                page.locator('#budget-input').fill(str(b))
                page.locator('#cpc-input').fill(str(c))
                actual = page.evaluate('window.lastScenario')
                expected_values = {'clicks': b/c, 'leadsLow': b/c*.1, 'leadsHigh': b/c*.15, 'cplBest': c/.15 if b else None, 'cplWorst': c/.1 if b else None}
                check(f'interactive unrounded arithmetic budget={b} CPC={c}', actual is not None and all(actual[k] is None if v is None else approximately(actual[k],v) for k,v in expected_values.items()), actual)
            for field,value in [('budget-input','1000.01'),('budget-input','5000'),('budget-input','-1'),('budget-input',''),('cpc-input','0'),('cpc-input','-10'),('cpc-input','')]:
                page.locator('#budget-input').fill('1000')
                page.locator('#cpc-input').fill('15')
                page.locator('#'+field).fill(value)
                check(f'invalid input rejected {field}={value}', page.evaluate('window.lastScenario') is None and page.locator('#calc-output').is_hidden() and bool(page.locator('#calc-error').inner_text()))
            page.locator('#budget-input').fill('1000')
            page.locator('#cpc-input').fill('15')
            for width in [320,375,768,1440]:
                page.set_viewport_size({'width':width,'height':1000})
                page.evaluate('window.scrollTo(0,0)')
                check(f'no page overflow at {width}px collapsed', page.evaluate('document.documentElement.scrollWidth<=innerWidth'))
                page.locator('#keyword-details').evaluate('(e)=>e.open=true')
                check(f'no page overflow at {width}px expanded', page.evaluate('document.documentElement.scrollWidth<=innerWidth'))
                if width < 768:
                    scrollable = page.locator('.table-wrap').first.evaluate('(e)=>{e.scrollLeft=150;return e.scrollLeft>0}')
                    check(f'tables scroll independently at {width}px', scrollable)
                page.locator('#keyword-details').evaluate('(e)=>e.open=false')
                page.locator('.table-wrap').evaluate_all('(els)=>els.forEach(e=>e.scrollLeft=0)')
                if width in [375,1440]:
                    page.evaluate('window.scrollTo(0,0)')
                    shot = EVIDENCE / f'presentation-{width}.png'
                    page.screenshot(path=str(shot), full_page=True)
                    screenshots.append(str(shot))
                    shot = EVIDENCE / f'presentation-hero-{width}.png'
                    page.screenshot(path=str(shot), full_page=False)
                    screenshots.append(str(shot))
                    page.locator('#budget').scroll_into_view_if_needed()
                    page.wait_for_timeout(250)
                    shot = EVIDENCE / f'presentation-budget-{width}.png'
                    page.screenshot(path=str(shot), full_page=False)
                    screenshots.append(str(shot))
            check('all internal anchors resolve', page.locator('a[href^="#"]').evaluate_all('(links)=>links.every(a=>document.getElementById(a.getAttribute("href").slice(1)))'))
            check('no JavaScript or console errors', not errors, errors)
            nojs = browser.new_context(java_script_enabled=False, viewport={'width':375,'height':900})
            fallback = nojs.new_page()
            fallback.goto((ROOT / 'index.html').as_uri())
            check('no-JS readable scenarios and native details', fallback.locator('#scenario-table tbody tr').count() == 3 and fallback.locator('noscript').is_visible())
            fallback.locator('#keyword-details summary').click()
            check('no-JS details works', fallback.locator('tr[data-keyword]:visible').count() == 41)
            nojs.close()
            browser.close()
        report['status'] = 'passed'
    except Exception as exc:
        report['failure'] = str(exc)
        raise
    finally:
        report['checks_passed'] = sum(c['passed'] for c in checks)
        report['checks_total'] = len(checks)
        RESULTS.write_text(json.dumps(report, indent=2), encoding='utf-8')
        print(json.dumps({'status':report['status'],'passed':report['checks_passed'],'total':report['checks_total'],'results':str(RESULTS),'screenshots':screenshots},indent=2))

if __name__ == '__main__':
    main()
