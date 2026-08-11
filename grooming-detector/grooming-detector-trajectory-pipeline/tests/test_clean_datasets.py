"""Tests for clean_datasets.py — the one-shot CSV repair preprocessor."""

import pandas as pd

from clean_datasets import clean_file, read_repaired


def test_read_repaired_rejoins_unquoted_commas(tmp_path):
    p = tmp_path / "src.csv"
    p.write_text(
        "convo_id,line,author,text,is_predator,is_suspicious,image_type\n"
        "1,1,user1,hello there,0,0,none\n"
        "1,2,user2,GG @user1, you just leveled up!,0,0,none\n"
        "1,3,user3,oh, wait, what?,0,0,none\n",
        encoding="utf-8",
    )
    header, rows = read_repaired(p)
    assert header == ["convo_id", "line", "author", "text",
                      "is_predator", "is_suspicious", "image_type"]
    assert len(rows) == 3
    assert all(len(r) == 7 for r in rows)
    assert "GG @user1" in rows[1][3] and "leveled up" in rows[1][3]
    assert rows[2][3].count(",") >= 2  # 'oh, wait, what?'


def test_clean_file_writes_quoted_output_and_pandas_reads_it(tmp_path):
    p = tmp_path / "src.csv"
    p.write_text(
        "convo_id,line,author,text,is_predator,is_suspicious,image_type\n"
        "1,1,user1,hello there,0,0,none\n"
        "1,2,user2,GG @user1, you just leveled up!,0,0,none\n",
        encoding="utf-8",
    )
    clean_file(p, in_place=True)
    # Backup exists.
    assert p.with_suffix(p.suffix + ".bak").exists()
    # Plain pandas now reads it without column-shifting.
    df = pd.read_csv(p)
    assert len(df) == 2
    assert df["convo_id"].nunique() == 1
    assert "GG @user1" in df.loc[1, "text"]


def test_clean_file_preserves_already_quoted_rows(tmp_path):
    p = tmp_path / "good.csv"
    p.write_text(
        'convo_id,line,author,text,is_predator,is_suspicious\n'
        '1,1,a,"already, quoted",0,0\n'
        '1,2,b,plain text,0,0\n',
        encoding="utf-8",
    )
    clean_file(p, in_place=True)
    df = pd.read_csv(p)
    assert df.loc[0, "text"] == "already, quoted"
    assert df.loc[1, "text"] == "plain text"
