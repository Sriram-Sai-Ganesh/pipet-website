# Pipelined Transformers — project page

Project page for *Pipelined Transformers: Autoregressive Generation with Increased Parallelism*.
Code: https://github.com/argolab/PipeT

Built from the [Academic Project Page Template](https://github.com/eliahuhorwitz/Academic-project-page-template).
Figures in `static/images/` are rendered from the paper's PDF figures.

Preview locally: `python3 -m http.server` and open http://localhost:8000.
Deploy: enable GitHub Pages on this repo (branch `main`, root).

## Anonymized version

Identifying content in `index.html` is wrapped in `<!-- ANON:START --> … <!-- ANON:REPLACE … ANON:END -->`
markers; the text after `ANON:REPLACE` is what the anonymous site shows. Wrap any new identifying content the same way.

- Build: `ANON_CODE_URL=<anonymized code link> python3 scripts/build_anon.py` → `dist-anon/`.
  Only `index.html` and the files it references are copied, and the build fails if a name, affiliation or repo link survives.
  Without `ANON_CODE_URL` the Code button is dropped.
- Deploy: `ANON_CODE_URL=… scripts/deploy_anon.sh origin` force-pushes the build as one history-free commit
  authored by "Anonymous" to the `anon` branch.
- Host: on https://anonymous.4open.science, anonymize this repo with branch `anon`, enable the GitHub page option
  (source: branch `anon`, path `/`), keep images and links enabled, and add the author names as terms as a backstop.
  The site is served at `https://anonymous.4open.science/w/<id>/`.
