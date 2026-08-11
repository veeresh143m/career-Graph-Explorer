from db import CognoDBClient, QueryError

SKILLS = [
    {"name": "Python", "description": "General-purpose programming for analysis and automation."},
    {"name": "SQL", "description": "Database querying for analytics and data access."},
    {"name": "Data Visualization", "description": "Translating data into charts and dashboards."},
    {"name": "Statistics", "description": "Core probability and statistical reasoning for data work."},
    {"name": "Machine Learning", "description": "Building predictive models from structured data."},
    {"name": "Cloud Infrastructure", "description": "Managing compute and storage resources in the cloud."},
    {"name": "Communication", "description": "Clear storytelling and collaboration with stakeholders."},
    {"name": "Product Strategy", "description": "Aligning customer needs, market context, and feature plans."},
]

ROLES = [
    {"name": "Data Analyst", "description": "Explores data to answer business questions and build reports."},
    {"name": "Machine Learning Engineer", "description": "Builds production-ready predictive models and data pipelines."},
    {"name": "Cloud Engineer", "description": "Designs and maintains cloud-hosted infrastructure and services."},
    {"name": "Product Manager", "description": "Guides product direction with customer insights and clear priorities."},
]

COURSES = [
    {"name": "Intro to SQL", "provider": "OpenAcademy", "description": "Learn queries, joins, and analytics workflows."},
    {"name": "Python for Data Analysis", "provider": "OpenAcademy", "description": "Use Python libraries to analyze and clean data."},
    {"name": "Visual Storytelling with Dashboards", "provider": "SkillPath", "description": "Create dashboards that make insights easy to share."},
    {"name": "Statistics Fundamentals", "provider": "SkillPath", "description": "Understand distributions, tests, and business decisions."},
    {"name": "Applied Machine Learning", "provider": "CloudLearn", "description": "Train and evaluate machine learning models on real data."},
    {"name": "Cloud Foundations", "provider": "CloudLearn", "description": "Learn the basics of cloud infrastructure and services."},
    {"name": "Communicating Data Insights", "provider": "CareerLab", "description": "Build stakeholder-ready presentations from analysis."},
    {"name": "Product Strategy Essentials", "provider": "CareerLab", "description": "Learn how to plan product goals and prioritize work."},
]

COURSE_TEACHES = [
    {"course": "Intro to SQL", "skill": "SQL"},
    {"course": "Python for Data Analysis", "skill": "Python"},
    {"course": "Visual Storytelling with Dashboards", "skill": "Data Visualization"},
    {"course": "Statistics Fundamentals", "skill": "Statistics"},
    {"course": "Applied Machine Learning", "skill": "Machine Learning"},
    {"course": "Cloud Foundations", "skill": "Cloud Infrastructure"},
    {"course": "Communicating Data Insights", "skill": "Communication"},
    {"course": "Product Strategy Essentials", "skill": "Product Strategy"},
    {"course": "Python for Data Analysis", "skill": "Data Visualization"},
]

ROLE_REQUIRES = [
    {"role": "Data Analyst", "skill": "SQL"},
    {"role": "Data Analyst", "skill": "Python"},
    {"role": "Data Analyst", "skill": "Data Visualization"},
    {"role": "Data Analyst", "skill": "Statistics"},
    {"role": "Machine Learning Engineer", "skill": "Python"},
    {"role": "Machine Learning Engineer", "skill": "Machine Learning"},
    {"role": "Machine Learning Engineer", "skill": "Statistics"},
    {"role": "Machine Learning Engineer", "skill": "Cloud Infrastructure"},
    {"role": "Cloud Engineer", "skill": "Cloud Infrastructure"},
    {"role": "Cloud Engineer", "skill": "Python"},
    {"role": "Product Manager", "skill": "Communication"},
    {"role": "Product Manager", "skill": "Product Strategy"},
    {"role": "Product Manager", "skill": "Data Visualization"},
]

SKILL_PREREQUISITES = [
    {"skill": "Data Visualization", "requires": "SQL"},
    {"skill": "Data Visualization", "requires": "Python"},
    {"skill": "Machine Learning", "requires": "Statistics"},
    {"skill": "Machine Learning", "requires": "Python"},
    {"skill": "Cloud Infrastructure", "requires": "Python"},
]


def seed_graph():
    client = CognoDBClient()
    try:
        with client.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")

            session.run(
                "UNWIND $nodes AS row CREATE (:Skill {name: row.name, description: row.description})",
                {"nodes": SKILLS},
            )
            session.run(
                "UNWIND $nodes AS row CREATE (:Role {name: row.name, description: row.description})",
                {"nodes": ROLES},
            )
            session.run(
                "UNWIND $nodes AS row CREATE (:Course {name: row.name, provider: row.provider, description: row.description})",
                {"nodes": COURSES},
            )
            session.run(
                "UNWIND $pairs AS row "
                "MATCH (c:Course {name: row.course}), (s:Skill {name: row.skill}) "
                "CREATE (c)-[:TEACHES]->(s)",
                {"pairs": COURSE_TEACHES},
            )
            session.run(
                "UNWIND $pairs AS row "
                "MATCH (r:Role {name: row.role}), (s:Skill {name: row.skill}) "
                "CREATE (r)-[:REQUIRES]->(s)",
                {"pairs": ROLE_REQUIRES},
            )
            session.run(
                "UNWIND $pairs AS row "
                "MATCH (s:Skill {name: row.skill}), (p:Skill {name: row.requires}) "
                "CREATE (s)-[:REQUIRES]->(p)",
                {"pairs": SKILL_PREREQUISITES},
            )
        print("Seed data loaded successfully.")
    except QueryError as exc:
        print(f"Unable to seed database: {exc}")
    finally:
        client.close()


if __name__ == "__main__":
    seed_graph()
