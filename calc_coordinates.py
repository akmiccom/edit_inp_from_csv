# calc_coordinates.py
from __future__ import annotations

import sys
import time
from contextlib import contextmanager
from pathlib import Path

import pandas as pd


# 必要列（strip後の名前で管理）  # ※修正
NEEDED_COLS_STRIPPED = {  # ※追加
    "Node Label",  # ※追加
    "X",  # ※追加
    "Y",  # ※追加
    "Z",  # ※追加
    "U-U1",  # ※追加
    "U-U2",  # ※追加
    "U-U3",  # ※追加
}  # ※追加

DTYPES_STRIPPED = {  # ※追加
    "Node Label": "int32",  # ※追加
    "X": "float64",  # ※追加
    "Y": "float64",  # ※追加
    "Z": "float64",  # ※追加
    "U-U1": "float64",  # ※追加
    "U-U2": "float64",  # ※追加
    "U-U3": "float64",  # ※追加
}  # ※追加


def exe_dir() -> Path:
    # exe実行時: sys.executable が exe のフルパス
    # py実行時: __file__ の場所
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


@contextmanager
def timer(label: str):
    t0 = time.perf_counter()
    yield
    t1 = time.perf_counter()
    print(f"[TIME] {label:<20} : {t1 - t0:8.3f} s")


def pick_input_csv(input_dir: Path) -> Path:
    csv_files = sorted(input_dir.glob("*.csv"))
    if not csv_files:
        raise FileNotFoundError(f"CSVが見つかりません: {input_dir}/*.csv")
    # 今は先頭1件を採用（必要なら「最新」や「番号選択」へ変更可）
    return csv_files[0]


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
        raise ValueError(f"CSVに必要列がありません: {missing} / file={csv_path.name}")  # ※追加
    df = df.astype(DTYPES_STRIPPED)  # ※追加
    return df  # ※追加


def calc_coordinates_from_displacement(prospect_coefficient: float = 1.0) -> Path:
    """
    input/*.csv を読み込み、変位から X_new/Y_new/Z_new を作成して output/output.csv に保存。
    戻り値: 出力CSVパス
    """
    base = exe_dir()
    input_dir = base / "input"
    output_dir = base / "output"

    if not input_dir.exists():
        raise FileNotFoundError(f"inputフォルダが見つかりません: {input_dir}")

    output_dir.mkdir(parents=True, exist_ok=True)

    csv_path = pick_input_csv(input_dir)
    print("-" * 60)
    print(f"[INFO] 入力CSV: {csv_path.name}")

    with timer("read csv"):
        df = _read_displacement_csv(csv_path)  # ※修正

    # チェック用（先頭100行）
    df.head(1000).to_csv(output_dir / "input_check.csv", index=False)  # ※修正

    with timer("calc new coords"):
        # 仕様メモ:
        # Abaqusの変位(U-U*)を「元座標に足す／引く」の向きは、座標更新の定義に依存します。
        # 現状は「X + U * (-1) * coeff」を踏襲しています。  # ※修正
        df["X_new"] = df["X"] + df["U-U1"] * (-1.0) * prospect_coefficient
        df["Y_new"] = df["Y"] + df["U-U2"] * (-1.0) * prospect_coefficient
        df["Z_new"] = df["Z"] + df["U-U3"] * (-1.0) * prospect_coefficient

    out_csv = output_dir / "output.csv"
    out_chk = output_dir / "output_check.csv"

    with timer("write csv"):
        df.to_csv(out_csv, index=False)
        df.head(1000).to_csv(out_chk, index=False)

    print(f"[INFO] 出力CSV: {out_csv}")
    print("-" * 60)
    return out_csv
