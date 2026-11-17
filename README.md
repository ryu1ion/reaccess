# ReAccess

## Look Once, Stay Focused with Efficient Test Time Memory

**Tianhao Chen · Yilong Fan · Yuheng Wu · Xiaobin Hu · Dongman Lee**  
KAIST · Tianjin University · National University of Singapore

[Project Page](https://ryu1ion.github.io/reaccess/) · [Paper](https://ryu1ion.github.io/reaccess/assets/pdf/reaccess-paper.pdf)

## Code release

> **The code will be publicly released after the review process is complete.**

This is the official repository for ReAccess. The research implementation is not yet available; this repository will be updated with the code after review.

## Overview

Vision-language models can encode important visual details without effectively using them to answer a question. **ReAccess** addresses this gap with a lightweight test-time evidence memory that preserves question-relevant visual information and keeps it accessible throughout reasoning.

During a single visual prefill, ReAccess builds a compact associative memory. Successive reads retrieve complementary evidence and steer both attention queries and hidden representations of the frozen VLM, improving visual grounding without repeated image encoding or explicit intermediate reasoning traces.

- **Preserve:** organize question-relevant visual associations while retaining the original image context.
- **Retrieve:** progressively recall complementary visual evidence from compact memory.
- **Guide:** integrate retrieved evidence into the model's native computation.

## Citation

```bibtex
@article{chen2026reaccess,
  title={ReAccess: Look Once, Stay Focused with Efficient Test Time Memory},
  author={Chen, Tianhao and Fan, Yilong and Wu, Yuheng and Hu, Xiaobin and Lee, Dongman},
  journal={arXiv preprint arXiv:2611.20936},
  year={2026}
}
```
