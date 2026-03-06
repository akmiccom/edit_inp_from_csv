import time

from utils import search_file, file_folder_exsist_check
from utils import csv_dir, inp_dir, output_dir
from extract_star_rows import extract_star_rows
from extraxct_nodes_elements import split_inp
from calc_coordinates import calc_coordinates_from_displacement
from update_inp import update_inp


def main():

    print("[INFO] ===== main start =====")

    t0 = time.perf_counter()

    # ファイルフォルダの有無をチェック
    file_folder_exsist_check()

    # inpファイルを Node, Element のみ抽出して別名保存
    input_path = search_file(inp_dir, file_extension=".inp")
    lines, extract_rows = extract_star_rows(input_path, print_on=False)
    split_inp(output_dir, lines, extract_rows)

    # csvデータにより節点座標の作成
    input_csv_path = search_file(csv_dir, file_extension=".csv")
    output_csv_path = calc_coordinates_from_displacement(input_csv_path, output_dir)

    # Nodeファイルの座標を更新
    update_inp(output_csv_path, output_dir)

    print(f"[INFO] Total elapsed: {time.perf_counter() - t0:.3f} sec")
    print("[INFO] ===== main end =====")


if __name__ == "__main__":

    try:
        main()
    except Exception as e:
        print(f"[ERROR] {e}")
    finally:
        input("\nEnterキーを押すと終了します...")