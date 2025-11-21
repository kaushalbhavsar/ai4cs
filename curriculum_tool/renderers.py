from typing import Dict


def pick_first_module(curriculum: dict) -> Dict[str, dict]:
    levels = curriculum["curriculum"]["levels"]
    level = levels[0]
    module = level["modules"][0]
    return {
        "level": level,
        "module": module,
        "topic": curriculum["curriculum"]["topic"],
    }


def render_youtube_script(data: dict) -> str:
    topic = data["topic"]
    mod = data["module"]

    cur = mod["curiosity_phase"]
    obs = mod["observation_phase"]
    aha = mod["aha_phase"]
    app = mod["practical_application"]
    nxt = mod["next_steps"]

    lines = []

    lines.append(f"TITLE: {topic} – From Curiosity to Aha\n")

    lines.append("[SECTION 1: CURIOSITY]\n")
    lines.append(f"- Hook: {cur['hook_script']}")
    if cur.get("visual_or_demo"):
        lines.append(f"- Visual/Demo: {cur['visual_or_demo']}")
    lines.append(f"- Key Question: {cur['key_question']}\n")

    lines.append("[SECTION 2: OBSERVATION]\n")
    lines.append(f"Baseline demo: {obs['baseline_demo']['description']}")
    lines.append("Steps:")
    for step in obs["baseline_demo"]["steps"]:
        lines.append(f"  - {step}")
    lines.append(f"Expected output: {obs['baseline_demo']['expected_output']}\n")

    if obs["micro_experiments"]:
        lines.append("Micro experiments:")
        for exp in obs["micro_experiments"]:
            lines.append(f"  * {exp['experiment_title']}")
            lines.append(f"    - Instruction: {exp['instruction']}")
            lines.append(f"    - Observation prompt: {exp['observation_prompt']}")
            lines.append(f"    - Expected change: {exp['expected_change']}")
        lines.append("")

    lines.append("[SECTION 3: AHA MOMENT]\n")
    lines.append(f"Goal: {aha['goal']}")
    lines.append(f"Core insight: {aha['core_insight']}")
    lines.append(f"Explanation: {aha['supporting_explanation']}")
    lines.append(f"Simple definition: {aha['simple_definition']}")
    if aha.get("analogy_or_visual"):
        lines.append(f"Analogy: {aha['analogy_or_visual']}\n")

    lines.append("[SECTION 4: PRACTICAL APPLICATION]\n")
    lines.append(f"Mini-project: {app['mini_project_title']}")
    lines.append(f"Context: {app['context']}")
    lines.append("Steps:")
    for step in app["steps"]:
        lines.append(f"  - {step}")
    lines.append(f"Success criteria: {app['success_criteria']}\n")

    lines.append("[SECTION 5: NEXT STEPS]\n")
    lines.append(f"Overall goal: {nxt['goal']}")
    lines.append(f"Beginner: {nxt['beginner']['description']} -> {nxt['beginner']['example_task']}")
    lines.append(f"Intermediate: {nxt['intermediate']['description']} -> {nxt['intermediate']['example_task']}")
    lines.append(f"Advanced: {nxt['advanced']['description']} -> {nxt['advanced']['example_task']}\n")

    return "\n".join(lines)


def render_slides_outline(data: dict) -> str:
    topic = data["topic"]
    mod = data["module"]
    cur = mod["curiosity_phase"]
    obs = mod["observation_phase"]
    aha = mod["aha_phase"]
    app = mod["practical_application"]
    nxt = mod["next_steps"]

    lines = []
    lines.append(f"# Slides Outline – {topic}\n")

    lines.append("## Slide 1 – Curiosity")
    lines.append(f"- Hook: {cur['hook_script']}")
    lines.append(f"- Visual/Demo: {cur.get('visual_or_demo', '')}")
    lines.append(f"- Question: {cur['key_question']}\n")

    lines.append("## Slide 2–3 – Observation")
    lines.append(f"- Baseline demo: {obs['baseline_demo']['description']}")
    lines.append("- Steps:")
    for step in obs["baseline_demo"]["steps"]:
        lines.append(f"  - {step}")
    lines.append(f"- Expected output: {obs['baseline_demo']['expected_output']}")
    if obs["micro_experiments"]:
        lines.append("- Micro experiments:")
        for exp in obs["micro_experiments"]:
            lines.append(f"  - {exp['experiment_title']}: {exp['instruction']}")

    lines.append("\n## Slide 4 – Aha Moment")
    lines.append(f"- Goal: {aha['goal']}")
    lines.append(f"- Core insight: {aha['core_insight']}")
    lines.append(f"- Simple definition: {aha['simple_definition']}")
    if aha.get("analogy_or_visual"):
        lines.append(f"- Analogy: {aha['analogy_or_visual']}\n")

    lines.append("## Slide 5–6 – Practical Application")
    lines.append(f"- Mini-project: {app['mini_project_title']}")
    lines.append(f"- Context: {app['context']}")
    lines.append("- Steps:")
    for step in app["steps"]:
        lines.append(f"  - {step}")
    lines.append(f"- Success criteria: {app['success_criteria']}\n")

    lines.append("## Slide 7 – Next Steps")
    lines.append(f"- Beginner: {nxt['beginner']['example_task']}")
    lines.append(f"- Intermediate: {nxt['intermediate']['example_task']}")
    lines.append(f"- Advanced: {nxt['advanced']['example_task']}\n")

    return "\n".join(lines)


def render_handout(data: dict) -> str:
    topic = data["topic"]
    mod = data["module"]
    cur = mod["curiosity_phase"]
    obs = mod["observation_phase"]
    aha = mod["aha_phase"]
    app = mod["practical_application"]
    nxt = mod["next_steps"]

    lines = []
    lines.append(f"# {topic} – Session Handout\n")

    lines.append("## 1. Curiosity")
    lines.append(f"- Hook scenario: {cur['hook_script']}")
    lines.append(f"- Key question: {cur['key_question']}\n")

    lines.append("## 2. Observation")
    lines.append(f"- Baseline demo: {obs['baseline_demo']['description']}")
    lines.append("- Steps:")
    for step in obs["baseline_demo"]["steps"]:
        lines.append(f"  - {step}")
    lines.append(f"- Expected output: {obs['baseline_demo']['expected_output']}")
    if obs["micro_experiments"]:
        lines.append("- Experiments:")
        for exp in obs["micro_experiments"]:
            lines.append(f"  - {exp['experiment_title']}: {exp['instruction']}")
            lines.append(f"    → Notice: {exp['observation_prompt']}")
    lines.append("")

    lines.append("## 3. Aha Moment")
    lines.append(f"- Core idea: {aha['core_insight']}")
    lines.append(f"- Simple definition: {aha['simple_definition']}")
    if aha.get("analogy_or_visual"):
        lines.append(f"- Analogy: {aha['analogy_or_visual']}\n")

    lines.append("## 4. Practical Application")
    lines.append(f"- Mini-project: {app['mini_project_title']}")
    lines.append(f"- Context: {app['context']}")
    lines.append("- Steps:")
    for step in app["steps"]:
        lines.append(f"  - {step}")
    lines.append(f"- Success criteria: {app['success_criteria']}\n")

    lines.append("## 5. Next Steps")
    lines.append(f"- Beginner: {nxt['beginner']['description']} ({nxt['beginner']['example_task']})")
    lines.append(f"- Intermediate: {nxt['intermediate']['description']} ({nxt['intermediate']['example_task']})")
    lines.append(f"- Advanced: {nxt['advanced']['description']} ({nxt['advanced']['example_task']})\n")

    return "\n".join(lines)


def render_code_notes(data: dict) -> str:
    topic = data["topic"]
    mod = data["module"]
    cur = mod["curiosity_phase"]
    obs = mod["observation_phase"]
    app = mod["practical_application"]

    lines = []
    lines.append(f"# Code Notes – {topic}\n")

    lines.append("## Curiosity Demo")
    lines.append(f"- Idea: {cur['hook_script']}")
    lines.append(f"- Visual/Demo setup: {cur.get('visual_or_demo', '')}\n")

    lines.append("## Baseline Demo (Observation)")
    lines.append(f"- Description: {obs['baseline_demo']['description']}")
    lines.append("- Steps to implement:")
    for step in obs["baseline_demo"]["steps"]:
        lines.append(f"  - {step}")
    lines.append(f"- Expected output: {obs['baseline_demo']['expected_output']}\n")

    if obs["micro_experiments"]:
        lines.append("## Experiments")
        for exp in obs["micro_experiments"]:
            lines.append(f"- {exp['experiment_title']}")
            lines.append(f"  - Instruction: {exp['instruction']}")
            lines.append(f"  - What to highlight: {exp['observation_prompt']}\n")

    lines.append("## Final Mini-Project")
    lines.append(f"- Title: {app['mini_project_title']}")
    lines.append(f"- Context: {app['context']}")
    lines.append("- Implementation steps:")
    for step in app["steps"]:
        lines.append(f"  - {step}")
    lines.append(f"- Success criteria: {app['success_criteria']}\n")

    return "\n".join(lines)
