"""DOM text bounds and readable contrast are checked before any output is accepted."""


def luminance(color: str) -> float:
    components = [int(color[i:i+2], 16) / 255 for i in (1, 3, 5)]
    linear = [v / 12.92 if v <= .04045 else ((v + .055) / 1.055) ** 2.4 for v in components]
    return .2126 * linear[0] + .7152 * linear[1] + .0722 * linear[2]


def contrast(a: str, b: str) -> float:
    left, right = sorted([luminance(a), luminance(b)])
    return (right + .05) / (left + .05)


def safe_palette(preset: list[str], colors: list[str], forbidden: list[str]) -> list[str]:
    bg = colors[0] if colors else preset[0]
    fg = preset[1]
    accent = colors[1] if len(colors) > 1 else preset[2]
    if contrast(bg, fg) < 4.5 or fg in forbidden:
        options = [c for c in ["#111111", "#ffffff", "#18392d", "#f8faf7"] if c not in forbidden]
        if not options:
            raise ValueError("No readable foreground satisfies brand constraints")
        fg = max(options, key=lambda c: contrast(bg, c))
    if accent in forbidden:
        accent = fg
    if bg in forbidden or contrast(bg, fg) < 4.5:
        raise ValueError("Palette conflicts with brand constraints or minimum contrast")
    return [bg, fg, accent]


FIT_SCRIPT = """() => {
  const sheet=document.querySelector('.sheet');
  const items=[...document.querySelectorAll('[data-fit]')];
  const title=sheet.querySelector('h1');
  const style=getComputedStyle(title), canvas=document.createElement('canvas');
  const context=canvas.getContext('2d');
  context.font=style.font;
  const titleMetrics=context.measureText(title.textContent);
  // CJK fallback fonts can have taller ascent/descent than the authored leading.
  // Reserve their actual font box before fitting, including inline word spans.
  const fontBox=titleMetrics.fontBoundingBoxAscent+titleMetrics.fontBoundingBoxDescent;
  const fontSize=parseFloat(style.fontSize);
  if(Number.isFinite(fontBox)&&fontBox+2>parseFloat(style.lineHeight)){
    title.style.lineHeight=String((fontBox+2)/fontSize);
  }
  const naturalWidth=titleMetrics.width;
  const density=naturalWidth/Math.max(1,title.clientWidth);
  sheet.dataset.titleLayout=density<=1.2?'display':density<=3?'balanced':'compact';
  if(density>3){
    sheet.classList.add('title-dense');
  }
  // Narrow display columns yield sooner, keeping medium CJK phrases together.
  if(density>2.2&&sheet.classList.contains('portrait')&&(sheet.classList.contains('swiss-grid')||sheet.classList.contains('sports-dynamic'))){
    sheet.classList.add('title-expanded');sheet.dataset.titleLayout='expanded';
  }
  // Keep short script runs together when they fit: AI Agent / 实战分享会.
  // Long phrases retain natural wrapping; user text is inserted only as text nodes.
  const tokens=title.textContent.split(/([\\p{Script=Han}]+|[A-Za-z0-9]+(?: +[A-Za-z0-9]+)*)/u);
  title.replaceChildren();
  for(const token of tokens){
    if(!token)continue;
    const tracking=parseFloat(style.letterSpacing)||0;
    if(/^[\\p{Script=Han}A-Za-z0-9]/u.test(token)&&context.measureText(token).width+tracking*token.length<=title.clientWidth-2){
      const word=document.createElement('span');word.className='title-word';word.textContent=token;title.append(word);
    }else title.append(document.createTextNode(token));
  }
  function overflowing(){return sheet.scrollHeight>sheet.clientHeight+1 || sheet.scrollWidth>sheet.clientWidth+1}
  for(let round=0;round<110;round++){
    let changed=false;
    if(overflowing()){
      const visual=sheet.querySelector('.visual');
      // Intrinsic SVG sizes must yield to the content; no factual text is removed.
      if(visual&&getComputedStyle(sheet).gridTemplateColumns.split(' ').length===1){
        visual.style.minHeight='0px';
        visual.querySelectorAll('svg').forEach(e=>e.style.maxHeight='80px');
      }
    }
    for(const el of items){
      if(getComputedStyle(el).display==='none'||!el.getClientRects().length)continue;
      const size=parseFloat(getComputedStyle(el).fontSize), min=+el.dataset.fit;
      const r=el.getBoundingClientRect(), parent=el.parentElement.getBoundingClientRect();
      const outsideParent=r.right>parent.right+1||r.bottom>parent.bottom+1||r.top<parent.top-1;
      const heading=el.closest('.heading');
      const headingOverflow=heading&&heading.scrollHeight>heading.clientHeight+1;
      if(size>min && (overflowing() || outsideParent || headingOverflow || el.scrollWidth>el.clientWidth+1)){
        el.style.fontSize=Math.max(min,size-1)+'px';changed=true;
      }
    }
    if(!changed)break;
  }
  // Persist sizes back to HTML so offline re-open is identical, with no runtime JS.
  return items.map(e=>({field:e.dataset.field||e.className,size:getComputedStyle(e).fontSize,
    line_height:getComputedStyle(e).lineHeight}));
}"""

CHECK_SCRIPT = """() => {
 const sheet=document.querySelector('.sheet'), s=sheet.getBoundingClientRect();
 const problems=[],boxes=[];
 for(const el of sheet.querySelectorAll('h1,p,li,.fact span,.credit,.edition,.date-index,.series,.greeting,.status,.qr span,.fold-label,.pass-band>span')){
   if(!el.textContent.trim()||getComputedStyle(el).display==='none'||el.getClientRects().length===0)continue;
   const r=el.getBoundingClientRect();
   const range=document.createRange();range.selectNodeContents(el);
   for(const t of range.getClientRects()){
     if(t.left<s.left-1||t.right>s.right+1||t.top<s.top-1||t.bottom>s.bottom+1)problems.push('text outside sheet: '+el.tagName);
     if(t.left<r.left-2||t.right>r.right+2||t.bottom>r.bottom+3)problems.push('text clipped: '+el.tagName);
   }
   if(el.scrollWidth>el.clientWidth+2)problems.push('horizontal overflow: '+el.tagName);
   boxes.push({tag:el.tagName,field:el.dataset.field||'',text:el.textContent,rect:{x:r.x,y:r.y,w:r.width,h:r.height}});
 }
 const sections=[...sheet.querySelectorAll(':scope > header,:scope > section,:scope > footer,.invite-main>header,.invite-main>section,.invite-main>footer,.inner-info>header,.inner-info>section,.inner-info>footer')].filter(e=>getComputedStyle(e).display!=='none');
 for(let i=0;i<sections.length;i++)for(let j=i+1;j<sections.length;j++){
   const a=sections[i].getBoundingClientRect(),b=sections[j].getBoundingClientRect();
   if(a.width&&a.height&&b.width&&b.height&&Math.min(a.right,b.right)-Math.max(a.left,b.left)>2&&Math.min(a.bottom,b.bottom)-Math.max(a.top,b.top)>2)problems.push('section overlap');
 }
 for(const img of sheet.querySelectorAll('img'))if(!img.complete||!img.naturalWidth)problems.push('broken image');
 const readingZones=[...sheet.querySelectorAll('[data-readability-zone]')].map(e=>({
   zone:e.dataset.readabilityZone,background:getComputedStyle(e).backgroundColor,
   color:getComputedStyle(e).color,rect:e.getBoundingClientRect().toJSON()}));
 // Transparency is intentional: actual pixels are inspected separately, not an opaque-panel requirement.
 const title=sheet.querySelector('h1'), style=getComputedStyle(title);
 return {passed:!problems.length,problems:[...new Set(problems)],text_boxes:boxes,width:s.width,height:s.height,
   title_layout:sheet.dataset.titleLayout,title_lines:Math.round(title.clientHeight/parseFloat(style.lineHeight)),reading_zones:readingZones};
}"""


def inspect_reading_pixels(page) -> dict:
    """Sample the real image under text. Advisory evidence, never certify visual quality alone."""
    import io
    import re

    from PIL import Image
    elements = page.locator('[data-readability-zone] h1,[data-readability-zone] p,[data-readability-zone] .credit')
    regions = elements.evaluate_all("""xs=>xs.filter(e=>e.textContent.trim()).map(e=>{
        const walker=document.createTreeWalker(e,NodeFilter.SHOW_TEXT), rects=[];
        while(walker.nextNode()){const range=document.createRange();range.selectNode(walker.currentNode);
          for(const r of range.getClientRects())rects.push({x:r.x,y:r.y,w:r.width,h:r.height})}
        return {field:e.dataset.field||e.closest('[data-field]')?.dataset.field||e.className,
        rects,color:getComputedStyle(e).color,size:parseFloat(getComputedStyle(e).fontSize)}})""")
    tag = page.add_style_tag(content='[data-readability-zone] h1,[data-readability-zone] p,[data-readability-zone] .credit{visibility:hidden!important}')
    try:
        with Image.open(io.BytesIO(page.screenshot())) as source:
            image = source.convert('RGB')
    finally:
        tag.evaluate('e=>e.remove()')
    records = []
    for r in regions:
        rgb = list(map(int, re.findall(r'\d+', r['color'])[:3]))
        fg = '#' + ''.join(f'{n:02x}' for n in rgb)
        ratios = []
        for rect in r['rects']:
            for ix in range(12):
                for iy in range(5):
                    x = min(image.width-1, max(0, int(rect['x'] + rect['w']*(ix+.5)/12)))
                    y = min(image.height-1, max(0, int(rect['y'] + rect['h']*(iy+.5)/5)))
                    bg = '#' + ''.join(f'{n:02x}' for n in image.getpixel((x, y)))
                    ratios.append(contrast(fg, bg))
        if not ratios:
            continue
        target = 3 if r['field'] == 'title' else 4.5
        records.append({'field': r['field'], 'minimum': round(min(ratios), 2),
                        'mean': round(sum(ratios)/len(ratios), 2),
                        'passing_fraction': round(sum(v >= target for v in ratios)/len(ratios), 3),
                        'target': target})
    return {'method': '60 background samples per actual text-line range with lettering hidden', 'regions': records,
            'needs_visual_review': any(r['passing_fraction'] < .9 for r in records),
            'limitation': 'Samples do not trace glyphs; inspect final imagery and regenerate/recompose when flagged.'}
