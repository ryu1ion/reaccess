# ReAccess project page

The project website for **ReAccess: Look Once, Stay Focused with Efficient Test Time Memory**.

**Live site:** https://ryu1ion.github.io/reaccess/

**Research repository:** https://github.com/ryu1ion/reaccess/tree/main

> The research code will be publicly released after the review process is complete.

## Branches

- `main` contains the research documentation and is reserved for the research implementation.
- `gh-pages` contains this static website, rendered figures, and paper PDFs. GitHub Pages publishes from the root of this branch.

Website changes should be committed to `gh-pages`; they do not need to be merged into `main`.

## Local preview

The website uses plain HTML, CSS, and JavaScript. No build step or package installation is required.

```sh
git clone --branch gh-pages --single-branch git@github.com:ryu1ion/reaccess.git reaccess-site
cd reaccess-site
python3 serve.py
```

Open http://localhost:8000/. To use another port, run `python3 serve.py --port 8001`.

## Updating and deploying

Edit `index.html`, `styles.css`, or `app.js`, preview the result, and push the changes to `gh-pages`.

In the repository's **Settings → Pages**, the publishing source is **Deploy from a branch**, with **gh-pages** and **/ (root)** selected. `.nojekyll` keeps the existing static files intact. Asset links are relative so the page works under the `/reaccess/` project path.

## Research assets

- The motivation, framework, efficiency, and visualization PDFs are copied unchanged from the paper project.
- Table 2 and Table 3 are cropped from the compiled paper PDF and rendered as images. They are not rebuilt as HTML tables.
- High-resolution PNG previews are in `assets/figures/`; the original PDFs and downloadable manuscript are in `assets/pdf/`.
- The downloadable manuscript is copied unchanged from the authors' supplied `reaccess.pdf`.
- `assets/provenance.json` records the source files, hashes, rendering dimensions, and table crop locations.
- Every research figure on the page supports enlargement and links to its PDF.

The optional `scripts/prepare_assets.py` helper rebuilds these assets from the authors' manuscript source. It expects a sibling `CVPR2027__Arxiv_` directory and requires Tectonic, Poppler, PyMuPDF, and Pillow. The manuscript source is not included in this branch; the committed assets are sufficient to view and deploy the site.

## Design credits and licenses

The page design was adapted from [Academic Project Page Template](https://github.com/eliahuhorwitz/Academic-project-page-template) and [Nerfies](https://github.com/nerfies/nerfies.github.io), with a custom layout, typography, and figure viewer. [Academic Project Astro Template](https://github.com/RomanHauksson/academic-project-astro-template) was also reviewed as a design reference.

- Website design is shared under [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/), with attribution in the page footer.
- The repository's existing [MIT license](LICENSE) is retained. It does not replace the separate terms for the website design, fonts, or paper assets.
- The locally hosted Manrope font uses the SIL Open Font License; see [assets/fonts/OFL.txt](assets/fonts/OFL.txt).
- The paper and research figures remain the property of their respective authors.
