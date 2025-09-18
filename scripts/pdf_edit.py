import fitz

def merge_rects(rects, threshold=2):
    if not rects:
        return []

    rects = sorted(rects, key=lambda r: r.y0)
    merged = []
    current = rects[0]

    for r in rects[1:]:
        if r.y0 - current.y1 < threshold:
            current |= r  # Union of rectangles
        else:
            merged.append(current)
            current = r
    merged.append(current)
    return merged

doc = fitz.open(r"C:\Users\djord\Downloads\Animal Eye Iowa History Form.pdf")
page = doc[1]

hits = page.search_for("Please list any systemic medications, heartworm medications or food supplements currently used:")

# Merge overlapping or stacked rectangles
merged_hits = merge_rects(hits)

for rect in merged_hits:
    page.add_redact_annot(
        rect,
        text="Please list any systemic medications, heartworm medications, flea preventatives or food supplements currently used:",
        fontsize=12
    )

page.apply_redactions()
doc.save('Animal Eye Iowa History Form - Edited.pdf')

# Debug: print merged rectangles
for rect in merged_hits:
    print(rect)

