#!/usr/bin/env python3
"""对原创中文小说做表层节奏诊断；不计算文风相似度。"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from statistics import median


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

METAPHOR = re.compile(r"像是|仿佛|似的")
SENTENCES = re.compile(r"[。！？!?…]+")
SLOGAN = re.compile(r"(?:改写命运|守护所有人|向命运宣战|逆天改命)")
EXPLAIN = re.compile(r"(?:眼泪|哭了|流泪).{0,35}(?:因为|这说明|原来是因为)")
CONTRAST = re.compile(r"不是[^，。！？；\n]{1,24}[，,]\s*(?:而)?是")


def analyse(source: str) -> dict:
    # Markdown headings describe the artifact; they are not prose paragraphs.
    body = "\n".join(
        line for line in source.splitlines()
        if not re.match(r"^\s{0,3}#{1,6}\s+", line)
    ).strip()
    chars = len(re.sub(r"\s", "", body))
    paragraphs = [p.strip() for p in body.splitlines() if len(p.strip()) > 1]
    sentences = [s.strip() for s in SENTENCES.split(body) if 2 < len(s.strip()) < 500]
    denom = max(chars, 1)

    def per_10000(count: int) -> float:
        return round(count / denom * 10000, 1)

    result = {
        "characters": chars,
        "paragraphs": len(paragraphs),
        "median_paragraph_length": round(median(map(len, paragraphs)), 1) if paragraphs else 0,
        "short_paragraph_percent": round(
            sum(len(p) <= 15 for p in paragraphs) / len(paragraphs) * 100, 1
        ) if paragraphs else 0,
        "mean_sentence_length": round(
            sum(map(len, sentences)) / len(sentences), 1
        ) if sentences else 0,
        "exclamations_per_10000": per_10000(body.count("！") + body.count("!")),
        "questions_per_10000": per_10000(body.count("？") + body.count("?")),
        "ellipses_per_10000": per_10000(body.count("……")),
        "explicit_similes_per_10000": per_10000(len(METAPHOR.findall(body))),
        "contrast_templates": len(CONTRAST.findall(body)),
        "slogan_candidates": len(SLOGAN.findall(body)),
        "emotion_explanation_candidates": len(EXPLAIN.findall(body)),
        "notes": [],
    }

    notes = result["notes"]
    if chars < 1500:
        notes.append("短于 1500 字：密度与段落统计仅供参考。")
    else:
        if result["short_paragraph_percent"] > 22:
            notes.append("超短段偏多；检查短句是否都承担了转折或强调。")
        if result["exclamations_per_10000"] > 80:
            notes.append("感叹号偏密；检查人物是否一直处于同一种高音量。")
        if result["ellipses_per_10000"] > 55:
            notes.append("省略号偏密；检查迟疑是否能由动作或沉默表达。")
    if result["contrast_templates"] > 2:
        notes.append("“不是……而是……”模板重复，建议逐处审读。")
    if result["slogan_candidates"]:
        notes.append("存在宣言式高潮候选；检查能否由具体选择承担情绪。")
    if result["emotion_explanation_candidates"]:
        notes.append("存在解释哭泣原因的候选；检查是否需要留白。")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", type=Path, help="UTF-8 小说稿件")
    parser.add_argument("--json", action="store_true", help="输出机器可读 JSON")
    args = parser.parse_args()
    reports = {}
    for path in args.paths:
        try:
            reports[str(path)] = analyse(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError) as exc:
            print(f"无法读取 {path}: {exc}", file=sys.stderr)
            return 2
    if args.json:
        print(json.dumps(reports, ensure_ascii=False, indent=2))
    else:
        for path, report in reports.items():
            print(f"{path}: {report['characters']} 字，{report['paragraphs']} 段")
            print(
                f"  段落中位数 {report['median_paragraph_length']}，"
                f"短段 {report['short_paragraph_percent']}%，"
                f"平均句长 {report['mean_sentence_length']}"
            )
            print(
                f"  每万字：感叹号 {report['exclamations_per_10000']}，"
                f"问号 {report['questions_per_10000']}，"
                f"省略号 {report['ellipses_per_10000']}，"
                f"显式比喻 {report['explicit_similes_per_10000']}"
            )
            for note in report["notes"]:
                print(f"  提示：{note}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
