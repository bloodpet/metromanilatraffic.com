
def generate_sections(road, direction):
    if direction == 'ns':
        dir1 = 's'
        dir2 = 'n'
    else:
        dir1 = 'w'
        dir2 = 'e'
    nodes = road.node_set.all().order_by('position')
    node_count = nodes.count()
    for count, node1, node2 in zip(range(node_count), nodes[:node_count], nodes[1:]):
        section1 = road.section_set.create(name='%s to %s' % (node1.name, node2.name), start=node1, end=node2, direction=dir1, position=count)
        section1.save()
        # Fix the position of the northbound/eastbound sections to allow viewing them from top to bottom
        section2 = road.section_set.create(name='%s to %s' % (node2.name, node1.name), start=node2, end=node1, direction=dir2, position=(node_count+1-count))
        section2.save()
    return ''
