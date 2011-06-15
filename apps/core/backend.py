import re
import datetime

PATTERN_ALL = re.compile('')

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

def get_statuses(twitter_name='MMDA', road_names=[], limit=5):
    '''A very basic twitter client to get traffic updates from MMDA by default.
    '''
    import httplib2
    from BeautifulSoup import BeautifulSoup
    now = datetime.datetime.now()
    since = now - datetime.timedelta(0, 120)
    now = datetime.datetime.now()
    h = httplib2.Http()
    tmp_url = 'http://search.twitter.com/search?&ors=%(roads)s&lang=all&from=%(user)s&rpp=%(limit)i&%(since)s'
    url = tmp_url % dict(
        user = twitter_name,
        roads = '+'.join(road_names),
        limit = limit,
        since = '%s-%s-%s' % (since.year, since.month, since.day),
    )
    try:
        resp, content = h.request(url, 'GET')
    except AttributeError, e:
        return []
    except httplib2.ServerNotFoundError, e:
        return []
    soup = BeautifulSoup(content)
    all_entries = soup.findAll('span', **{'class': re.compile('msgtxt.*')})
    entries = []
    for entry in all_entries:
        entries.append(''.join(entry.fetchText(PATTERN_ALL)))
    return entries
