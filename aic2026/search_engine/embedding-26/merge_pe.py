"""
Script gộp các file .npy trong từng thư mục L* (concat theo chiều 0).
Mỗi thư mục L (L21, L22, ...) sẽ được gộp thành một file L<N>.npy
và lưu vào thư mục output.

Cấu trúc:
    pe/
        L21/
            L21_V001.npy
            L21_V002.npy
            ...
        L22/
            L22_V001.npy
            ...
        ...

Output:
    pe_merged/
        L21.npy
        L22.npy
        ...
"""

import numpy as np
from pathlib import Path


# ─── CẤU HÌNH ────────────────────────────────────────────────────────────────

BASE_DIR = Path(__file__).parent / "pe"
OUTPUT_DIR = Path(__file__).parent / "pe_merged"

# ─────────────────────────────────────────────────────────────────────────────


def merge_L_folder(l_dir: Path, output_dir: Path) -> None:
    """Gộp tất cả .npy trong l_dir, concat theo axis=0, lưu ra output_dir."""
    l_name = l_dir.name  # e.g. "L21"

    # Lấy danh sách file .npy, sort để đảm bảo thứ tự
    npy_files = sorted(l_dir.glob("*.npy"))

    if not npy_files:
        print(f"  [SKIP] {l_name}: không có file .npy")
        return

    print(f"  [MERGE] {l_name}: {len(npy_files)} files ...", end=" ", flush=True)

    arrays = [np.load(f) for f in npy_files]
    merged = np.concatenate(arrays, axis=0)

    out_path = output_dir / f"{l_name}.npy"
    np.save(out_path, merged)

    print(f"-> shape {merged.shape}  => {out_path.name}")


def main():
    if not BASE_DIR.exists():
        raise FileNotFoundError(f"Không tìm thấy thư mục: {BASE_DIR}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Input  : {BASE_DIR}")
    print(f"Output : {OUTPUT_DIR}\n")

    # Lấy tất cả thư mục con dạng L*
    l_dirs = sorted([d for d in BASE_DIR.iterdir() if d.is_dir() and d.name.startswith("L")])

    if not l_dirs:
        print("Không tìm thấy thư mục L* nào.")
        return

    for l_dir in l_dirs:
        merge_L_folder(l_dir, OUTPUT_DIR)

    print("\nHoàn thành!")


if __name__ == "__main__":
    main()
