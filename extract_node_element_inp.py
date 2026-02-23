from __future__ import annotations

from pathlib import Path


def extract_node_element_inp(
    inp_path: Path,
    out_path: Path,
    *,
    keep_comments: bool = True,
    keep_blank_lines: bool = True,
    add_header: bool = True,
) -> None:
    """
    inpファイルから *NODE と *ELEMENT のセクションだけを抽出して out_path に保存する。

    仕様:
    - セクション開始: 行頭が '*' で始まり、キーワードが NODE / ELEMENT のとき
      (例: '*NODE' / '*NODE, NSET=...' / '*Element, type=...') いずれも対象
    - セクション終了: 次の '*' で始まるキーワード行が来たら終了
    - コメント行 '**' は keep_comments=True ならセクション内で保持
    - 空行は keep_blank_lines=True ならセクション内で保持
    """
    lines = inp_path.read_text(encoding="utf-8", errors="replace").splitlines(keepends=False)

    out_lines: list[str] = []
    in_target = False

    if add_header:
        out_lines.append("** Extracted *NODE and *ELEMENT only")
        out_lines.append(f"** Source: {inp_path.name}")

    for line in lines:
        stripped = line.strip()

        # 空行
        if not stripped:
            if in_target and keep_blank_lines:
                out_lines.append(line)
            continue

        # コメント
        if stripped.startswith("**"):
            if in_target and keep_comments:
                out_lines.append(line)
            continue

        # キーワード行（*で始まる）
        if stripped.startswith("*"):
            # パラメータを除去してキーワードだけ取り出す
            # 例: "*NODE, NSET=A" -> "*NODE"
            key = stripped.split(",", 1)[0].strip().upper()

            if key in ("*NODE", "*ELEMENT"):
                in_target = True
                out_lines.append(line)  # 元の行（パラメータ含む）をそのまま残す
            else:
                in_target = False
            continue

        # データ行（NODE/ELEMENT セクション内のみ出力）
        if in_target:
            out_lines.append(line)

    # 末尾に改行を付けて保存（inpとして扱いやすい）
    out_text = "\n".join(out_lines) + "\n"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(out_text, encoding="utf-8")


if __name__ == "__main__":
    inp_path = Path("../output/updated.inp")
    out_path = Path("../output/updated_node_element.inp")  # 出力inp
    extract_node_element_inp(inp_path, out_path)
    print(f"Saved: {out_path.resolve()}")