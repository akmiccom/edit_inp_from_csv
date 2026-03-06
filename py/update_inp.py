# update_inp.py
from __future__ import annotations

import re
import sys
import time
from contextlib import contextmanager
from pathlib import Path

import pandas as pd

from utils import timer, search_file, file_folder_exsist_check, create_include_inp
from utils import csv_dir, inp_dir, output_dir
from extraxct_nodes_elements import split_inp
from calc_coordinates import calc_coordinates_from_displacement


def update_inp_nodes(
    inp_text: str,
    mapping: dict[int, tuple[float, float, float]],
    # sample_limit: int = 100,
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

            else:
                out_lines.append(line)
        else:
            out_lines.append(line)

    updated_text = "\n".join(out_lines) + ("\n" if inp_text.endswith("\n") else "")

    return updated_text


def update_inp(csv_path: Path, output_dir: Path) -> None:

    print("[INFO] === update inp start ===")

    with timer("read csv"):
        df = pd.read_csv(csv_path)

    # 1回だけrenameして使い回す
    df2 = df.rename(columns={"Node Label": "Node_Label"})

    # mapping 作成（見込み形状 deformed）
    with timer("build mapping deformed"):
        mapping_deformed = {
            int(r.Node_Label): (
                float(r.X_deformed),
                float(r.Y_deformed),
                float(r.Z_deformed),
            )
            for r in df2.itertuples(index=False)
        }

    # mapping 作成（変形後形状 prospects）
    with timer("build mapping prospects"):
        mapping_prospects = {
            int(r.Node_Label): (
                float(r.X_prospects),
                float(r.Y_prospects),
                float(r.Z_prospects),
            )
            for r in df2.itertuples(index=False)
        }

    # output_dir 配下の node_XX.inp を取得（globの基点を統一）
    inp_files = sorted(output_dir.glob("node_[0-9][0-9].inp"))

    for inp_path in inp_files:
        file_stem = inp_path.stem
        file_num = file_stem[-2:]

        # inp読み込み
        with timer(f"read inp: {inp_path.name}"):
            inp_text = inp_path.read_text(encoding="utf-8", errors="replace")

        # update_deformed
        with timer(f"update_deformed *NODE: {inp_path.name}"):
            deformed_text = update_inp_nodes(inp_text, mapping_deformed)
        deformed_inp_path = output_dir / f"{file_stem}_deformed.inp"
        deformed_inp_path.write_text(deformed_text, encoding="utf-8", newline="\n")

        # make include_inp
        create_include_inp(output_dir, file_num, keyword="_deformed")

        print(f"[INFO] Output INP: {deformed_inp_path.resolve()}")

        # update_prospects
        with timer(f"update_prospects *NODE: {inp_path.name}"):
            prospects_text = update_inp_nodes(inp_text, mapping_prospects)
        prospects_inp_path = output_dir / f"{file_stem}_prospects.inp"
        prospects_inp_path.write_text(prospects_text, encoding="utf-8", newline="\n")

        # make include_inp
        create_include_inp(output_dir, file_num, keyword="_prospects")

        print(f"[INFO] Output INP: {prospects_inp_path.resolve()}")

    print("[INFO] === update inp end ===")


if __name__ == "__main__":

    calc_coordinates = False

    t0 = time.perf_counter()

    # ファイルフォルダの有無をチェック
    file_folder_exsist_check()

    if calc_coordinates:
        # csvデータにより節点座標の作成
        input_csv_path = search_file(csv_dir, file_extension=".csv")
        output_csv_path = calc_coordinates_from_displacement(input_csv_path, output_dir)
    else:
        output_csv_path = output_dir / "output.csv"

    # Nodeファイルの座標を更新
    update_inp(output_csv_path, output_dir)

    print(f"[INFO] Total elapsed: {time.perf_counter() - t0:.3f} sec")
