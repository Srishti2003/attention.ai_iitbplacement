from neo4j import GraphDatabase

class Neo4jMemory:
    def __init__(self, uri: str, username: str, password: str):
        self.driver = GraphDatabase.driver(uri, auth=(username, password))
    
    def retrieve_preferences(self, user_id: str):
        with self.driver.session() as session:
            result = session.run(
                "MATCH (u:User {user_id: $user_id}) RETURN u.interests AS interests, u.budget AS budget",
                user_id=user_id
            )
            record = result.single()
            if record:
                return {"interests": record["interests"], "budget": record["budget"]}
            return None
