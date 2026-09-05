"""Render TILDA image/box/mask comparisons for annotation quality review."""

import cv2
import numpy as np
from build_dataset import ROOT, load_mask, load_rgb, read_yolo, save_image


def main() -> None:
    """Keep diagnostic renders in the ignored dataset workspace."""
    source = ROOT / "raw" / "tilda_400"
    out = ROOT / "inspection"
    out.mkdir(exist_ok=True)
    for stem in ("c1r1e1n43", "c1r1e3n8", "c1r1e2n1", "c1r3e4n1"):
        image = load_rgb(source / "images" / f"{stem}.tif")
        boxes, classes = read_yolo(source / "labels" / f"{stem}.txt", 768, 512)
        drawn = image.copy()
        for box, cls in zip(boxes, classes):
            x1, y1, x2, y2 = map(round, box)
            cv2.rectangle(drawn, (x1, y1), (x2, y2), (255, 0, 0), 2)
            cv2.putText(
                drawn,
                str(cls),
                (x1, max(15, y1)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 0, 0),
                1,
            )
        mask = load_mask([str(source / "masks" / f"{stem}.png")], (512, 768))
        overlay = image.copy()
        overlay[mask > 0] = image[mask > 0] // 2 + np.array([127, 0, 0], np.uint8)
        panel = np.concatenate([image, drawn, overlay], axis=1)
        save_image(out / f"{stem}.jpg", panel)


if __name__ == "__main__":
    main()
