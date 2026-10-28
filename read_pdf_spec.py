import pypdf

reader = pypdf.PdfReader('EduBridge – Complete Project Documentation.pdf')
print(f"Total Pages: {len(reader.pages)}")

# Print page by page headers and key sections
toc = []
for i, page in enumerate(reader.pages):
    txt = page.extract_text()
    lines = [l.strip() for l in txt.split('\n') if l.strip()]
    if lines:
        header = lines[0] if len(lines) > 0 else ""
        sub = lines[1] if len(lines) > 1 else ""
        toc.append((i + 1, header, sub))

for page_num, h, s in toc[:47]:
    print(f"Page {page_num:02d}: {h} | {s}")
