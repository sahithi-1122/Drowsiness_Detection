from pathlib import Path

root = Path(r'C:\Users\sriss\.cache\kagglehub\datasets\minhngt02\uta-rldd\versions\2')
IMG_EXTS = {'.jpg', '.jpeg', '.png', '.bmp'}

print('Root exists:', root.exists())
print()

if not root.exists():
    print('ERROR: path not found')
    exit(1)

for item in sorted(root.iterdir()):
    if item.is_dir():
        children = [x.name for x in sorted(item.iterdir())]
        print(f'DIR : {item.name}/  -> {children}')
    else:
        print(f'FILE: {item.name}  {item.stat().st_size/1024/1024:.1f}MB')

print()
total = 0
for path in ['train/active', 'train/fatigue', 'test/active', 'test/fatigue']:
    d = root / path
    if d.exists():
        n = sum(1 for f in d.rglob('*') if f.is_file() and f.suffix.lower() in IMG_EXTS)
        total += n
        print(f'  {path:<25}: {n:>6,} images')
    else:
        print(f'  {path:<25}: NOT FOUND')

print(f'\n  TOTAL: {total:,} images')
