import time

from utils import search_file, timer
from utils import inp_dir, output_dir
from utils import file_folder_exsist_check, create_include_inp
from extract_star_rows import extract_star_rows


def split_inp(output_dir, lines, extract_rows):

    print("[INFO] === split inp start ===")

    file_num = 1

    for start_row, end_row in zip(extract_rows, extract_rows[1:]):
        start_lineno, start_text = start_row
        end_lineno, _ = end_row

        start_key = start_text.lstrip()

        if not (start_key.startswith("*NODE,") or start_key.startswith("*ELEMENT,")):
            continue

        out_lines = lines[start_lineno:end_lineno]
        
        if start_key.startswith("*ELEMENT,"):
            header = "*ELEMENT, TYPE=C3D10, ELSET=ALL\n"

            out_lines_num_only = [header]
            for line in out_lines:
                if not line.lstrip().startswith("*ELEMENT"):
                    out_lines_num_only.append(line)

            output_path = output_dir / f"element_{file_num:02}.inp"

            with timer(f"output element_{file_num:02}.inp"):
                with open(output_path, mode="w") as f:
                    f.writelines(out_lines_num_only)

            file_num +=1
            
        else:
            create_include_inp(output_dir, file_num, keyword="")
            output_path = output_dir / f"node_{file_num:02}.inp"
            with timer(f"output node_{file_num:02}.inp"):
                with open(output_path, mode="w") as f:
                    f.writelines(out_lines)
        

    print("[INFO] === split inp end ===")


if __name__ == "__main__":

    t0 = time.perf_counter()

    file_folder_exsist_check()

    input_path = search_file(inp_dir, file_extension=".inp")
    lines, extract_rows = extract_star_rows(input_path, print_on=False)

    split_inp(output_dir, lines, extract_rows)

    print(f"[INFO] Total elapsed: {time.perf_counter() - t0:.3f} sec")
