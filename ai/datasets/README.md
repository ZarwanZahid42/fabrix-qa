# FabriX-QA — Datasets

> **Note:** Raw datasets are NOT tracked by Git (see `.gitignore`).
> Model weights are tracked via Git LFS or stored externally.

## Datasets Used

### 1. AITEX Fabric Defect Dataset
- **Source:** [AITEX](https://www.aitex.es/afid/)
- **Description:** 245 defect images across 12 defect types + 140 defect-free images at 4096×256 px
- **Download:** Request access from AITEX website
- **Place in:** `datasets/raw/aitex/`

### 2. NEU Surface Defect Database
- **Source:** [NEU](http://faculty.neu.edu.cn/yunhyan/NEU_surface_defect_database.html)
- **Description:** 1800 images, 6 defect types: rolled-in scale, patches, crazing, pitted surface, inclusion, scratches
- **Download:** Available via the NEU lab website
- **Place in:** `datasets/raw/neu/`

### 3. Custom FabriX Dataset (to be collected)
- **Description:** Real-world fabric inspection images collected from production environment
- **Labelling Tool:** LabelImg / Roboflow
- **Format:** YOLO format (txt annotations)
- **Place in:** `datasets/raw/custom/`

## Directory Structure
```
datasets/
├── raw/          # Original, untouched source data
│   ├── aitex/
│   ├── neu/
│   └── custom/
├── processed/    # Resized, patched, split into train/val/test
│   ├── train/
│   ├── val/
│   └── test/
└── README.md     # This file
```

## Data Preparation
Run the preprocessing pipeline:
```bash
cd ai/
python preprocessing/patch_extractor.py --source datasets/raw/aitex --output datasets/processed
```
