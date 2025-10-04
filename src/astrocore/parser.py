
"""Simple parser to extract structured data from read01.txt content.

This module contains a lightweight, forward-compatible parser. It
provides a heuristic implementation that can be used as a fallback if
an enhanced NLP pipeline is not available.
"""
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional
import re


@dataclass
class Goal:
    title: str
    description: str


@dataclass
class MaterialSpec:
    name: str
    features: Optional[str] = None
    impact: Optional[str] = None
    pore_size: Optional[str] = None
    surface_property: Optional[str] = None
    mechanical: Optional[str] = None


def _extract_pore_size(text: str) -> Optional[str]:
    m = re.search(r"(\d{1,3}\s*-\s*\d{1,3}\s*kDa)", text, flags=re.IGNORECASE)
    if m:
        return m.group(1)
    # also try ranges like 50-100
    m2 = re.search(r"(\d{1,3}\s*-\s*\d{1,3})\s*(kDa)?", text, flags=re.IGNORECASE)
    if m2:
        return m2.group(1) + (" kDa" if m2.group(2) else "")
    return None


def parse_text(text: str) -> Dict:
    """Parse the provided text and return structured summary.

    Heuristic parser that extracts:
    - project core goals (energy and waste)
    - material specifications (name + optional properties)
    - monitoring methods list
    """
    summary = {"goals": [], "materials": [], "monitoring": []}

    # Goals
    if "能量供给" in text or "能量辅助" in text:
        summary["goals"].append(asdict(Goal("能量辅助", "对抗线粒体功能障碍，优化代谢，保证 ATP 供应")))
    if "有害物质清除" in text or "废物清除" in text:
        summary["goals"].append(asdict(Goal("有害物质清除", "增强细胞内外废物处理，防止有毒蛋白质积累")))

    # Materials table (heuristic detection)
    materials_found: List[MaterialSpec] = []
    known = [
        ("Alginate", ["海藻酸盐", "Alginate"]),
        ("PEG", ["聚乙二醇", "PEG"]),
        ("PES", ["聚醚砜", "PES"]),
        ("PAN", ["聚丙烯腈", "PAN"]),
    ]
    for canonical, aliases in known:
        for a in aliases:
            if a in text:
                ms = MaterialSpec(name=canonical)
                ms.features = "提到在文件中"
                ms.impact = "见文档"
                ms.pore_size = _extract_pore_size(text)
                # surface hints
                if "亲水性" in text or "亲水" in text:
                    ms.surface_property = "亲水性"
                if "中性电荷" in text or "中性" in text:
                    ms.surface_property = (ms.surface_property + ", 中性电荷") if ms.surface_property else "中性电荷"
                # mechanical
                if "弹性" in text or "稳定性" in text:
                    ms.mechanical = "弹性与稳定性要求"
                materials_found.append(ms)
                break

    summary["materials"] = [asdict(m) for m in materials_found]

    # Monitoring: look for canonical keywords
    monitors = []
    for kw in ["MRS", "EEG", "MEG", "PET", "MRI", "AQP4", "脑电图", "MRS"]:
        if kw in text:
            monitors.append(kw)
    summary["monitoring"] = monitors

    return summary


def summarize_to_json(text: str) -> Dict:
    return parse_text(text)
