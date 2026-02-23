# main.py
import time
import traceback
import sys
from pathlib import Path

from calc_coordinates import calc_coordinates_from_displacement
from update_inp import update_inp
from extract_node_element_inp import extract_node_element_inp


def exe_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


def preflight_check() -> tuple[Path, Path, Path]:
    """
    実行前に必要なフォルダ/ファイルを一括チェックする。
    戻り値: (input_csv_path, inp_path, output_dir)
    """
    base = exe_dir()
    input_dir = base / "input"
    inp_dir = base / "inp"
    output_dir = base / "output"

    # フォルダ存在チェック
    if not input_dir.exists():
        raise FileNotFoundError(f"inputフォルダが見つかりません: {input_dir}")
    if not inp_dir.exists():
        raise FileNotFoundError(f"inpフォルダが見つかりません: {inp_dir}")

    # 入力CSV（input/*.csv）が1つ以上あるか
    csv_files = sorted(input_dir.glob("*.csv"))
    if not csv_files:
        raise FileNotFoundError(f"CSVが見つかりません: {input_dir}/*.csv")
    input_csv_path = csv_files[0]

    # inp（inp/*.inp）がちょうど1つか
    inp_files = sorted(inp_dir.glob("*.inp"))
    if len(inp_files) == 0:
        raise FileNotFoundError(f"inpが見つかりません: {inp_dir}/*.inp")
    if len(inp_files) > 1:
        names = ", ".join(p.name for p in inp_files)
        raise RuntimeError(f"inpが複数あります（1つにしてください）: {names}")
    inp_path = inp_files[0]

    # output は無ければ作成
    output_dir.mkdir(parents=True, exist_ok=True)

    # 参考情報を表示
    print("-" * 60)
    print(f"[CHECK] input csv : {input_csv_path.resolve()}")
    print(f"[CHECK] inp file  : {inp_path.resolve()}")
    print(f"[CHECK] output dir: {output_dir.resolve()}")
    print("-" * 60)

    return input_csv_path, inp_path, output_dir


def main():
    preflight_check()  # ※追加
    t0 = time.perf_counter()
    out_csv = calc_coordinates_from_displacement()  # ※修正（戻り値を使う）
    update_inp(csv_path=out_csv)  # ※修正

    inp_path = Path("output/updated.inp")
    out_path = Path("output/updated_node_element.inp")  # 出力inp
    extract_node_element_inp(inp_path, out_path)
    print(f"[INOF] Saved: {out_path.resolve()}")

    print(f"[TIME] pipeline total      : {time.perf_counter() - t0:8.3f} s")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        traceback.print_exc()
        input("エラー発生。Enterで終了します...")
    else:
        input("Enterで終了します...")
