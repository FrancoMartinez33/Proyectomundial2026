from src import data_store

print(f"✓ Países cargados: {len(data_store.paises_mundial)}")
print(f"✓ Primeros 5 países: {data_store.paises_mundial[:5]}")
print(f"✓ Jugadores cargados: {sum(len(v) for v in data_store.jugadores_por_equipo.values())}")
print(f"✓ Jugadores de México: {len(data_store.jugadores_por_equipo.get('México', []))}")
print(f"✓ Confederaciones: {len(data_store.confederaciones)} únicas")
print(f"✓ Prefijos telefónicos: {len(data_store.prefijos_telefonicos)} únicos")
