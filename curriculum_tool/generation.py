import json
from openai import OpenAI


SYSTEM_PROMPT = (
    "You are a curriculum designer. "
    "You design teaching flows using the structure: "
    "Curiosity → Observation → Aha Moment → Practical Application → Next Steps. "
    "You must respond with STRICT JSON only, no markdown, no comments."
)


USER_TEMPLATE = """
Create a JSON object for a curriculum on this topic: "{topic}".

Structure:

{{
  "curriculum": {{
    "version": "1.0",
    "topic": "{topic}",
    "metadata": {{
      "intended_audience": "beginners",
      "mode": "hybrid",
      "estimated_duration_minutes": 45,
      "prerequisites": []
    }},
    "levels": [
      {{
        "level_id": "beginner",
        "title": "{topic} – Beginner",
        "modules": [
          {{
            "module_id": "mod1",
            "module_title": "Core introduction to {topic}",
            "curiosity_phase": {{
              "hook_type": "surprising_output",
              "hook_script": "",
              "visual_or_demo": "",
              "key_question": ""
            }},
            "observation_phase": {{
              "baseline_demo": {{
                "description": "",
                "steps": [],
                "expected_output": ""
              }},
              "micro_experiments": []
            }},
            "aha_phase": {{
              "goal": "",
              "core_insight": "",
              "supporting_explanation": "",
              "simple_definition": "",
              "analogy_or_visual": ""
            }},
            "practical_application": {{
              "goal": "",
              "mini_project_title": "",
              "context": "",
              "steps": [],
              "success_criteria": ""
            }},
            "next_steps": {{
              "goal": "",
              "beginner": {{
                "description": "",
                "example_task": ""
              }},
              "intermediate": {{
                "description": "",
                "example_task": ""
              }},
              "advanced": {{
                "description": "",
                "example_task": ""
              }}
            }}
          }}
        ]
      }}
    ]
  }}
}}

Fill all empty strings/arrays with meaningful, concrete content for this topic.
Follow the Curiosity → Observation → Aha → Practical → Next Steps logic in each section.
Return ONLY the JSON, no explanation.
"""


def generate_curriculum_json(topic: str, model: str, client: OpenAI) -> dict:
    user_message = USER_TEMPLATE.format(topic=topic)

    response = client.responses.create(
        model=model,
        instructions=SYSTEM_PROMPT,
        input=user_message,
        response_format={"type": "json_object"},
    )

    return json.loads(response.output_text)
