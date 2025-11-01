from collections import defaultdict
from sqlalchemy import select

from app.sim_engine.core.dummy_roadnet import *

from app import SessionLocal
from app.models import FuelStation, IdleArea, Shovel, Unload, TYPE_MODEL_MAP

db = SessionLocal()
__all__ = (
    'RoadNetCleaner',
    'BINDABLE_ENTITIES',
)


class RoadNetCleaner(BaseRoadNetCleaner):

    def __init__(self, quarry_id: int):
        self.quarry_id = quarry_id

    def clean(self, graph: RoadNetGraph, *args, **kwargs) -> None:
        self.__clean_graph_bonds_by_schema(graph)
        self.__clean_graph_bonds_by_data(graph)

    @staticmethod
    def __clean_graph_bonds_by_schema(graph: RoadNetGraph) -> None:
        """
        Internal helper for sanitizing point bonds schema.
        Broken and forbidden entries are silently dropped
        """

        met_bonds = set()

        for bonds in graph.vertices['bonds']:

            idx_to_delete = []
            for i, bond in enumerate(bonds):

                if bond.get('type') not in BINDABLE_ENTITIES:
                    idx_to_delete.append(i)
                    continue

                try:
                    int(bond.get('id'))
                except (ValueError, TypeError):
                    idx_to_delete.append(i)
                    continue

                id_type_tuple = (bond['id'], bond['type'])
                if id_type_tuple in met_bonds:
                    idx_to_delete.append(i)
                    continue

                met_bonds.add((bond['id'], bond['type']))

            for idx in reversed(idx_to_delete):
                del bonds[idx]


    def __clean_graph_bonds_by_data(self, graph: RoadNetGraph) -> None:
        """
        Internal helper for sanitizing point bonds data.
        Broken and forbidden entries are silently dropped
        """

        bond_type_ids_map = defaultdict(set)
        bond_vertex_map = defaultdict(set)

        for vertex_idx, bonds in enumerate(graph.vertices['bonds']):
            for bond in bonds:
                bond_type_ids_map[bond['type']].add(bond['id'])
                bond_vertex_map[(bond['id'], bond['type'])].add(vertex_idx)

        for bond_type, ids in bond_type_ids_map.items():
            model = TYPE_MODEL_MAP[bond_type]
            db_ids = set(db.execute(
                select(model.id).where(model.id.in_(ids), model.quarry_id == self.quarry_id)
            ).scalars())
            non_existent_ids = ids - db_ids
            for non_existent_id in non_existent_ids:
                for vertex_idx in bond_vertex_map[(non_existent_id, bond_type)]:
                    for bond_idx, bond in enumerate(graph.vertices[vertex_idx]['bonds']):
                        if bond['id'] == non_existent_id and bond['type'] == bond_type:
                            del graph.vertices[vertex_idx]['bonds'][bond_idx]
                            break


BINDABLE_ENTITIES: tuple[str, ...] = (
    Shovel.__tablename__,
    Unload.__tablename__,
    IdleArea.__tablename__,
    FuelStation.__tablename__,
)
"""Entity types that may be bound to road net junctions"""

