"""Reopen actual v3 deliverables; decode composed QR and rasterize every PDF page."""
import hashlib
import json
import re
import subprocess
import unicodedata
from pathlib import Path

import cv2
from PIL import Image
from pypdf import PdfReader

from eventcraft.schema import Event, facts
from eventcraft.security import digest, write_json

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'examples/visual-v3'


def compact(value):
    return re.sub(r'\s+', '', unicodedata.normalize('NFKC', value))


def main():
    target = ROOT/'tmp/visual-v3-pdf'
    target.mkdir(parents=True,exist_ok=True)
    packages, pdfs, qr, readings = [], [], [], []
    for path in sorted(OUT.rglob('manifest.json')):
        m = json.loads(path.read_text(encoding='utf-8'))
        event = Event.model_validate_json(path.with_name('event.json').read_text(encoding='utf-8'))
        assert digest(event.model_dump()) == m['event_digest']
        assert event.demo and not m['publishable']
        assert m['generation_mode'] == 'event-specific-host-art'
        for record in m['files']:
            file = path.parent/record['path']
            assert hashlib.sha256(file.read_bytes()).hexdigest() == record['sha256']
            if file.suffix == '.png':
                with Image.open(file) as im:
                    assert list(im.size) == record['dimensions']
                    im.verify()
            if file.suffix == '.pdf':
                reader = PdfReader(file)
                text = compact(''.join(page.extract_text() or '' for page in reader.pages))
                if file.name != 'invitation_outside.pdf':
                    for field in ['title','when','where']:
                        assert compact(facts(event)[field]) in text, f'{file}: missing {field}'
                assert 'Asia/Shanghai' not in text
                assert 'UTC+8' not in text
                prefix = target/(str(file.relative_to(OUT)).replace('\\','_').replace('.pdf',''))
                subprocess.run(['pdftoppm','-r','80','-png',str(file),str(prefix)],check=True,capture_output=True)
                previews = sorted(target.glob(prefix.name+'-*.png'))
                assert len(previews) == len(reader.pages)
                pdfs.append({'file':str(file.relative_to(ROOT)),'pages':len(reader.pages),'rasterized':True})
        for name, check in m['checks']['layouts'].items():
            assert check['passed']
            if 'image_readability' in check:
                readings.append({'campaign':str(path.parent.relative_to(ROOT)),'output':name,
                                 **check['image_readability']})
        if m['checks']['qr'] == 'generated-from-url':
            for name in ['poster_portrait.png','poster_square.png','invitation.png']:
                decoded, _, _ = cv2.QRCodeDetector().detectAndDecode(cv2.imread(str(path.parent/name)))
                assert decoded == event.registration_url, f'QR failed {path.parent/name}'
                qr.append({'file':str((path.parent/name).relative_to(ROOT)),'decoded':decoded})
        else:
            assert not (path.parent/'registration_qr.png').exists()
        packages.append(str(path.parent.relative_to(ROOT)))
    # The user's fourteen supplied files are never altered.
    reference_records = json.loads((ROOT/'tmp/reference-study/inventory.json').read_text(encoding='utf-8'))
    actual = {hashlib.sha256(p.read_bytes()).hexdigest():p.name for p in (ROOT/'image').iterdir() if p.is_file()}
    for r in reference_records:
        assert r['sha256'] in actual, f'Reference bytes changed: {r["style"]}'
    report = {'campaigns':packages,'pdf_count':len(pdfs),'pdf_pages':sum(p['pages'] for p in pdfs),
              'composed_qr':qr,'references_unchanged':len(reference_records),'pdfs':pdfs,
              'background_readability':readings,
              'visual_review_required':sum(r['needs_visual_review'] for r in readings)}
    write_json(ROOT/'docs/acceptance-v3-audit.json',report)
    print(f'{len(packages)} complete campaigns; {len(pdfs)} PDFs/{report["pdf_pages"]} pages rasterized; '
          f'{len(qr)} composed QRs decoded; {report["visual_review_required"]} image-readability flags; '
          f'all {len(reference_records)} reference hashes unchanged')


if __name__ == '__main__':
    main()
