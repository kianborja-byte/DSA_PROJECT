import heapq
import math

METERS_PER_PIXEL = 0.3  # scale of the CSPC campus map


class CampusGraph:
    def __init__(self):
        # Adjacency list: building -> {neighbor: distance in meters}
        self.map = {}
        self.pos = {}  # building -> (x, y) position on the map

    def add_building(self, name, x=0, y=0):
        # Add a vertex if it doesn't exist yet
        self.map.setdefault(name, {})
        self.pos.setdefault(name, (x, y))

    def add_pathway(self, a, b):
        # Add an undirected, weighted edge (walkable both ways).
        # The weight is the straight-line distance between the two buildings.
        (x1, y1), (x2, y2) = self.pos[a], self.pos[b]
        meters = round(math.hypot(x1 - x2, y1 - y2) * METERS_PER_PIXEL, 1)
        self.map[a][b] = meters
        self.map[b][a] = meters

    def close_pathway(self, a, b):
        # Remove an edge, e.g. when a path is blocked for an event
        self.map[a].pop(b, None)
        self.map[b].pop(a, None)

    def is_reachable(self, start, goal):
        # BFS: explore neighbors level by level
        visited = {start}
        queue = [start]
        while queue:
            current = queue.pop(0)
            if current == goal:
                return True
            for neighbor in self.map[current]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)
        return False

    def shortest_path(self, start, goal):
        # Dijkstra: always expand the closest unvisited building first
        dist = {b: float("inf") for b in self.map}
        prev = {}
        dist[start] = 0
        pq = [(0, start)]
        while pq:
            d, current = heapq.heappop(pq)
            if d > dist[current]:
                continue  # skip outdated queue entries
            for neighbor, w in self.map[current].items():
                new_d = d + w
                if new_d < dist[neighbor]:
                    dist[neighbor] = new_d
                    prev[neighbor] = current
                    heapq.heappush(pq, (new_d, neighbor))
        if dist[goal] == float("inf"):
            return None, None  # no route exists
        path = [goal]
        while path[-1] != start:
            path.append(prev[path[-1]])
        return path[::-1], round(dist[goal], 1)

    def display(self):
        # Print every building and its connections
        for building, links in self.map.items():
            print(building, "->", links)


# ---------- Build the CSPC campus ----------
campus = CampusGraph()

buildings = {
    "Entry Gate": (150, 920), "Security Gate": (300, 860),
    "Admin Building": (395, 705), "Food & Laboratory Building": (505, 615),
    "Library Building": (640, 560), "CSPC Auditorium": (795, 525),
    "ACAD Bldg I": (620, 830), "ACAD Bldg II": (1000, 495),
    "Green Building": (1130, 590), "ACAD Bldg III": (1375, 595),
    "ACAD Bldg IV": (1370, 672), "ACAD Bldg V": (1370, 515),
    "Duran Hall": (585, 715), "Freedom Park": (525, 745),
    "CSPC Gymnasium": (715, 715), "Villafuerte Hall": (885, 645),
    "CSPC Radio Tower Field": (1000, 625),
    "Restroom 1": (800, 800), "Restroom 2": (960, 765),
}
for name, (x, y) in buildings.items():
    campus.add_building(name, x, y)

pathways = [
    ("Entry Gate", "Security Gate"), ("Security Gate", "Admin Building"),
    ("Security Gate", "Duran Hall"), ("Security Gate", "Freedom Park"),
    ("Security Gate", "ACAD Bldg I"), ("Freedom Park", "Duran Hall"),
    ("Admin Building", "Food & Laboratory Building"),
    ("Food & Laboratory Building", "Library Building"),
    ("Library Building", "CSPC Auditorium"), ("CSPC Auditorium", "ACAD Bldg II"),
    ("ACAD Bldg II", "Green Building"), ("Green Building", "ACAD Bldg V"),
    ("Green Building", "ACAD Bldg III"),
    ("ACAD Bldg I", "Restroom 1"), ("Restroom 1", "Restroom 2"),
    ("Restroom 2", "Green Building"), ("Restroom 2", "ACAD Bldg IV"),
    ("ACAD Bldg I", "Duran Hall"), ("ACAD Bldg I", "CSPC Gymnasium"),
    ("CSPC Gymnasium", "CSPC Auditorium"), ("CSPC Gymnasium", "Restroom 1"),
    ("CSPC Gymnasium", "Villafuerte Hall"), ("Villafuerte Hall", "Restroom 1"),
    ("Villafuerte Hall", "Restroom 2"), ("Villafuerte Hall", "CSPC Auditorium"),
    ("CSPC Radio Tower Field", "Restroom 2"),
    ("CSPC Radio Tower Field", "Green Building"),
    ("CSPC Radio Tower Field", "ACAD Bldg II"),
    ("Duran Hall", "Food & Laboratory Building"),
    ("Library Building", "CSPC Gymnasium"),
    ("Villafuerte Hall", "CSPC Radio Tower Field"),
    ("Villafuerte Hall", "ACAD Bldg II"),
    ("Green Building", "ACAD Bldg IV"),
    ("Admin Building", "Freedom Park"),
    ("ACAD Bldg I", "Freedom Park"),
    ("ACAD Bldg II", "ACAD Bldg V"),
]
for a, b in pathways:
    campus.add_pathway(a, b)

campus.add_building("New Dorm", 200, 700)  # a building with no pathway yet

# ---------- Demo ----------
campus.display()

print("Entry Gate -> New Dorm reachable?",
      campus.is_reachable("Entry Gate", "New Dorm"))
print("Entry Gate -> ACAD Bldg IV reachable?",
      campus.is_reachable("Entry Gate", "ACAD Bldg IV"))

path, meters = campus.shortest_path("Entry Gate", "ACAD Bldg IV")
print("Shortest route:", " -> ".join(path), f"({meters} m)")

# Before the closure, the rest of the trip from ACAD Bldg I
path, meters = campus.shortest_path("ACAD Bldg I", "ACAD Bldg IV")
print("Old route from ACAD Bldg I:", " -> ".join(path), f"({meters} m)")

campus.close_pathway("ACAD Bldg I", "Restroom 1")  # blocked for an event!
path, meters = campus.shortest_path("ACAD Bldg I", "ACAD Bldg IV")
print("New route:     ", " -> ".join(path), f"({meters} m)")
