# Model artifact workspace

This directory documents model bundles; weights and generated artifacts are ignored by Git.

The planned pipeline requires three versioned artifacts:

- `yolov8_fabric_defects.pt` for detection;
- `fabric_defect_classifier.pt` for four-class CNN classification;
- `fabric_anomaly_autoencoder.pt` for anomaly scoring.

No architecture, registry, weight file, accuracy, or artifact size has been selected or produced. A future bundle manifest must record training code revision, dataset/split version, preprocessing, class map, thresholds, metrics, framework versions, hardware, and a cryptographic checksum.
