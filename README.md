# Messaging-Channel Reliability Study

## What This Project Is

This project studies whether image transformations applied by messaging apps can make image-based diagnostic classifiers less reliable.

The primary setting is maize disease classification. The study should also test a second, openly licensed phone-captured image domain if the data, labels, and ethics requirements are acceptable.

The central comparison is the original image, the same image sent through a real messaging channel, the same image sent as a document/file control, a locally emulated version of the measured channel, and standard synthetic JPEG corruptions.

The study must measure more than accuracy. The key outcome is whether a channel changes the model's decision or causes a confident wrong prediction.

## Research Questions

- How do real messaging channels affect predictions, accuracy, and calibration?
- Does forwarding an image through multiple hops compound the effect?
- Does sending the image as a file/document avoid most of the damage?
- Can a small, measured channel emulator reproduce the real channel's model decisions?
- Do channel-aware augmentation and provenance-aware calibration reduce confident errors better than a generic quality score?

## First Decision: Run the Pilot

Do this before building the full pipeline.

1. Select about 300 held-out maize images across the four classes.
2. Train a lightweight MobileNetV3 baseline on the remaining data.
3. Send the pilot images manually through WhatsApp and Telegram in photo/compressed mode and document/file mode.
4. Match received files to originals with perceptual hashes.
5. Run inference on originals and received images.
6. Calculate prediction flip rate, calibration change, and confident-error rate.

Suggested decision rule:

- Continue if any photo-mode channel produces roughly 1-2% or more flips, or a clear increase in confident errors.
- If the effect is near zero at 224-pixel input, repeat at higher resolution, with multi-hop forwarding, and with small-lesion field images.
- If the effect remains negligible, frame the result as a useful negative measurement study or switch to the documented backup topic.

Agree the threshold with the supervisor before inspecting the pilot results.

## Required Study Design

### Data

- Use PlantVillage maize classes: healthy, common rust, northern leaf blight, and gray leaf spot.
- Audit near-duplicates and split by duplicate group, never by individual image alone.
- Keep raw data immutable.
- Add a second domain only after verifying its licence, labels, class overlap, and ethics requirements.
- Create a probe set of 20-30 images at approximately 640, 1280, 2048, and 4000 pixels on the long side.

### Models

- Baselines: MobileNetV3-Large and ResNet-18 or EfficientNet-B0.
- Train five seeds per main configuration where compute permits.
- Evaluate at 224 pixels and at a larger resolution such as 384 pixels.
- Save per-image logits, labels, predictions, confidence, model seed, and preprocessing configuration.

### Channels

Measure each channel manually using owned accounts and record the app and operating-system versions.

| Channel | Mode | Hops | Purpose |
| --- | --- | --- | --- |
| WhatsApp | Photo | 1-4 | Primary real channel |
| WhatsApp | Document/file | 1 | Near-lossless control |
| Telegram | Compressed photo | 1-4 | Second real channel |
| Telegram | File | 1 | Near-lossless control |
| Messenger | Photo | 1 | Optional third platform |
| Synthetic JPEG | Quality 50-95 | 1 | Conventional corruption baseline |

Repeat measurements on a second device or OS version and after major app updates when possible. Every measurement needs a date, device model, OS version, app version, network type, mode, hop count, original image ID, and received-file path.

## Implementation Order

### 1. Create the project

Use Python 3.11 or later and pin the exact environment after installation.

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev,ml,analysis,measurement,quality]"
pip freeze > requirements.txt
```

The first scaffold already provides a fingerprinting CLI and the core reliability metrics:

```powershell
python -m pytest -q
channel-study --help
```

Recommended layout:

```text
configs/                 YAML configuration files
data/raw/                Original datasets; never edit in place
data/splits/             Group-aware train/validation/test CSVs
data/channels/           Received files grouped by app, mode, and hop
data/channel_log.csv     Measurement metadata and fingerprints
src/channel_study/       Installable Python package
src/channel_study/cli.py Fingerprinting and project commands
src/channel_study/metrics.py Reliability and calibration metrics
src/channel_study/fingerprint.py JPEG and metadata characterization
src/channel_study/audit.py Duplicate grouping and split creation (next)
src/channel_study/train.py Model training and checkpoints (next)
src/channel_study/infer.py Inference and per-image logits (next)
src/channel_study/emulate.py Channel emulator and augmentation (next)
src/channel_study/calibrate.py Calibration variants (next)
src/channel_study/stats.py Bootstrap and paired statistical tests (next)
results/                 Tables, figures, logits, and reports
notebooks/               Exploration only; source-of-truth code stays in src/
README.md
```

### 2. Audit and split the data

Use perceptual hashes to cluster near-duplicates. Inspect representative clusters manually, then create group-aware train, validation, and test splits. Save the split files and hash/group information so the split can be reproduced exactly.

### 3. Train clean baselines

Fix and document the evaluation resize, crop, normalization, orientation handling, and random seeds. Train the baseline models on clean data and write all per-image logits to Parquet. Later analysis must read these stored logits rather than rerunning ad hoc inference.

### 4. Measure real channels

Use a fixed image ordering. Send the same probe and test images through each app and mode manually. Forward received images for hops 2-4 where applicable. Pull the resulting files with ADB or a file manager; Android storage paths vary by version, so verify the path on the device first.

Match received files to originals by perceptual hash. Flag high-distance matches and duplicate mappings for manual review. Do not assume app filenames or receive order identify the original.

For every received image, record dimensions, file size, bytes per pixel, JPEG luminance and chrominance quantization tables, chroma subsampling, EXIF/metadata presence, app, mode, hop, device, OS, date, network, and original ID.

Characterize resizing by comparing probe input and output dimensions. Estimate JPEG quality only as a convenience; preserve the actual quantization tables when they are custom.

### 5. Build and validate the emulator

Implement the measured orientation handling, RGB conversion, resize limit, resampling filter, quantization tables, subsampling, and metadata behavior. Fit parameters on one part of the probe/test material and validate on held-out images and, when possible, a held-out device or app version.

Validate using both:

- pixel fidelity: PSNR and SSIM;
- behavioral fidelity: model decision agreement and confidence difference.

The behavioral check is the important one. Compare the fitted emulator against a simple JPEG-quality-70 baseline and show that the fitted emulator better reproduces the real channel.

Store emulator parameters with the app version and measurement date in YAML.

### 6. Run reliability experiments

Run every model on clean images, each real channel and hop, document-mode controls, fitted emulators, and the synthetic JPEG ladder. Compute accuracy and macro-F1, prediction flip rate against the original, ECE, Brier score, NLL, confident-error rate at confidence >= 0.9, failure-prediction AUROC, AURC, and selective risk at 80% and 90% coverage.

Always show the document-mode control next to the corresponding photo-mode result.

### 7. Test mitigations

Compare clean and raw-softmax confidence, clean temperature scaling, channel-aware temperature scaling, channel-aware augmentation using measured emulator parameters, provenance-conditioned correctness prediction using confidence and file fingerprints, a no-reference quality-aware baseline such as BRISQUE/NIQE/MUSIQ, and an optional deep ensemble.

Fit calibration and mitigation components only on validation or calibration data. Evaluate the final comparison on real channels that were not used to fit the emulator. Do not evaluate a mitigation only on the emulator that generated its training examples.

## Statistics and Figures

- Bootstrap 95% confidence intervals over images.
- Paired McNemar tests for condition-level prediction differences.
- Paired Wilcoxon tests across seeds where appropriate.
- Holm correction for multiple comparisons.
- Report effect sizes, confidence intervals, and practical differences, not only p-values.

Main figures should include flip rate by channel and hop, reliability diagrams, risk-coverage curves, confident-error rates across mitigations, and emulator-versus-real agreement. Inspect Grad-CAM on a small set of flipped cases as qualitative evidence only.

## Reproducibility Requirements

Before publication, the repository must contain pinned dependencies, versioned YAML configs and random seeds, leakage-free split files, channel logs and measured fingerprints, emulator parameters tied to app versions and dates, per-image logits and analysis scripts, tables and figures generated by one-command entry points, and clear data-licence and data-availability statements.

Publish a tagged GitHub release and archive it on Zenodo where possible. The README should eventually document commands that reproduce each main table and figure from the released artifacts.

## Guardrails

- Send only public, licensed images or images created for the study. Never send private patient images through messaging apps.
- Use owned accounts and manual sending. Do not automate, scrape, or use unofficial clients.
- Check institutional ethics requirements, especially for a skin-lesion domain.
- Record platform versions because channel behavior can change silently.
- Treat the result as an image-channel reliability study, not as medical or agronomic advice.
- Re-run the literature searches before committing to novelty claims and again before submission. Log database, query, date, and relevant-hit count.

## Timeline and Deliverables

| Period | Work | Deliverable |
| --- | --- | --- |
| Week 1 | Pilot and go/no-go decision | Pilot note and decision |
| Weeks 2-3 | Data audit, splits, baselines | Splits, checkpoints, logits |
| Weeks 4-5 | Real-channel measurements | Channel log and fingerprint tables |
| Week 6 | Emulator and validation | Emulator and agreement results |
| Weeks 7-9 | Reliability experiments and second domain | Metrics, tables, plots |
| Weeks 10-11 | Mitigations | Augmentation and calibration comparison |
| Week 12 | Statistics and figures | Final figures, tables, flipped-case analysis |
| Weeks 13-15 | Writing and literature refresh | Full manuscript draft |
| Week 16 | Review and release | Submission package and reproducibility repository |

## What Counts as Success

The project is successful if it produces a defensible, versioned answer to all five research questions, including negative results where appropriate. The strongest practical result would be evidence that ordinary photo mode causes decision or confidence failures while document/file mode largely avoids them, plus a validated emulator and mitigation tested on real held-out channels.

Keep the novelty claim modest: the contribution is rigorous measurement, emulator validation by model decisions, multi-hop analysis, and practical reliability guidance, not a new classifier architecture.