"""Contact sheet of generated frames over dark + checker backgrounds (dev aid)."""
import glob, os, sys
from PIL import Image, ImageDraw
root = sys.argv[1]; out = sys.argv[2]; pat = sys.argv[3] if len(sys.argv) > 3 else '*'
files = sorted(glob.glob(os.path.join(root, '**', pat + '.*'), recursive=True))
files = [f for f in files if f.endswith(('.webp', '.png'))]
cell = 300
cols = 6
rows = (len(files) + cols - 1) // cols * 2
sheet = Image.new('RGB', (cols * cell, rows * (cell + 16)), (0, 0, 0))
dr = ImageDraw.Draw(sheet)
for i, f in enumerate(files):
    im = Image.open(f).convert('RGBA')
    im.thumbnail((cell - 8, cell - 8))
    for j, bg in enumerate([(22, 24, 30), None]):
        r = (i // cols) * 2 + j
        x, y = (i % cols) * cell, r * (cell + 16)
        if bg:
            b = Image.new('RGBA', (cell, cell), bg + (255,))
        else:
            b = Image.new('RGBA', (cell, cell), (205, 205, 205, 255))
            d = ImageDraw.Draw(b)
            for yy in range(0, cell, 16):
                for xx in range(0, cell, 16):
                    if (xx // 16 + yy // 16) % 2: d.rectangle([xx, yy, xx + 15, yy + 15], fill=(160, 160, 160, 255))
        b.alpha_composite(im, ((cell - im.width) // 2, (cell - im.height) // 2))
        sheet.paste(b.convert('RGB'), (x, y + 16))
        dr.text((x + 4, y + 2), os.path.basename(f)[:44], fill=(200, 200, 200))
sheet.save(out)
print(len(files), 'files ->', out)
