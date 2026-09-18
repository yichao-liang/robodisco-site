"""Build index.html and one page per environment from data/envs.json.

Usage (from the repo root):

    python3 tools/build.py

Media for an environment with slug ``s`` is expected at
assets/gifs/s.gif (square solve loop for the grid), assets/thumbnails/s.png
(its first frame), assets/videos/s.mp4 (the solve at full quality) and
assets/init/s.gif (initial states of several tasks).
"""
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE_URL = ("https://github.com/BasisResearch/predicators/blob/master/"
              "predicators/envs/{module}.py")
ENVS_URL = ("https://github.com/BasisResearch/predicators/tree/master/"
            "predicators/envs")

HEAD = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="{description}">
    <title>{title}</title>
    <link rel="stylesheet" href="{prefix}assets/site.css">
    <script>
        if (localStorage.getItem('theme') === 'dark') {{
            document.documentElement.setAttribute('data-theme', 'dark');
        }}
    </script>
</head>
<body>
    <header>
        <div class="container">
            <a href="{prefix}index.html" class="logo">Robo<span>Disco</span></a>
            <nav>
                <ul class="nav-links">
                    <li><a href="{prefix}index.html#about">About</a></li>
                    <li><a href="{prefix}index.html#environments">Environments</a></li>
                    <li><a href="{envs_url}" target="_blank">GitHub</a></li>
                    <li><button class="theme-toggle" onclick="toggleTheme()" aria-label="Toggle theme">&#9790;</button></li>
                </ul>
            </nav>
        </div>
    </header>
    <div style="background: var(--accent); color: #fff; text-align: center; padding: 0.5rem; font-size: 0.85rem; font-weight: 600;">Work in Progress</div>
"""

FOOT = """    <footer>
        <div class="container">
            <p>RoboDisco</p>
            <p><a href="{envs_url}" target="_blank">View on GitHub</a></p>
        </div>
    </footer>
    <script>
        function toggleTheme() {{
            const html = document.documentElement;
            const btn = document.querySelector('.theme-toggle');
            if (html.getAttribute('data-theme') === 'dark') {{
                html.removeAttribute('data-theme');
                btn.innerHTML = '&#9728;';
                localStorage.setItem('theme', 'light');
            }} else {{
                html.setAttribute('data-theme', 'dark');
                btn.innerHTML = '&#9790;';
                localStorage.setItem('theme', 'dark');
            }}
        }}
        document.addEventListener('DOMContentLoaded', function() {{
            const btn = document.querySelector('.theme-toggle');
            btn.innerHTML = document.documentElement.getAttribute('data-theme') === 'dark'
                ? '&#9790;' : '&#9728;';
            // Swap the still thumbnail for the solve loop while hovered.
            document.querySelectorAll('[data-gif]').forEach(el => {{
                const box = el.querySelector('.gif-paused') || el;
                const img = el.querySelector('img');
                const still = img.src;
                el.addEventListener('mouseenter', () => {{
                    img.src = el.getAttribute('data-gif') + '?t=' + Date.now();
                    box.classList.remove('gif-paused');
                }});
                el.addEventListener('mouseleave', () => {{
                    img.src = still;
                    box.classList.add('gif-paused');
                }});
            }});
        }});
    </script>
</body>
</html>
"""

INDEX_BODY = """    <main>
        <section class="hero">
            <div class="container">
                <h1>RoboDisco</h1>
                <div class="authors">
                    <span class="author"><a href="https://yichao-liang.github.io/" target="_blank">Yichao Liang</a><sup>1,2</sup></span>
                    <span class="author"><a href="https://mlg.eng.cam.ac.uk/adrian/" target="_blank">Adrian Weller</a><sup>2,3</sup></span>
                    <span class="author"><a href="https://www.zenna.org/" target="_blank">Zenna Tavares</a><sup>1</sup></span>
                    <span class="author"><a href="https://tomsilver.github.io/" target="_blank">Tom Silver</a><sup>4</sup></span>
                    <span class="author"><a href="https://www.cs.cornell.edu/~ellisk/" target="_blank">Kevin Ellis</a><sup>5</sup></span>
                    <span class="author">and the MARA team</span>
                </div>
                <p class="affiliations"><sup>1</sup><a href="https://www.basis.ai/" target="_blank">Basis</a>, <sup>2</sup><a href="https://www.cam.ac.uk/" target="_blank">University of Cambridge</a>, <sup>3</sup><a href="https://www.turing.ac.uk/" target="_blank">The Alan Turing Institute</a>, <sup>4</sup><a href="https://www.princeton.edu/" target="_blank">Princeton University</a>, <sup>5</sup><a href="https://www.cornell.edu/" target="_blank">Cornell University</a></p>
                <p class="subtitle">Robot Model Discovery Benchmark &mdash; embodied world-model learning and causal discovery</p>
                <p class="hover-hint">Hover to watch a solve, click for the environment page</p>
                <div class="gif-grid">
{hero}
                </div>
            </div>
        </section>

        <section id="about">
            <div class="container">
                <p class="section-label">About</p>
                <h2>Embodied World Model Learning</h2>
                <p>RoboDisco (Robot Model Discovery Benchmark) is a benchmark suite for embodied world-model learning and causal discovery. It targets agents that must autonomously discover how their environment works &mdash; learning predictive models, identifying causal relationships between actions and outcomes, and forming abstractions that support planning and generalization.</p>
                <p>The benchmark is developed as part of the MARA (Modeling, Abstraction, Reasoning, and Action) project, which aims to build agents capable of scientific reasoning about novel environments.</p>
                <p>The suite comprises a diverse set of 3D robotic manipulation environments built on PyBullet, each presenting distinct challenges for world model learning. A Fetch robot must interact with various objects &mdash; from stacking blocks and pouring liquids to completing circuits and redirecting lasers &mdash; requiring agents to discover diverse physical and causal phenomena such as contact mechanics, fluid dynamics, electrical connectivity, and chain reactions.</p>
                <p>Every clip on this page shows a task being solved, by planning with ground-truth models or by a scripted skill sequence. Each environment page also shows the initial states of several tasks.</p>
            </div>
        </section>

        <section id="environments">
            <div class="container">
                <p class="section-label">Environments</p>
                <h2>Task Suite</h2>
{groups}
            </div>
        </section>
    </main>

"""

GROUPS = [
    ("benchmark", "Benchmark domains"),
    ("recent", "Continual-learning domains"),
    ("classic", "Further domains"),
]


def esc(text: str) -> str:
    return html.escape(text, quote=True)


def hero_cell(env: dict) -> str:
    s = env["slug"]
    return (f'                    <a class="gif-cell gif-paused" '
            f'href="envs/{s}.html" data-gif="assets/gifs/{s}.gif">'
            f'<img src="assets/thumbnails/{s}.png" alt="{esc(env["title"])}">'
            f'<span class="label">{esc(env["title"])}</span></a>')


def card(env: dict) -> str:
    s = env["slug"]
    badge = '<span class="badge">Benchmark</span>' if env["group"] == \
        "benchmark" else ""
    return f"""                    <a class="env-card" href="envs/{s}.html" data-gif="assets/gifs/{s}.gif">
                        <div class="env-card-gif gif-paused"><img src="assets/thumbnails/{s}.png" alt="{esc(env['title'])}" loading="lazy"></div>
                        <div class="env-card-body"><h3>{esc(env['title'])}{badge}</h3><div class="env-id">{esc(env['env'])}</div><p>{esc(env['tagline'])}</p></div>
                    </a>"""


def build_index(envs: list) -> str:
    groups = []
    for key, heading in GROUPS:
        members = [e for e in envs if e["group"] == key]
        cards = "\n".join(card(e) for e in members)
        groups.append(f'                <h3 class="env-subheading">{heading}</h3>\n'
                      f'                <div class="env-grid">\n{cards}\n'
                      f'                </div>')
    page = HEAD.format(
        description="RoboDisco: Robot Model Discovery Benchmark for embodied "
        "world-model learning and causal discovery",
        title="RoboDisco: Robot Model Discovery Benchmark",
        prefix="",
        envs_url=ENVS_URL)
    page += INDEX_BODY.format(hero="\n".join(hero_cell(e) for e in envs),
                              groups="\n".join(groups))
    page += FOOT.format(envs_url=ENVS_URL)
    return page


def build_env_page(env: dict, prev: dict, nxt: dict) -> str:
    s = env["slug"]
    badge = '<span class="badge">Benchmark</span>' if env["group"] == \
        "benchmark" else ""
    page = HEAD.format(description=esc(f"RoboDisco {env['title']}: "
                                       f"{env['tagline']}"),
                       title=f"{esc(env['title'])} - RoboDisco",
                       prefix="../",
                       envs_url=ENVS_URL)
    page += f"""    <main class="env-page">
        <div class="container">
            <p class="breadcrumb"><a href="../index.html#environments">&larr; All environments</a></p>
            <h1>{esc(env['title'])}{badge}</h1>
            <p class="env-id">{esc(env['env'])}</p>
            <p class="lede">{esc(env['description'])}</p>
            <div class="media-grid">
                <figure class="media-card">
                    <video src="../assets/videos/{s}.mp4" poster="../assets/thumbnails/{s}.png" autoplay loop muted playsinline controls></video>
                    <figcaption><strong>Solving a {esc(env['solve_split'])} task.</strong> {esc(env['solve_note'])}</figcaption>
                </figure>
                <figure class="media-card">
                    <img src="../assets/init/{s}.gif" alt="Initial states of several {esc(env['title'])} tasks">
                    <figcaption><strong>Initial states.</strong> {esc(env['init_note'])}</figcaption>
                </figure>
            </div>
            <p class="source-link"><a href="{SOURCE_URL.format(module=env['module'])}" target="_blank">Environment source</a> &middot; run with <code>python predicators/main.py --env {esc(env['env'])}</code></p>
            <nav class="pager">
                <a href="{prev['slug']}.html">&larr; {esc(prev['title'])}</a>
                <a href="{nxt['slug']}.html">{esc(nxt['title'])} &rarr;</a>
            </nav>
        </div>
    </main>

"""
    page += FOOT.format(envs_url=ENVS_URL)
    return page


def main() -> None:
    envs = json.loads((ROOT / "data" / "envs.json").read_text())
    (ROOT / "index.html").write_text(build_index(envs))
    out = ROOT / "envs"
    out.mkdir(exist_ok=True)
    for i, env in enumerate(envs):
        page = build_env_page(env, envs[i - 1], envs[(i + 1) % len(envs)])
        (out / f"{env['slug']}.html").write_text(page)
    print(f"wrote index.html and {len(envs)} environment pages")


if __name__ == "__main__":
    main()
