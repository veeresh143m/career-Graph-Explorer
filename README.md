# Career Graph Explorer

A simple Python Flask application backed by CognoDB (Neo4j-compatible graph database) for exploring career roles, skills, and learning paths.

## Why a graph database?

This use case is about connected career knowledge: roles require skills, skills require prerequisite skills, and courses teach skills. A graph database makes it easy to model this as nodes and relationships, then answer multi-hop questions like:

- "Which courses teach skills required by a role?"
- "What prerequisite skills support this role through related skill dependencies?"
- "Which roles share a common skill?"

A relational database would require multiple joins across role-skill, skill-prerequisite, and course-skill tables. Graph traversal is more intuitive and expressive for this connected domain.

## Data model

- `:Role` nodes with `name`, `description`
- `:Skill` nodes with `name`, `description`
- `:Course` nodes with `name`, `provider`, `description`
- `(:Role)-[:REQUIRES]->(:Skill)`
- `(:Skill)-[:REQUIRES]->(:Skill)`
- `(:Course)-[:TEACHES]->(:Skill)`

### Search results

The app supports searching for roles, skills, and courses by name.

### Example graph diagram

```text
Role -[:REQUIRES]-> Skill -[:REQUIRES]-> Skill
  \                          /
   \-[:REQUIRES]-> Skill <-[:TEACHES]- Course
```

## Setup

1. Create a CognoDB Cloud account at https://console.cognodb.com/signup.
2. Provision a free instance and copy the generated password for user `cognodb`.
3. Clone this repository.
4. Create a `.env` file in the project root with:

```env
COGNODB_URI=bolt+s://<instance-id>.databases.cognodb.cloud
COGNODB_PASSWORD=<your-password>
COGNODB_USER=cognodb
```

5. Install dependencies:

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

6. Load seed data:

```bash
python seed.py
```

7. Run the app:

```bash
python app.py
```

8. Open `http://127.0.0.1:5000`.

## Main queries

- `list_roles()` / `list_skills()` - list all role or skill names.
- `get_role_details(name)` - loads role info, required skills, related learning paths, prerequisite skills, and related roles.
- `get_skill_details(name)` - loads skill info, prerequisites, courses that teach the skill, and roles that require it.
- `search_nodes(term)` - searches nodes by name.

## Multi-hop query example

The role detail page runs a multi-hop traversal to find courses for a role:

```cypher
MATCH (r:Role {name:$name})-[:REQUIRES]->(:Skill)<-[:TEACHES]-(c:Course)
RETURN DISTINCT c.name AS name ORDER BY name
```

This query travels from `Role` to `Skill` to `Course`.

## Screenshots

*Add screenshots here once the UI is visible.*
