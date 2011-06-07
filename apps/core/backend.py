
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

def get_statuses(twitter_name='MMDA', road=None):
    '''A very basic twitter client to get traffic updates from MMDA by default.
    '''
    import re
    import httplib2
    from BeautifulSoup import BeautifulSoup
    h = httplib2.Http()
    resp, content = h.request('http://twitter.com/%s' % twitter_name, 'GET')
    soup = BeautifulSoup(content)
    if road is None:
        entries = soup.findAll('span', *{'class': 'entry-content'})
    else:
        entries = soup.findAll('span', text=re.compile('.*EDSA.*'), *{'class': 'entry-content'})
    # Return the 10 most recent entries (the ten topmost entries)
    return entries[:10]
