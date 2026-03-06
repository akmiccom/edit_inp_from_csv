import time

from utils import search_file, timer, file_folder_exsist_check
from utils import inp_dir


def extract_star_rows(input_path, print_on=False):

    extract_rows = []
    element_row = None

    print("[INFO] === extract star rows start ===")
    print(f"[INFO] Input {input_path}")

    with timer("read inp"):
        with input_path.open("r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()

        for lineno, line in enumerate(lines):
            s = line.lstrip()
            row = line.rstrip("\n")

            if lineno % 100000 == 0 and print_on:
                print(lineno, row)

            if s.startswith("*NODE,"):
                extract_rows.append((lineno, row))

            elif s.startswith("*ELEMENT,") and element_row is None:
                element_row = (lineno, row)

            elif s.startswith("*ELSET,"):
                if element_row is not None:
                    extract_rows.append(element_row)
                    element_row = None
                extract_rows.append((lineno, row))

    for start_row, end_row in zip(extract_rows, extract_rows[1:]):
        if "*NODE," in start_row[1] or "*ELEMENT," in start_row[1]:
            print(f"[INFO] {start_row}, {end_row}")

    print("[INFO] === extract star rows end ===")
    
    return lines, extract_rows


if __name__ == "__main__":

    t0 = time.perf_counter()

    file_folder_exsist_check()

    input_path = search_file(inp_dir, file_extension=".inp")
    lines, extract_rows = extract_star_rows(input_path, print_on=False)

    print(f"[INFO] Total elapsed: {time.perf_counter() - t0:.3f} sec")
