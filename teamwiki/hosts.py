from django_hosts import patterns, host


host_patterns = patterns('',
    host(r'administration', 'teamwiki.admin_urls', name='admin'),
    host(r'dropme|pydrop', 'dropmefiles.urls', name='dropme'),
    host(None, 'thewiki.default_urls', name='default'),
    host(r'(?P<username>[a-z0-9_.-]+)\.wiki', 'thewiki.urls',
         callback='thewiki.models.wiki_load_for_host',
         name='wikis')
)

