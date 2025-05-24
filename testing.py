#!/usr/bin/env python3
"""
Interactive CVD recolorization tool.

By default it does everything (simulate, daltonize, recolor),
prints metrics, shows comparison plots, and saves results.
"""
import sys
from pathlib import Path
from time import time

import cv2
import matplotlib.pyplot as plt
import numpy as np
from skimage.metrics import structural_similarity as ssim
from tqdm import tqdm

# -------------------------------------------------------------------
# 1) Matrices for simulation & daltonization
# -------------------------------------------------------------------
DEFICIENCIES = {
    "protanopia": {
        "sim": np.array([
            [0.56667, 0.43333, 0.0],
            [0.55833, 0.44167, 0.0],
            [0.0,     0.24167, 0.75833]
        ]),
        "dalt": np.array([
            [0.0, 2.02344, -2.52581],
            [0.0, 1.0,      0.0    ],
            [0.0, 0.0,      1.0    ]
        ])
    },
    "deuteranopia": {
        "sim": np.array([
            [0.625, 0.375, 0.0],
            [0.7,   0.3,   0.0],
            [0.0,   0.3,   0.7]
        ]),
        "dalt": np.array([
            [1.0,      0.0,      0.0    ],
            [0.494207, 0.0,      1.24827],
            [0.0,      0.0,      1.0    ]
        ])
    },
    "tritanopia": {
        "sim": np.array([
            [0.95,  0.05,   0.0],
            [0.0,   0.433,  0.567],
            [0.0,   0.475,  0.525]
        ]),
        "dalt": np.array([
            [1.0,       0.0,       0.0     ],
            [0.0,       1.0,       0.0     ],
            [-0.395913, 0.801109,  0.0     ]
        ])
    }
}


# -------------------------------------------------------------------
# 2) Core image‐processing routines
# -------------------------------------------------------------------
def read_image(path: Path) -> np.ndarray:
    data = np.fromfile(str(path), np.uint8)
    bgr = cv2.imdecode(data, cv2.IMREAD_COLOR)
    if bgr is None:
        raise IOError(f"Cannot read {path}")
    return cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)


def write_image(path: Path, img_rgb: np.ndarray) -> None:
    bgr = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR)
    ok, buf = cv2.imencode(path.suffix, bgr)
    if not ok:
        raise IOError(f"Failed to encode {path}")
    buf.tofile(str(path))


def transform_image(img: np.ndarray, M: np.ndarray) -> np.ndarray:
    """
    Apply a 3×3 matrix to an RGB image (uint8 [0..255]).
    """
    f = img.astype(np.float32) / 255.0
    t = np.dot(f, M.T)
    t = np.clip(t, 0.0, 1.0)
    return (t * 255.0).astype(np.uint8)


def simulate(img: np.ndarray, defn: str) -> np.ndarray:
    return transform_image(img, DEFICIENCIES[defn]["sim"])


def daltonize(img: np.ndarray, defn: str) -> np.ndarray:
    return transform_image(img, DEFICIENCIES[defn]["dalt"])


def recolor(img: np.ndarray, defn: str) -> np.ndarray:
    d = daltonize(img, defn)
    return simulate(d, defn)


# -------------------------------------------------------------------
# 3) Metrics & plotting
# -------------------------------------------------------------------
def compute_metrics(orig: np.ndarray, rec: np.ndarray) -> dict:
    mse = np.mean((orig.astype(float) - rec.astype(float)) ** 2)
    psnr = 10 * np.log10((255.0 ** 2) / mse) if mse > 0 else float("inf")
    g0 = cv2.cvtColor(orig, cv2.COLOR_RGB2GRAY)
    g1 = cv2.cvtColor(rec, cv2.COLOR_RGB2GRAY)
    s = ssim(g0, g1, data_range=255)
    return {"MSE": mse, "PSNR": psnr, "SSIM": s}


def plot_comparison(orig, sim_img, dalt_img, rec_img, title_prefix: str):
    plt.figure(figsize=(16, 5))
    for i, (label, im) in enumerate([
        ("Original", orig),
        ("Simulated", sim_img),
        ("Daltonized", dalt_img),
        ("Recolored", rec_img)
    ], start=1):
        ax = plt.subplot(1, 4, i)
        ax.imshow(im)
        ax.set_title(f"{title_prefix}\n{label}")
        ax.axis("off")
    plt.tight_layout()
    plt.show()


# -------------------------------------------------------------------
# 4) Interactive main()
# -------------------------------------------------------------------
def main():
    print("=== CVD Recolorization Interactive Tool ===\n")
    print("Choose deficiency type:")
    for i, key in enumerate(DEFICIENCIES.keys(), start=1):
        print(f"  {i}. {key}")
    choice = input("Enter 1/2/3: ").strip()
    try:
        defn = list(DEFICIENCIES.keys())[int(choice) - 1]
    except Exception:
        print("Invalid choice; exiting.")
        sys.exit(1)
    inp = Path(input("Enter input path (file or directory): ").strip())
    if not inp.exists():
        print("Path does not exist; exiting.")
        sys.exit(1)
    out_dir = Path(input("Enter output directory: ").strip())
    out_dir.mkdir(parents=True, exist_ok=True)
    if inp.is_dir():
        files = list(inp.glob("*.[jp][pn]g"))
        if not files:
            print("No .jpg/.png in directory; exiting.")
            sys.exit(1)
    else:
        files = [inp]

    print(f"\nProcessing {len(files)} image(s) as '{defn}'...\n")
    start = time()
    for path in tqdm(files, desc="Images"):
        try:
            img = read_image(path)
            sim_img = simulate(img, defn)
            dalt_img = daltonize(img, defn)
            rec_img = recolor(img, defn)

            # metrics
            m = compute_metrics(img, rec_img)
            print(f"\n[{path.name}] MSE={m['MSE']:.2f}, "
                  f"PSNR={m['PSNR']:.2f}dB, SSIM={m['SSIM']:.4f}")

            # save
            base = path.stem
            write_image(out_dir / f"{base}_{defn}_sim.png", sim_img)
            write_image(out_dir / f"{base}_{defn}_dal.png", dalt_img)
            write_image(out_dir / f"{base}_{defn}_rec.png", rec_img)

            # show
            plot_comparison(img, sim_img, dalt_img, rec_img, base)

        except Exception as e:
            print(f"Failed on {path}: {e}")

    print(f"\nDone in {time() - start:.2f}s. Outputs in {out_dir.resolve()}")


if __name__ == "__main__":
    main()
