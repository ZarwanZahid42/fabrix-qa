# Notebook workspace

This directory is reserved for exploratory analysis and experiments. No notebook or experiment result exists yet.

Notebook rules:

- keep reusable logic in `preprocessing/`, `training/`, or `inference/`;
- record seed, dataset/split version, environment, and hardware;
- clear large outputs and never embed secrets, private data, or model weights;
- label exploratory metrics as non-final;
- avoid reading the held-out test set during tuning.

Likely future studies include dataset audit, YOLOv8 baseline, CNN selection, autoencoder calibration, fusion analysis, and heatmap-method comparison. Exact notebooks follow Phase 1 decisions.
