#!/usr/bin/env python3
"""
Build index.html from the two standalone viewers in src/.

Each viewer is a complete, self-contained HTML document with its own CSS and
its own global JavaScript scope. Rather than merging them -- which would mean
renaming hundreds of colliding identifiers and namespacing every CSS rule --
the build embeds each document verbatim and hands it to an <iframe srcdoc>.
Each view then keeps its own document, its own globals and its own stylesheet,
exactly as if it were opened on its own.

The embedded markup lives inside <script type="text/html"> blocks, so every
literal "</script>" in a viewer is escaped to "<\\/script>" on the way in and
restored on the way out. Without that, the HTML parser would end the template
block at the viewer's own closing script tag.

Usage:  python3 tools/build.py
"""

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

VIEWS = [
    {
        "id": "parts",
        "file": "src/parts-reference.html",
        "label": "Parts Reference",
        "blurb": "Every joint, actuator and plate, with specs and build notes",
    },
    {
        "id": "sequence",
        "file": "src/entry-sequence.html",
        "label": "Entry Sequence",
        "blurb": "Scrub the don/doff cycle, mechanism and front-plate layers",
    },
]

SHELL = """<!DOCTYPE html>
<!--
  Exo Skeleton 1 — combined viewer
  Copyright 2026 The Exo Skeleton 1 Authors

  Licensed under the Apache License, Version 2.0 (the "License");
  you may not use this file except in compliance with the License.
  You may obtain a copy of the License at

      http://www.apache.org/licenses/LICENSE-2.0

  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and
  limitations under the License.

  GENERATED FILE -- do not edit by hand.
  Edit the viewers in src/ and run:  python3 tools/build.py
-->
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Exo Skeleton 1</title>
<style>
  :root{
    --bg:#0f1319; --bar:#141a22; --line:#28323f;
    --txt:#dce4ee; --dim:#8695a8; --accent:#2fd3c4;
    --mono: ui-monospace,"SF Mono",Menlo,Consolas,monospace;
  }
  *{box-sizing:border-box}
  html,body{height:100%;margin:0}
  body{
    background:var(--bg);color:var(--txt);display:flex;flex-direction:column;overflow:hidden;
    font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Inter,Roboto,sans-serif;
  }
  #topbar{
    flex:0 0 auto;display:flex;align-items:center;gap:18px;padding:0 18px;
    height:54px;background:var(--bar);border-bottom:1px solid var(--line);
  }
  #brand{
    font-family:var(--mono);font-size:12px;letter-spacing:.2em;text-transform:uppercase;
    white-space:nowrap;
  }
  #brand span{color:var(--accent)}
  #tabs{display:flex;gap:4px;height:100%;align-items:center}
  .tab{
    background:transparent;border:1px solid transparent;color:var(--dim);cursor:pointer;
    font-family:var(--mono);font-size:11px;letter-spacing:.1em;text-transform:uppercase;
    padding:9px 14px;border-radius:8px;display:flex;align-items:center;gap:9px;
  }
  .tab:hover{color:var(--txt);background:#1b232d}
  .tab.on{background:var(--accent);color:#07120f;border-color:var(--accent)}
  .tab .n{
    font-size:9.5px;opacity:.65;border:1px solid currentColor;border-radius:4px;
    padding:1px 4px;line-height:1.3;
  }
  #blurb{
    margin-left:auto;font-size:12px;color:var(--dim);white-space:nowrap;overflow:hidden;
    text-overflow:ellipsis;max-width:46%;
  }
  #views{flex:1;position:relative;min-height:0}
  .view{position:absolute;inset:0;border:0;width:100%;height:100%;display:none;background:var(--bg)}
  .view.on{display:block}
  #loading{
    position:absolute;inset:0;display:flex;align-items:center;justify-content:center;
    font-family:var(--mono);font-size:11px;letter-spacing:.16em;color:var(--dim);
    text-transform:uppercase;pointer-events:none;
  }
  @media (max-width:700px){
    #topbar{height:auto;flex-wrap:wrap;padding:8px 12px;gap:8px}
    #blurb{display:none}
    .tab{padding:8px 11px}
  }
</style>
</head>
<body>

<div id="topbar">
  <div id="brand">EXO <span>SKELETON 1</span></div>
  <nav id="tabs">__TABS__</nav>
  <div id="blurb"></div>
</div>

<div id="views">
  <div id="loading">Select a view</div>
__TEMPLATES__
</div>

<script>
(function(){
  "use strict";

  var VIEWS = __VIEWMETA__;
  var frames = {};

  function unescapeMarkup(text){
    // restore the closing tags escaped at build time
    return text.replace(/<\\\\\\/script>/g, '<\\/script>');
  }

  function mount(id){
    if (frames[id]) return frames[id];
    var tpl = document.getElementById('tpl-' + id);
    var frame = document.createElement('iframe');
    frame.className = 'view';
    frame.id = 'view-' + id;
    frame.setAttribute('title', id + ' view');
    document.getElementById('views').appendChild(frame);
    frame.srcdoc = unescapeMarkup(tpl.textContent);
    frames[id] = frame;
    return frame;
  }

  function show(id){
    var meta = VIEWS.filter(function(v){ return v.id === id; })[0];
    if (!meta) return;
    var loading = document.getElementById('loading');
    if (loading) loading.style.display = 'none';

    mount(id);
    Object.keys(frames).forEach(function(k){
      frames[k].classList.toggle('on', k === id);
    });
    document.querySelectorAll('.tab').forEach(function(t){
      t.classList.toggle('on', t.dataset.view === id);
    });
    document.getElementById('blurb').textContent = meta.blurb;

    try { history.replaceState(null, '', '#' + id); } catch(e) {}
    try { localStorage.setItem('exo1-view', id); } catch(e) {}
  }

  document.querySelectorAll('.tab').forEach(function(t){
    t.addEventListener('click', function(){ show(t.dataset.view); });
  });

  // number keys switch views
  window.addEventListener('keydown', function(e){
    var i = parseInt(e.key, 10);
    if (i >= 1 && i <= VIEWS.length && !e.metaKey && !e.ctrlKey) show(VIEWS[i-1].id);
  });

  var start = (location.hash || '').replace('#','');
  if (!VIEWS.some(function(v){ return v.id === start; })) {
    start = null;
    try { start = localStorage.getItem('exo1-view'); } catch(e) {}
  }
  if (!VIEWS.some(function(v){ return v.id === start; })) start = VIEWS[0].id;
  show(start);
})();
</script>
</body>
</html>
"""


def build():
    tabs, templates, meta = [], [], []

    for i, v in enumerate(VIEWS, start=1):
        path = os.path.join(ROOT, v["file"])
        if not os.path.exists(path):
            sys.exit("missing viewer: %s" % v["file"])

        with open(path, encoding="utf-8") as fh:
            markup = fh.read()

        # escape the viewer's own closing script tags so the template block
        # survives the HTML parser
        markup = markup.replace("</script>", "<\\/script>")

        tabs.append(
            '<button class="tab" data-view="%s"><span class="n">%d</span>%s</button>'
            % (v["id"], i, v["label"])
        )
        templates.append(
            '  <script type="text/html" id="tpl-%s">%s</script>' % (v["id"], markup)
        )
        meta.append(
            '{id:"%s",label:"%s",blurb:"%s"}' % (v["id"], v["label"], v["blurb"])
        )

    out = (
        SHELL.replace("__TABS__", "\n    ".join(tabs))
        .replace("__TEMPLATES__", "\n".join(templates))
        .replace("__VIEWMETA__", "[" + ",".join(meta) + "]")
    )

    dest = os.path.join(ROOT, "index.html")
    with open(dest, "w", encoding="utf-8") as fh:
        fh.write(out)

    print("built %s (%.1f KB) from %d viewers" % (dest, len(out) / 1024.0, len(VIEWS)))


if __name__ == "__main__":
    build()
