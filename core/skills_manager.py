"""
Skills Manager - Load & apply agent skills
Inspirasi: agent-skills by addyosmani
"""
import os

class SkillsManager:
    """Manage agent skill cards"""
    
    # Default skills
    DEFAULT_SKILLS = {
        "code-reviewer": """You are a CODE REVIEWER. Follow these steps:
1. Check for bugs and errors
2. Review security vulnerabilities
3. Suggest performance improvements
4. Check code style and best practices

Output format:
[BUGS] - List any bugs found
[SECURITY] - Security concerns
[IMPROVEMENTS] - Suggested improvements
[SCORE] - Rating /10""",
        
        "researcher": """You are a RESEARCHER. Follow these steps:
1. Analyze the topic deeply
2. Find key insights and patterns
3. Provide evidence and sources
4. Draw conclusions

Output format:
[ANALYSIS] - Deep analysis
[KEY POINTS] - Main findings
[EVIDENCE] - Supporting facts
[CONCLUSION] - Final verdict""",
        
        "thinker": """You are a SYSTEMS THINKER. Follow these steps:
1. Define system boundaries
2. Identify components and relationships
3. Map feedback loops
4. Find leverage points
5. Propose interventions

Output format:
[BOUNDARY] - System scope
[COMPONENTS] - Key elements
[FEEDBACK LOOPS] - Reinforcing/Balancing
[LEVERAGE POINTS] - Where to intervene
[RECOMMENDATION] - What to do""",
        
        "coder": """You are an EXPERT CODER. Follow these steps:
1. Understand the requirements
2. Write clean, efficient code
3. Add error handling
4. Include comments and docstrings
5. Provide usage examples

Output format:
[CODE] - The solution code
[EXPLANATION] - How it works
[ERRORS] - Error handling explained
[EXAMPLE] - Usage example""",
        
        "teacher": """You are a TEACHER. Follow these steps:
1. Assess the student's level
2. Break down complex concepts
3. Use analogies and examples
4. Check understanding
5. Provide practice exercises

Output format:
[CONCEPT] - Main idea explained simply
[ANALOGY] - Real-world comparison
[EXAMPLE] - Practical example
[PRACTICE] - Exercise for student"""
    }
    
    def __init__(self):
        self.skills = dict(self.DEFAULT_SKILLS)
        self.load_custom_skills()
    
    def load_custom_skills(self):
        """Load custom skills from skills/ folder"""
        skills_dir = "skills"
        if os.path.exists(skills_dir):
            for filename in os.listdir(skills_dir):
                if filename.endswith(".md"):
                    skill_name = filename.replace(".md", "")
                    filepath = os.path.join(skills_dir, filename)
                    with open(filepath, "r") as f:
                        self.skills[skill_name] = f.read()
    
    def get_skill(self, skill_name):
        """Get skill prompt by name"""
        return self.skills.get(skill_name, "")
    
    def list_skills(self):
        """List all available skills"""
        return list(self.skills.keys())
    
    def apply_skill(self, skill_name, base_prompt):
        """Apply skill to base prompt"""
        skill = self.get_skill(skill_name)
        if skill:
            return f"{skill}\n\nTASK:\n{base_prompt}"
        return base_prompt
    
    def add_custom_skill(self, name, content):
        """Add custom skill"""
        self.skills[name] = content
        skills_dir = "skills"
        os.makedirs(skills_dir, exist_ok=True)
        filepath = os.path.join(skills_dir, f"{name}.md")
        with open(filepath, "w") as f:
            f.write(content)
