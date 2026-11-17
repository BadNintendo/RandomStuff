class NanoscaleContainer:
    def __init__(self):
        self.containers = [[0]]  # Initial empty container

    def add_data(self, data):
        current_container = self.containers[-1]
        # Check if the last element is a filled container
        if isinstance(current_container[-1], int) and current_container[-1] == 0:
            current_container[-1] = data  # Replace 0 with data
        elif isinstance(current_container[-1], int):
            current_container[-1] = [current_container[-1], data]  # Subdivide the container
        else:
            self._subdivide(current_container)

    def _subdivide(self, container):
        if len(container) < 10:  # Assuming a container can hold 10 items
            container.append(0)
        else:
            new_container = [0]
            self.containers.append(new_container)

    def measure_container(self, index):
        if index < len(self.containers):
            container = self.containers[index]
            return self._measure(container)
        else:
            return []

    def _measure(self, container):
        coordinates = []
        for i, element in enumerate(container):
            if isinstance(element, list):
                sub_coordinates = self._measure(element)
                for sub_i, sub_element in sub_coordinates:
                    coordinates.append((i, sub_i, sub_element))
            else:
                coordinates.append((i, element))
        return coordinates

# Example usage
nanoscope = NanoscaleContainer()
nanoscope.add_data('matter1')
nanoscope.add_data('matter2')
nanoscope.add_data('matter3')
print(nanoscope.measure_container(0))