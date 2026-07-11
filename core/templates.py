"""
Prompt Templates Manager
Simpan & load template prompt
Inspirasi: NextChat
"""
import os
import json

class TemplateManager:
    """Manage prompt templates"""

    # Default templates
    DEFAULT_TEMPLATES = {
        "debug-code": {
            "name": "Debug Kode",
            "mode": "coding",
            "prompt": "Debug kode berikut. Cari bug, error, dan berikan solusi perbaikan:\n\n```\n{{code}}\n```",
            "description": "Debug dan perbaiki kode"
        },
        "explain-code": {
            "name": "Jelaskan Kode",
            "mode": "coding",
            "prompt": "Jelaskan kode berikut secara detail, line by line:\n\n```\n{{code}}\n```",
            "description": "Penjelasan kode detail"
        },
        "write-function": {
            "name": "Bikin Fungsi",
            "mode": "coding",
            "prompt": "Buat fungsi {{language}} untuk {{task}}. Sertakan error handling, type hints, dan contoh penggunaan.",
            "description": "Generate fungsi dengan best practices"
        },
        "research-topic": {
            "name": "Research Topik",
            "mode": "research",
            "prompt": "Lakukan riset mendalam tentang {{topic}}. Sertakan:\n- Definisi\n- Konsep kunci\n- Perkembangan terbaru\n- Pro & kontra\n- Kesimpulan",
            "description": "Riset mendalam suatu topik"
        },
        "compare-concepts": {
            "name": "Bandingkan Konsep",
            "mode": "research",
            "prompt": "Bandingkan {{concept1}} vs {{concept2}} dalam hal:\n- Definisi\n- Keunggulan\n- Kelemahan\n- Use case\n- Kesimpulan (mana yang lebih baik?)",
            "description": "Perbandingan dua konsep"
        },
        "system-design": {
            "name": "System Design",
            "mode": "thinking",
            "prompt": "Design sistem untuk {{system}}. Analisis dengan Systems Thinking:\n1. System boundary\n2. Components & interconnections\n3. Feedback loops\n4. Leverage points\n5. Rekomendasi",
            "description": "Analisis sistem kompleks"
        },
        "problem-solving": {
            "name": "Problem Solving",
            "mode": "thinking",
            "prompt": "Pecahkan masalah {{problem}} dengan step-by-step:\n1. Define the problem\n2. Root cause analysis\n3. Possible solutions\n4. Evaluation\n5. Recommendation",
            "description": "Pemecahan masalah terstruktur"
        },
        "quick-summary": {
            "name": "Ringkasan Cepat",
            "mode": "quick",
            "prompt": "Ringkas teks berikut dalam 3 poin utama:\n\n{{text}}",
            "description": "Ringkasan singkat"
        }
    }

    def __init__(self):
        self.templates = dict(self.DEFAULT_TEMPLATES)
        self.load_custom_templates()

    def load_custom_templates(self):
        """Load custom templates from templates/ folder"""
        templates_dir = "templates"
        if os.path.exists(templates_dir):
            for filename in os.listdir(templates_dir):
                if filename.endswith(".json"):
                    try:
                        filepath = os.path.join(templates_dir, filename)
                        with open(filepath, "r") as f:
                            custom = json.load(f)
                            if isinstance(custom, dict):
                                self.templates.update(custom)
                    except:
                        pass

    def get_template(self, template_id):
        """Get template by ID"""
        return self.templates.get(template_id, None)

    def list_templates(self, mode=None):
        """List templates, optional filter by mode"""
        if mode:
            return {k: v for k, v in self.templates.items() if v.get("mode") == mode}
        return self.templates

    def get_template_names(self, mode=None):
        """Get list of template names"""
        templates = self.list_templates(mode)
        return [(k, v["name"]) for k, v in templates.items()]

    def apply_template(self, template_id, variables=None):
        """Apply template dengan variable substitution"""
        template = self.get_template(template_id)
        if not template:
            return None

        prompt = template["prompt"]

        # Substitute variables {{var}}
        if variables:
            for key, value in variables.items():
                prompt = prompt.replace(f"{{{{{key}}}}}", str(value))

        return {
            "prompt": prompt,
            "mode": template.get("mode", "coding"),
            "name": template.get("name", "")
        }

    def add_custom_template(self, template_id, name, prompt, mode="coding", description=""):
        """Add custom template"""
        self.templates[template_id] = {
            "name": name,
            "mode": mode,
            "prompt": prompt,
            "description": description
        }
        self._save_custom()

    def remove_template(self, template_id):
        """Remove custom template (default tidak bisa dihapus)"""
        if template_id in self.DEFAULT_TEMPLATES:
            return False
        if template_id in self.templates:
            del self.templates[template_id]
            self._save_custom()
            return True
        return False

    def _save_custom(self):
        """Save custom templates to file"""
        os.makedirs("templates", exist_ok=True)
        
        # Hanya simpan yang BUKAN default
        custom = {k: v for k, v in self.templates.items() if k not in self.DEFAULT_TEMPLATES}
        
        filepath = os.path.join("templates", "custom_templates.json")
        with open(filepath, "w") as f:
            json.dump(custom, f, indent=2)
