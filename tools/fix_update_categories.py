from pathlib import Path
p=Path('tools/update_categories.py')
s=p.read_text(encoding='utf-8')
s=s.replace("html = re.sub(r'<script>.*?</script>', script, html, count=1, flags=re.S)", "html = re.sub(r'<script>.*?</script>', lambda m: script, html, count=1, flags=re.S)")
p.write_text(s, encoding='utf-8')
