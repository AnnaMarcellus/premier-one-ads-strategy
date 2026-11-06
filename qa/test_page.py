"""Run with installed Playwright Chromium. Evidence defaults to Hermes scratch."""
from pathlib import Path
import json, math, os, re
from datetime import datetime, timezone
from playwright.sync_api import sync_playwright
import fitz

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = Path.home() / 'AppData/Local/hermes/cache/scratch/premier-one-corrective-audit'
EVIDENCE.mkdir(parents=True, exist_ok=True)
checks = []
def check(name, passed, detail=None):
    checks.append({'name': name, 'passed': bool(passed), 'detail': detail})

def load_capture(path):
    text = path.read_text(encoding='utf-8')
    return json.loads(text[text.index('{'):text.rindex('}') + 1])

source = load_capture(ROOT.parent / 'google_ads_kp_demolition_rows.json')
rows = [r for r in source['rows'] if len(r) > 1]
excav = load_capture(ROOT.parent / 'google_ads_kp_excavation_rows.json')
errors = []
with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={'width':1440,'height':1000}, device_scale_factor=1)
    page.on('pageerror', lambda error: errors.append(str(error)))
    page.goto((ROOT / 'index.html').as_uri(), wait_until='load')
    displayed = page.locator('.keyword-table tbody tr').evaluate_all('(rows)=>rows.map(r=>Array.from(r.cells).map(c=>c.textContent.trim()))')
    expected = [[r[0],r[1],r[2],r[3], 'Unavailable' if r[4] == '\u2014' else r[4], 'Unavailable / unavailable'] for r in rows]
    check('exact nine keyword rows, competition, changes and unavailable bids', displayed == expected, {'observed_count': len(displayed),'expected_count':len(expected)})
    check('excavation source repeats all demolition keywords', all(r[0] in excav['text'] for r in rows))
    body = page.locator('body').inner_text()
    forbidden = ['620+', '$10.80', '$11.20', '$24.80', 'Threlkeld', 'Eastern Land Solutions', '864', 'zero budget waste', '30-second', '5-story', '\u2014']
    check('unsupported legacy claims and private phone removed', not any(term in body for term in forbidden))
    check('noindex retained', 'noindex' in page.locator('meta[name="robots"]').get_attribute('content'))
    check('official definition linked', page.locator('#source-link').get_attribute('href') == 'https://support.google.com/google-ads/answer/3022575')
    check('all calculator inputs have accessible labels', page.locator('.controls input').evaluate_all('(els)=>els.every(e=>e.labels.length>0)'))
    def expected_scenario(budget,cpc=12,low=10,high=15):
        actual=page.evaluate('window.lastScenario')
        expected={'clicks':budget/cpc,'leadsLow':budget/cpc*low/100,'leadsHigh':budget/cpc*high/100,'cplBest':None if high==0 else cpc/(high/100),'cplWorst':None if low==0 else cpc/(low/100)}
        return all(actual[k] is None if v is None else math.isclose(actual[k],v,rel_tol=1e-12,abs_tol=1e-12) for k,v in expected.items()),actual
    passed,actual=expected_scenario(1500)
    check('calculator renders on initial load from unrounded math', passed,actual)
    check('initial rendered labels', page.locator('#clicks').inner_text()=='125.00' and page.locator('#leads').inner_text()=='12.50 to 18.75' and page.locator('#cpl').inner_text()=='$80.00 to $120.00')
    for budget in (2500,1500):
        page.locator(f'[data-budget="{budget}"]').click()
        passed,actual=expected_scenario(budget)
        check(f'{budget} preset math and fixed CPC', passed and page.locator('#cpc').input_value()=='12',actual)
    page.locator('#rate-low').fill('0');page.locator('#rate-high').fill('0')
    passed,actual=expected_scenario(1500,low=0,high=0)
    check('zero conversion: zero leads and undefined CPL, no Infinity', passed and 'Undefined' in page.locator('#cpl').inner_text() and 'Infinity' not in page.locator('#cpl').inner_text(),actual)
    page.locator('#rate-high').fill('15')
    check('one-sided zero conversion safely represented', 'Undefined' in page.locator('#cpl').inner_text() and '$80.00' in page.locator('#cpl').inner_text())
    page.locator('#rate-low').fill('10');page.locator('#cpc').fill('0')
    check('invalid zero CPC shows inline error and hides stale output', page.locator('#calc-error').inner_text()!='' and page.locator('#calc-output').is_hidden())
    page.locator('#cpc').fill('')
    check('empty input rejected', page.locator('#calc-output').is_hidden())
    page.locator('#cpc').fill('12');page.locator('#rate-low').fill('20')
    check('reversed conversion range rejected', page.locator('#calc-output').is_hidden())
    page.locator('#rate-low').fill('10');page.locator('#budget').fill('0')
    check('zero budget produces zero clicks and leads', page.evaluate('lastScenario.clicks===0 && lastScenario.leadsHigh===0'))
    page.locator('[data-budget="1500"]').click()
    page.locator('#cpc').fill('13.37');page.locator('#rate-low').fill('11.2');page.locator('#rate-high').fill('14.6')
    passed,actual=expected_scenario(1500,13.37,11.2,14.6)
    check('fractional assumptions preserve unrounded intermediate math',passed,actual)
    page.locator('#cpc').fill('12');page.locator('#rate-low').fill('10');page.locator('#rate-high').fill('15')
    page.locator('[data-budget="2500"]').focus();page.keyboard.press('Enter')
    check('keyboard activates preset and visible focus style',page.locator('#budget').input_value()=='2500' and page.locator('[data-budget="2500"]').evaluate('(e)=>getComputedStyle(e).outlineStyle')!='none')
    page.locator('[data-budget="1500"]').click()
    check('no hidden data tabs or disclosures',page.locator('[role="tab"],details').count()==0,'All report sections always visible; no tab or disclosure interaction applicable.')
    for width in (320,375,768,1440):
        page.set_viewport_size({'width':width,'height':900})
        dimensions=page.evaluate('({width:innerWidth,document:document.documentElement.scrollWidth,nav:document.querySelector(".top-nav").getBoundingClientRect().width})')
        nav_overflow=page.locator('.nav-links').evaluate('(el)=>el.scrollWidth > el.clientWidth+1')
        check(f'no document or nav overflow at {width}px',dimensions['document']<=width and not nav_overflow,dimensions)
        page.locator('nav a[href="#services"]').click()
        check(f'navigation to services works at {width}px',page.evaluate('location.hash')=='#services')
        page.evaluate('window.scrollTo(0,0)')
        page.screenshot(path=str(EVIDENCE/f'page-{width}.png'),full_page=True)
    page.set_viewport_size({'width':1440,'height':1000})
    page.emulate_media(media='print')
    print_styles=page.locator('main').evaluate('(main)=>Array.from(main.querySelectorAll("h1,h2,h3,p,td,th,li,dt,dd")).map(e=>({color:getComputedStyle(e).color,display:getComputedStyle(e).display})).filter(x=>x.color!=="rgb(17, 17, 17)" && x.color!=="rgb(34, 34, 34)")')
    check('print text colors dark and legible',len(print_styles)==0,print_styles[:5])
    pdf_path=EVIDENCE/'research-brief-print.pdf'
    page.pdf(path=str(pdf_path),format='A4',print_background=True,prefer_css_page_size=True)
    doc=fitz.open(pdf_path)
    text='\n'.join(pg.get_text() for pg in doc)
    required=[page.locator('h2').nth(i).inner_text() for i in range(page.locator('h2').count())]+[r[0] for r in rows]+['Forestry mulching','Selective and interior demolition','$2,500','Undefined','Before any capped test']
    # Undefined is a zero-conversion explanation in the formula, case-insensitive.
    normalized_text = re.sub(r'\s+', ' ', text).lower()
    missing=[term for term in required if term.lower() not in normalized_text]
    check('PDF includes every report section, nine keywords, both service lists and scenarios',not missing,{'pages':len(doc),'missing':missing,'characters':len(text)})
    offpage=[]
    for i,pg in enumerate(doc):
        for word in pg.get_text('words'):
            if word[0]<0 or word[1]<0 or word[2]>pg.rect.width+1 or word[3]>pg.rect.height+1:offpage.append({'page':i+1,'word':word[4]})
    check('PDF text stays inside page bounds',not offpage,offpage)
    doc[0].get_pixmap(matrix=fitz.Matrix(1.5,1.5)).save(str(EVIDENCE/'print-first-page.png'))
    (EVIDENCE/'print-text.txt').write_text(text,encoding='utf-8')
    check('no browser JavaScript errors',not errors,errors)
    browser_version=browser.version
    browser.close()
result={'timestamp_utc':datetime.now(timezone.utc).isoformat(),'browser':'Chromium '+browser_version,'url':(ROOT/'index.html').as_uri(),'checks':checks,'passed':sum(c['passed'] for c in checks),'failed':sum(not c['passed'] for c in checks),'evidence_dir':str(EVIDENCE),'artifacts':[str(x) for x in EVIDENCE.iterdir()]}
(ROOT/'qa/test-results.json').write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding='utf-8')
print(json.dumps(result,indent=2,ensure_ascii=False))
raise SystemExit(1 if result['failed'] else 0)
