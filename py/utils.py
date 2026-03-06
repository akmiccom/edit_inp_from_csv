from __future__ import annotations

import sys
import time
from contextlib import contextmanager
from pathlib import Path


def create_include_inp(output_dir, n, keyword=""):
    output_dir = Path(output_dir)
    text = (
        f"*HEADING\n"
        f"** main_{n:02}{keyword}.inp\n"
        f"** Mesh include file (nodes + elements)\n"
        f"\n"
        f"*PREPRINT, ECHO=NO, MODEL=NO, HISTORY=NO, CONTACT=NO\n"
        f"\n"
        f"*PART, NAME=main_{n:02}{keyword}\n"
        f"*INCLUDE, INPUT=node_{n:02}{keyword}.inp\n"
        f"*INCLUDE, INPUT=element_{n:02}.inp\n"
        f"*END PART\n"
        f"\n"
        f"*ASSEMBLY, NAME=ASSEMBLY\n"
        f"*INSTANCE, NAME=main_{n:02}{keyword}, PART=main_{n:02}{keyword}\n"
        f"*END INSTANCE\n"
        f"*END ASSEMBLY\n"
    )
    output_path = output_dir / f"main_{n:02}{keyword}.inp"
    output_path.write_text(text, encoding="utf-8", newline="\n")

    return output_path


def exe_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent.parent
    return Path(__file__).resolve().parent.parent


@contextmanager
def timer(label: str):
    t0 = time.perf_counter()
    yield
    t1 = time.perf_counter()
    print(f"[TIME] {label:<20} : {t1 - t0:8.3f} s")


def search_file(serch_dir, file_extension):
    search_files = sorted(serch_dir.glob(f"*{file_extension}"))
    if not search_files:
        raise FileNotFoundError(
            f"{file_extension} ファイルが見つかりません: {serch_dir}/**{file_extension}"
        )
    search_path = search_files[0]
    return search_path


base = exe_dir()
csv_dir = base / "csv"
inp_dir = base / "inp"
output_dir = base / "output"


def file_folder_exsist_check():

    sec = 0.5
    print("[INFO] === Pre-check start ===")
    time.sleep(sec)
    print(f"[INFO] csv    : {csv_dir.resolve()}")
    time.sleep(sec)
    print(f"[INFO] inp    : {inp_dir.resolve()}")
    time.sleep(sec)
    print(f"[INFO] output : {output_dir.resolve()}")
    time.sleep(sec)

    # Create the directory if it does not exist
    output_dir.mkdir(parents=True, exist_ok=True)

    # check if folder exsist
    if not inp_dir.exists():
        raise FileNotFoundError(f"inpフォルダが見つかりません: {inp_dir}")
    if not csv_dir.exists():
        raise FileNotFoundError(f"csvフォルダが見つかりません: {csv_dir}")

    if not inp_dir.is_dir():
        raise NotADirectoryError(f"inp はフォルダではありません: {inp_dir}")
    if not csv_dir.is_dir():
        raise NotADirectoryError(f"csv はフォルダではありません: {csv_dir}")
    if not output_dir.is_dir():
        raise NotADirectoryError(f"output はフォルダではありません: {output_dir}")

    # check if file exsist
    inp_files = sorted(inp_dir.glob("*.inp"))
    if len(inp_files) == 0:
        raise FileNotFoundError(f"{inp_dir} に .inp が見つかりません")
    # 1つだけ想定なら複数はエラーにする（必要に応じて方針変更）
    if len(inp_files) > 1:
        raise FileExistsError(
            f"{inp_dir} に .inp が複数あります: {[p.name for p in inp_files]}"
        )

    csv_files = sorted(csv_dir.glob("*.csv"))
    if len(csv_files) == 0:
        raise FileNotFoundError(f"{csv_dir} に .csv が見つかりません")
    if len(csv_files) > 1:
        raise FileExistsError(
            f"{inp_dir} に .csv が複数あります: {[p.name for p in csv_files]}"
        )

    print("[INFO] フォルダ/ファイルチェック完了。実行可能です。")
    time.sleep(sec)
    print("[INFO] === Pre-check end ===")
    time.sleep(sec)


if __name__ == "__main__":

    file_folder_exsist_check()
