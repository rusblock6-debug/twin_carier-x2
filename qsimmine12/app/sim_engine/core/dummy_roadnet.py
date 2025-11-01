# === ЗАГЛУШКА: roadnet отключён ===
class Edge: pass
class Vertex: pass
class RoadNetGraph: pass
class BaseRoadNetCleaner: pass
class BaseSchemaValidator: pass
class RoadNetFactory:
    @staticmethod
    def create_graph(): return None
    @staticmethod
    def create_cleaner(): return None
class RoadNetException(Exception): pass
