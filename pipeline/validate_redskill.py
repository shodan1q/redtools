"""
validate_redskill —— RedSkill（小红书技能市场）上传就绪校验器。

把 RedSkill 上传/审核的硬规则固化成可复跑的检查，逐个扫描 redskill/ 下的技能包，
明确报告每个能不能上传、卡在哪。以后每加一个市场版 skill，跑一遍就知道过不过。

规则依据（2026-07 内测）：
- 只收 Markdown/TXT；独立的 .py/.yaml/.json 等脚本/配置文件会被过滤 → 技能包必须纯 .md
- frontmatter 必备 name + description；name 仅小写字母/数字/连字符，≤64 字，
  禁下划线与保留词（anthropic/claude）
- 站内正文严禁外链导流；GitHub 等来源填在上传时的「来源」字段，不进正文
- 敏感/导流词（微信/加微/私信/公众号/二维码…）命中即高风险

用法：
    python3 pipeline/validate_redskill.py            # 校验 redskill/ 下全部技能包
    python3 pipeline/validate_redskill.py <dir>...   # 校验指定技能目录
退出码：全部通过=0，有阻断项=1。
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REDSKILL_DIR = os.path.join(ROOT, "redskill")

NAME_RE = re.compile(r"^[a-z0-9-]{1,64}$")
RESERVED = ("anthropic", "claude")
URL_RE = re.compile(r"https?://[^\s)>\"']+")
# 导流/敏感词：命中即人工复核高风险
DIVERT_WORDS = ["微信", "加微", "vx", "威信", "私信我", "私聊", "公众号",
                "二维码", "扫码", "抖音", "b站", "淘宝", "闲鱼", "qq群", "微信群"]


def _split_frontmatter(text):
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
    if not m:
        return None, text
    fm = {}
    for line in m.group(1).splitlines():
        km = re.match(r"^([A-Za-z_][\w-]*):\s*(.*)$", line)
        if km:
            fm[km.group(1)] = km.group(2).strip()
    return fm, m.group(2)


def validate_skill(skill_dir):
    """返回 (errors, warnings)。errors 非空即不能上传。"""
    errors, warnings = [], []
    name_expected = os.path.basename(skill_dir.rstrip("/"))

    files = [f for f in os.listdir(skill_dir)
             if os.path.isfile(os.path.join(skill_dir, f))]
    non_md = [f for f in files if not f.lower().endswith((".md", ".txt"))]
    if non_md:
        errors.append(f"含非 Markdown 文件（会被平台过滤）：{', '.join(non_md)}")

    skill_md = os.path.join(skill_dir, "SKILL.md")
    if not os.path.exists(skill_md):
        errors.append("缺少 SKILL.md")
        return errors, warnings

    text = open(skill_md, encoding="utf-8").read()
    fm, body = _split_frontmatter(text)
    if fm is None:
        errors.append("缺少 YAML frontmatter（--- 包裹的头部）")
        return errors, warnings

    name = fm.get("name", "")
    if not name:
        errors.append("frontmatter 缺少 name")
    else:
        if not NAME_RE.match(name):
            errors.append(f"name「{name}」非法：仅限小写字母/数字/连字符、≤64 字、禁下划线")
        if any(w in name.lower() for w in RESERVED):
            errors.append(f"name「{name}」含保留词（{'/'.join(RESERVED)}）")
        if name != name_expected:
            warnings.append(f"name「{name}」与目录名「{name_expected}」不一致")

    desc = fm.get("description", "")
    if not desc:
        errors.append("frontmatter 缺少 description")
    elif len(desc) < 20:
        warnings.append("description 过短，触发准确度可能低")

    # 正文外链 = 导流高风险（GitHub 等来源应填「来源」字段，不进正文）
    for url in URL_RE.findall(body):
        errors.append(f"正文含外链（导流风险，移到上传「来源」字段）：{url}")
    for w in DIVERT_WORDS:
        if w in body:
            warnings.append(f"正文含疑似导流/敏感词「{w}」，建议复核")

    return errors, warnings


def main(argv):
    if argv:
        dirs = [os.path.abspath(d) for d in argv]
    else:
        dirs = sorted(
            os.path.join(REDSKILL_DIR, d) for d in os.listdir(REDSKILL_DIR)
            if os.path.isdir(os.path.join(REDSKILL_DIR, d))
        )

    all_ok = True
    print(f"RedSkill 上传校验 · 共 {len(dirs)} 个技能包\n" + "=" * 44)
    for d in dirs:
        errors, warnings = validate_skill(d)
        name = os.path.basename(d.rstrip("/"))
        if errors:
            all_ok = False
            print(f"\n❌ {name} —— 不能上传")
            for e in errors:
                print(f"   × {e}")
        else:
            print(f"\n✅ {name} —— 可上传")
        for w in warnings:
            print(f"   ⚠ {w}")

    print("\n" + "=" * 44)
    print("全部通过，可提交上传。" if all_ok else "存在阻断项，修复后再传。")
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
