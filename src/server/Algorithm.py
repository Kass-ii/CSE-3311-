import heapq


def dijkstra(graph, start, end):

    pq = [(0, start)]       
    # starts at the first node with distance of zero

    distances = {start: 0}     # best known distance to each node
    #holds shortest distance
    previous = {}

    visited = set()

    while pq:
        current_distance, node = heapq.heappop(pq)

        if node in visited:
            continue
        
        visited.add(node)

        if node == end:
            break

        for neighbor, weight in graph.get(node, []):
            new_distance = current_distance + weight

            if neighbor not in distances or new_distance < distances[neighbor]:
                distances[neighbor] = new_distance
                previous[neighbor] = node
                heapq.heappush(pq, (new_distance, neighbor))

    if end not in distances:
        return "empty"

    path = []
    current = end
    while current != start:
        path.append(current)
        current = previous[current]
    path.append(start)
    path.reverse()

    return distances[end], path