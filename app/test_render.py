# test_render.py
from jinja2 import Environment, FileSystemLoader, TemplateSyntaxError
import os, sys, json
env = Environment(loader=FileSystemLoader('templates'))  # update path
tmpl_name = 'report_template.html'                       # update name

ctx = {
    "report_date": "2025-10-28",
    "target": "demo.com",
    "findings": [
        {"ts": "2025-10-28 10:00", "url":"https://demo.com", "level":"Critical", "score":9, "summary":"test"}
    ]
}

try:
    tmpl = env.get_template(tmpl_name)
    out = tmpl.render(ctx)
    outpath = os.path.join('/tmp', 'test_report.html')
    with open(outpath + '.tmp', 'w', encoding='utf-8') as f:
        f.write(out)
    os.replace(outpath + '.tmp', outpath)
    print("Rendered OK > - test_render.py:22", outpath)
except TemplateSyntaxError as e:
    print("TemplateSyntaxError: - test_render.py:24", e, file=sys.stderr); raise
except Exception as e:
    print("Render failed: - test_render.py:26", e, file=sys.stderr); raise
