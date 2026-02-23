# update_inp.py
from __future__ import annotations

import re
import sys
import time
from contextlib import contextmanager
from pathlib import Path

import pandas as pd


def exe_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


def pick_single_inp(inp_dir: Path) -> Path:
    inp_files = sorted(inp_dir.glob("*.inp"))
    if len(inp_files) == 0:
        raise FileNotFoundError(f"inpが見つかりません: {inp_dir}/*.inp")
    if len(inp_files) > 1:
        names = ", ".join(p.name for p in inp_files)
        raise RuntimeError(f"inpが複数あります（1つにしてください）: {names}")
    return inp_files[0]


@contextmanager
def timer(label: str):
    t0 = time.perf_counter()
    yield
    t1 = time.perf_counter()
    print(f"[TIME] {label:<20} : {t1 - t0:8.3f} s")


def update_inp_nodes(
    inp_text: str,
    mapping: dict[int, tuple[float, float, float]],
    sample_limit: int = 100,
) -> tuple[str, list[str], int]:
    """
    *NODE セクション内の node 行を mapping に基づいて座標置換。

    Returns:
      updated_text: 置換後のinp全文
      updated_samples: 更新したNODE行のサンプル（先頭 sample_limit 行）
      updated_count: 更新したNODE行の総数
    """
    lines = inp_text.splitlines()
    out_lines: list[str] = []
    updated_samples: list[str] = []
    updated_count = 0
    in_node = False

    for line in lines:
        stripped = line.strip()

        # *NODE 開始
        if stripped.upper().startswith("*NODE"):
            in_node = True
            out_lines.append(line)
            continue

        if in_node:
            # 次のキーワードが来たら *NODE 終了
            if stripped.startswith("*") and not stripped.upper().startswith("*NODE"):
                in_node = False
                out_lines.append(line)
                continue

            # 空行/コメントはそのまま
            if (not stripped) or stripped.startswith("**"):
                out_lines.append(line)
                continue

            # node行の先頭ID取得
            m = re.match(r"\s*(\d+)\s*,(.*)", line)
            if not m:
                out_lines.append(line)
                continue

            nid = int(m.group(1))
            if nid in mapping:
                x, y, z = mapping[nid]
                new_line = f"{nid:>10d},  {x:.5E},  {y:.5E},  {z:.5E},"
                out_lines.append(new_line)

                updated_count += 1
                if len(updated_samples) < sample_limit:
                    updated_samples.append(new_line)
            else:
                out_lines.append(line)
        else:
            out_lines.append(line)

    updated_text = "\n".join(out_lines) + ("\n" if inp_text.endswith("\n") else "")
    return updated_text, updated_samples, updated_count


def write_updated_node_samples(
    out_path: Path,
    updated_samples: list[str],
    updated_count: int,
    sample_limit: int = 100,
    encoding: str = "utf-8",
) -> None:
    """
    更新したNODE行だけを確認用に出力（先頭 sample_limit 行）。
    """
    lines = []
    lines.append("** Updated NODE lines (sample)")
    lines.append(f"** Total updated node lines: {updated_count}")
    lines.append(f"** Showing first {min(sample_limit, len(updated_samples))} lines")
    lines.append("*NODE")
    lines.extend(updated_samples)
    lines.append("")  # 末尾改行用

    out_path.write_text("\n".join(lines), encoding=encoding)


def update_inp(csv_path: Path | None = None):  # ※修正
    base = exe_dir()
    inp_dir = base / "inp"
    output_dir = base / "output"

    output_dir.mkdir(parents=True, exist_ok=True)  # ※追加

    # inp フォルダ存在チェック（exe運用で原因が分かりやすい）  # ※追加
    if not inp_dir.exists():  # ※追加
        raise FileNotFoundError(f"inpフォルダが見つかりません: {inp_dir}")  # ※追加

    # 入力CSV（座標更新表）  # ※修正
    csv_path = csv_path or (output_dir / "output.csv")  # ※追加
    if not csv_path.exists():
        raise FileNotFoundError(f"csvが見つかりません: {csv_path}")

    # inp は inp/ 内の *.inp を1つだけ取得
    inp_path = pick_single_inp(inp_dir)

    # 出力
    out_inp_path = output_dir / "updated.inp"
    out_node_check_path = output_dir / "updated_check.inp"  # ★更新したNODE 100行だけ

    t0 = time.perf_counter()

    # CSV読み込み
    with timer("read csv"):  # ※修正
        df = pd.read_csv(csv_path)  # ※修正

    # mapping 作成（itertuplesで高速化）  # ※修正
    with timer("build mapping"):  # ※追加
        mapping = {  # ※修正
            int(r.Node_Label): (float(r.X_new), float(r.Y_new), float(r.Z_new))  # ※修正
            for r in df.rename(columns={"Node Label": "Node_Label"}).itertuples(index=False)  # ※修正
        }  # ※修正

    # inp読み込み
    with timer("read inp"):  # ※修正
        inp_text = inp_path.read_text(encoding="utf-8", errors="replace")  # ※修正

    # 更新（サンプルも回収）
    with timer("update *NODE"):  # ※修正
        updated_text, updated_samples, updated_count = update_inp_nodes(  # ※修正
            inp_text, mapping, sample_limit=100  # ※修正
        )  # ※修正

    # 保存（本体）
    out_inp_path.write_text(updated_text, encoding="utf-8")  # （mkdir済みなので安全）  # ※修正

    # 保存（更新したNODE行だけ100行）
    write_updated_node_samples(
        out_node_check_path,
        updated_samples=updated_samples,
        updated_count=updated_count,
        sample_limit=1000,
        encoding="utf-8",
    )

    print(f"[INFO] Input INP : {inp_path.resolve()}")
    print(f"[INFO] Output INP: {out_inp_path.resolve()}")
    print(f"[INFO] Check INP : {out_node_check_path.resolve()}  (更新NODE行のみ先頭100行)")
    print(f"[INFO] 更新したNODE行の総数: {updated_count}")
    print(f"[INFO] 合計: {time.perf_counter() - t0:.3f} 秒")
