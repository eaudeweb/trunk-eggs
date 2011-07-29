import simplejson as json
import urllib
import logging
from App.config import getConfiguration
from Products.Five.browser import BrowserView
from zope.pagetemplate.pagetemplatefile import PageTemplateFile

log = logging.getLogger(__name__)

tiles_url = getConfiguration().environment.get('AOA_MAP_TILES', '')
aoa_url = getConfiguration().environment.get('AOA_PORTAL_URL', '')


map_template = PageTemplateFile('map.pt', globals())

class AoaMap(BrowserView):
    """
    The "AoA map search" page.
    """

    def _get_aoa_config(self):
        aoa_data = urllib.urlopen(aoa_url + 'jsmap_search_map_config')
        aoa_config = json.load(aoa_data)
        aoa_data.close()
        return aoa_config

    def _get_search_url(self):
        return self.context.absolute_url() + '/aoa-map-search'

    def get_map_html(self):
        try:
            aoa_config = self._get_aoa_config()
        except:
            log.exception("Could not load configuration for AoA search map")
            return "Error loading configuration for AoA search map"

        map_config = {
            'tiles_url': tiles_url,
            'search_url': self._get_search_url(),
            'country_fiche_prefix': aoa_url + '/viewer_aggregator/',
            'debug': True,
            'www_prefix': "++resource++eea.aoamap",
        }
        map_config.update(aoa_config)

        options = {
            'map_config': json.dumps(map_config),
            'filter_options': {
                'themes': [u"Water", u"Green economy"],
                'document_types': map_config['document_types'],
            },
        }

        return map_template(**options)


class AoaMapSearch(BrowserView):
    """
    Proxy search requests to the AoA portal.
    """

    def __call__(self):
        search_url = (aoa_url + 'jsmap_search_map_documents?' +
                      self.request.QUERY_STRING)
        json_response = urllib.urlopen(search_url).read()
        self.request.RESPONSE.setHeader('Content-Type', 'application/json')
        return json_response
