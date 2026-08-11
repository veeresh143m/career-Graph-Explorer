import os
try:
    from neo4j import GraphDatabase, basic_auth, exceptions
except ImportError:  # pragma: no cover - fallback when dependency is unavailable
    GraphDatabase = None
    basic_auth = None
    exceptions = None

from dotenv import load_dotenv
load_dotenv()

COGNODB_URI = os.getenv("COGNODB_URI")
COGNODB_USER = os.getenv("COGNODB_USER", "cognodb")
COGNODB_PASSWORD = os.getenv("COGNODB_PASSWORD")

class QueryError(Exception):
    pass

class CognoDBClient:
    def __init__(self):
        self.driver = None
        self._fallback = False
        self._demo_data = {
            "roles": {
                "Data Analyst": {
                    "description": "Turns data into business insights.",
                    "skills": ["Python", "SQL", "Statistics"],
                    "prerequisites": ["Statistics"],
                    "courses": [{"name": "Python for Data Analysis", "provider": "Coursera"}],
                    "related_roles": ["Machine Learning Engineer"],
                },
                "Machine Learning Engineer": {
                    "description": "Builds models and automation systems.",
                    "skills": ["Python", "Machine Learning", "Statistics"],
                    "prerequisites": ["Python", "Statistics"],
                    "courses": [{"name": "Machine Learning Specialization", "provider": "Coursera"}],
                    "related_roles": ["Data Analyst"],
                },
            },
            "skills": {
                "Python": {
                    "description": "General-purpose programming language.",
                    "prerequisites": [],
                    "courses": [{"name": "Python for Data Analysis", "provider": "Coursera"}],
                    "roles": ["Data Analyst", "Machine Learning Engineer"],
                },
                "SQL": {
                    "description": "Query language for relational databases.",
                    "prerequisites": [],
                    "courses": [{"name": "SQL Bootcamp", "provider": "Udemy"}],
                    "roles": ["Data Analyst"],
                },
                "Statistics": {
                    "description": "Mathematical reasoning for data analysis.",
                    "prerequisites": [],
                    "courses": [{"name": "Statistics Fundamentals", "provider": "edX"}],
                    "roles": ["Data Analyst", "Machine Learning Engineer"],
                },
                "Machine Learning": {
                    "description": "Methods for training predictive models.",
                    "prerequisites": ["Python", "Statistics"],
                    "courses": [{"name": "Machine Learning Specialization", "provider": "Coursera"}],
                    "roles": ["Machine Learning Engineer"],
                },
            },
            "courses": {
                "Python for Data Analysis": {
                    "provider": "Coursera",
                    "description": "Learn Python for practical data analysis workflows.",
                    "skills": ["Python"],
                    "roles": ["Data Analyst"],
                },
                "SQL Bootcamp": {
                    "provider": "Udemy",
                    "description": "Learn core SQL skills for analytics.",
                    "skills": ["SQL"],
                    "roles": ["Data Analyst"],
                },
                "Machine Learning Specialization": {
                    "provider": "Coursera",
                    "description": "Advanced learning path for model building.",
                    "skills": ["Machine Learning", "Python"],
                    "roles": ["Machine Learning Engineer"],
                },
                "Statistics Fundamentals": {
                    "provider": "edX",
                    "description": "Foundational statistics for data work.",
                    "skills": ["Statistics"],
                    "roles": ["Data Analyst", "Machine Learning Engineer"],
                },
            },
        }

        if not COGNODB_URI or not COGNODB_PASSWORD or GraphDatabase is None or basic_auth is None:
            self._fallback = True
            return

        try:
            self.driver = GraphDatabase.driver(
                COGNODB_URI,
                auth=basic_auth(COGNODB_USER, COGNODB_PASSWORD),
            )
        except Exception:
            self._fallback = True

    def close(self):
        if self.driver is not None:
            self.driver.close()

    def _run(self, cypher, params=None):
        if self._fallback:
            return self._fallback_run(cypher, params or {})

        try:
            with self.driver.session() as session:
                result = session.run(cypher, params or {})
                return [record.data() for record in result]
        except exceptions.Neo4jError as exc:
            raise QueryError(f"Database query failed: {exc}")
        except Exception as exc:
            raise QueryError(f"Unable to reach CognoDB: {exc}")

    def _fallback_run(self, cypher, params=None):
        params = params or {}
        normalized = cypher.replace("\n", " ").strip()

        if "MATCH (r:Role)" in normalized and "RETURN r.name AS name" in normalized:
            return [{"name": name} for name in sorted(self._demo_data["roles"].keys())]

        if "MATCH (s:Skill)" in normalized and "RETURN s.name AS name" in normalized:
            return [{"name": name} for name in sorted(self._demo_data["skills"].keys())]

        if "MATCH (n) WHERE toLower(n.name) CONTAINS toLower" in normalized:
            term = (params.get("term") or "").lower()
            results = []
            for name in sorted(self._demo_data["roles"].keys()):
                if term in name.lower():
                    results.append({"label": "Role", "name": name})
            for name in sorted(self._demo_data["skills"].keys()):
                if term in name.lower():
                    results.append({"label": "Skill", "name": name})
            for name in sorted(self._demo_data["courses"].keys()):
                if term in name.lower():
                    results.append({"label": "Course", "name": name})
            return results

        if "MATCH (r:Role {name:$name}) RETURN r.name AS name" in normalized:
            name = params.get("name")
            if name in self._demo_data["roles"]:
                return [{"name": name, "description": self._demo_data["roles"][name]["description"]}]
            return []

        if "MATCH (s:Skill {name:$name}) RETURN s.name AS name" in normalized:
            name = params.get("name")
            if name in self._demo_data["skills"]:
                return [{"name": name, "description": self._demo_data["skills"][name]["description"]}]
            return []

        if "MATCH (c:Course {name:$name}) RETURN c.name AS name" in normalized:
            name = params.get("name")
            if name in self._demo_data["courses"]:
                return [{"name": name, "provider": self._demo_data["courses"][name]["provider"], "description": self._demo_data["courses"][name]["description"]}]
            return []

        if "MATCH (r:Role {name:$name})-[:REQUIRES]->(s:Skill)" in normalized:
            name = params.get("name")
            if name in self._demo_data["roles"]:
                return [{"name": skill} for skill in self._demo_data["roles"][name]["skills"]]
            return []

        if "MATCH (r:Role {name:$name})-[:REQUIRES]->(:Skill)<-[:TEACHES]-(c:Course)" in normalized:
            name = params.get("name")
            if name in self._demo_data["roles"]:
                return [{"name": course["name"]} for course in self._demo_data["roles"][name]["courses"]]
            return []

        if "MATCH (r:Role {name:$name})-[:REQUIRES]->(s:Skill)-[:REQUIRES]->(p:Skill)" in normalized:
            name = params.get("name")
            if name in self._demo_data["roles"]:
                return [{"name": item} for item in self._demo_data["roles"][name]["prerequisites"]]
            return []

        if "MATCH (r:Role {name:$name})-[:REQUIRES]->(s:Skill)<-[:REQUIRES]-(other:Role)" in normalized:
            name = params.get("name")
            if name in self._demo_data["roles"]:
                return [{"name": item} for item in self._demo_data["roles"][name]["related_roles"]]
            return []

        if "MATCH (s:Skill {name:$name})-[:REQUIRES]->(p:Skill)" in normalized:
            name = params.get("name")
            if name in self._demo_data["skills"]:
                return [{"name": item} for item in self._demo_data["skills"][name]["prerequisites"]]
            return []

        if "MATCH (c:Course)-[:TEACHES]->(s:Skill {name:$name})" in normalized:
            name = params.get("name")
            if name in self._demo_data["skills"]:
                return [{"name": item["name"], "provider": item["provider"]} for item in self._demo_data["skills"][name]["courses"]]
            return []

        if "MATCH (r:Role)-[:REQUIRES]->(s:Skill {name:$name})" in normalized:
            name = params.get("name")
            if name in self._demo_data["skills"]:
                return [{"name": item} for item in self._demo_data["skills"][name]["roles"]]
            return []

        if "MATCH (c:Course {name:$name})-[:TEACHES]->(s:Skill)" in normalized:
            name = params.get("name")
            if name in self._demo_data["courses"]:
                return [{"name": item} for item in self._demo_data["courses"][name]["skills"]]
            return []

        if "MATCH (c:Course {name:$name})-[:TEACHES]->(s:Skill)<-[:REQUIRES]-(r:Role)" in normalized:
            name = params.get("name")
            if name in self._demo_data["courses"]:
                return [{"name": item} for item in self._demo_data["courses"][name]["roles"]]
            return []

        return []

    def list_roles(self):
        rows = self._run(
            "MATCH (r:Role) RETURN r.name AS name ORDER BY r.name"
        )
        return [row["name"] for row in rows]

    def list_skills(self):
        rows = self._run(
            "MATCH (s:Skill) RETURN s.name AS name ORDER BY s.name"
        )
        return [row["name"] for row in rows]

    def search_nodes(self, term):
        return self._run(
            "MATCH (n) WHERE toLower(n.name) CONTAINS toLower($term) "
            "RETURN labels(n)[0] AS label, n.name AS name "
            "ORDER BY n.name LIMIT 30",
            {"term": term},
        )

    def get_role_details(self, name):
        role = self._run(
            "MATCH (r:Role {name:$name}) RETURN r.name AS name, r.description AS description",
            {"name": name},
        )
        if not role:
            return None

        skills = self._run(
            "MATCH (r:Role {name:$name})-[:REQUIRES]->(s:Skill) "
            "RETURN s.name AS name ORDER BY s.name",
            {"name": name},
        )
        courses = self._run(
            "MATCH (r:Role {name:$name})-[:REQUIRES]->(:Skill)<-[:TEACHES]-(c:Course) "
            "RETURN DISTINCT c.name AS name ORDER BY name",
            {"name": name},
        )
        prerequisites = self._run(
            "MATCH (r:Role {name:$name})-[:REQUIRES]->(s:Skill)-[:REQUIRES]->(p:Skill) "
            "RETURN DISTINCT p.name AS name ORDER BY name",
            {"name": name},
        )
        related_roles = self._run(
            "MATCH (r:Role {name:$name})-[:REQUIRES]->(s:Skill)<-[:REQUIRES]-(other:Role) "
            "WHERE other.name <> $name RETURN DISTINCT other.name AS name ORDER BY name",
            {"name": name},
        )
        return {
            "name": role[0]["name"],
            "description": role[0].get("description", ""),
            "skills": [row["name"] for row in skills],
            "courses": [row for row in courses],
            "prerequisites": [row["name"] for row in prerequisites],
            "related_roles": [row["name"] for row in related_roles],
        }

    def get_skill_details(self, name):
        skill = self._run(
            "MATCH (s:Skill {name:$name}) RETURN s.name AS name, s.description AS description",
            {"name": name},
        )
        if not skill:
            return None

        prerequisites = self._run(
            "MATCH (s:Skill {name:$name})-[:REQUIRES]->(p:Skill) "
            "RETURN p.name AS name ORDER BY name",
            {"name": name},
        )
        courses = self._run(
            "MATCH (c:Course)-[:TEACHES]->(s:Skill {name:$name}) "
            "RETURN c.name AS name, c.provider AS provider ORDER BY c.name",
            {"name": name},
        )
        roles = self._run(
            "MATCH (r:Role)-[:REQUIRES]->(s:Skill {name:$name}) "
            "RETURN r.name AS name ORDER BY r.name",
            {"name": name},
        )
        return {
            "name": skill[0]["name"],
            "description": skill[0].get("description", ""),
            "prerequisites": [row["name"] for row in prerequisites],
            "courses": [{"name": row["name"], "provider": row["provider"]} for row in courses],
            "roles": [row["name"] for row in roles],
        }

    def get_course_details(self, name):
        course = self._run(
            "MATCH (c:Course {name:$name}) RETURN c.name AS name, c.provider AS provider, c.description AS description",
            {"name": name},
        )
        if not course:
            return None

        skills = self._run(
            "MATCH (c:Course {name:$name})-[:TEACHES]->(s:Skill) "
            "RETURN s.name AS name ORDER BY s.name",
            {"name": name},
        )
        related_roles = self._run(
            "MATCH (c:Course {name:$name})-[:TEACHES]->(s:Skill)<-[:REQUIRES]-(r:Role) "
            "RETURN DISTINCT r.name AS name ORDER BY name",
            {"name": name},
        )
        return {
            "name": course[0]["name"],
            "provider": course[0].get("provider", ""),
            "description": course[0].get("description", ""),
            "skills": [row["name"] for row in skills],
            "roles": [row["name"] for row in related_roles],
        }
