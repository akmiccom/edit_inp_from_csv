# calc_coordinates.py
import time
from pathlib import Path

import pandas as pd

from utils import timer, search_file
from utils import file_folder_exsist_check
from utils import csv_dir, output_dir

# 必要列（strip後の名前で管理）
NEEDED_COLS_STRIPPED = {
    "Node Label",
    "X",
    "Y",
    "Z",
    "U-U1",
    "U-U2",
    "U-U3",
}

DTYPES_STRIPPED = {
    "Node Label": "int32",
    "X": "float64",
    "Y": "float64",
    "Z": "float64",
    "U-U1": "float64",
    "U-U2": "float64",
    "U-U3": "float64",
}


def _read_displacement_csv(csv_path: Path) -> pd.DataFrame:  # ※追加
    """
    Abaqus出力など、列名の先頭空白ゆれを吸収して必要列だけ読む。
    ・usecols を callable にして、strip後の列名で判定
    ・読み込み後に列名を strip して正規化
    """  # ※追加
    df = pd.read_csv(  # ※追加
        csv_path,  # ※追加
        usecols=lambda c: c.strip() in NEEDED_COLS_STRIPPED,  # ※追加
    )  # ※追加
    df = df.rename(columns=lambda c: c.strip())  # ※追加
    missing = [c for c in sorted(NEEDED_COLS_STRIPPED) if c not in df.columns]  # ※追加
    if missing:  # ※追加
        raise ValueError(
            f"CSVに必要列がありません: {missing} / file={csv_path.name}"
        )  # ※追加
    df = df.astype(DTYPES_STRIPPED)  # ※追加
    return df  # ※追加


def calc_coordinates_from_displacement(
    input_path,
    output_dir,
    prospect_coefficient: float = 1.0,
) -> Path:
    """
    input/*.csv を読み込み、変位から X_new/Y_new/Z_new を作成して output/output.csv に保存。
    戻り値: 出力CSVパス
    """

    output_dir.mkdir(parents=True, exist_ok=True)

    # print("-" * 60)
    print("[INFO] === calc coordinates from displacement start ===")
    print(f"[INFO] 入力CSV: {input_path.name}")

    with timer("read csv"):
        df = _read_displacement_csv(input_path)  # ※修正

    # チェック用（先頭100行）
    df.head(100).to_csv(output_dir / "input_for_check.csv", index=False)  # ※修正

    with timer("calc new coords"):
        # Abaqusの変位(U-U*)を「元座標に足す／引く」の操作を行う
        # deformed : 変形後形状
        # prospects : 反転した見込み形状
        df["X_deformed"] = df["X"] + df["U-U1"]
        df["Y_deformed"] = df["Y"] + df["U-U2"]
        df["Z_deformed"] = df["Z"] + df["U-U3"]

        df["X_prospects"] = df["X"] + df["U-U1"] * (-1.0) * prospect_coefficient
        df["Y_prospects"] = df["Y"] + df["U-U2"] * (-1.0) * prospect_coefficient
        df["Z_prospects"] = df["Z"] + df["U-U3"] * (-1.0) * prospect_coefficient

    output_csv_path = output_dir / "output.csv"
    output_check_path = output_dir / "output_for_check.csv"

    with timer("write csv"):
        df.to_csv(output_csv_path, index=False)
        df.head(100).to_csv(output_check_path, index=False)

    print(f"[INFO] 出力CSV: {output_csv_path}")
    print("[INFO] === calc coordinates from displacement end ===")
    # print("-" * 60)
    return output_csv_path


if __name__ == "__main__":

    t0 = time.perf_counter()

    file_folder_exsist_check()

    input_csv_path = search_file(csv_dir, file_extension=".csv")
    output_csv_path = calc_coordinates_from_displacement(input_csv_path, output_dir)

    print(f"[INFO] Total elapsed: {time.perf_counter() - t0:.3f} sec")
