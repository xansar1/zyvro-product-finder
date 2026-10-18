import pytest
import requests
from zyvro.providers import amazon_url, fetch_amazon, parse_search_results, ProviderError

def test_host_validation():
    assert amazon_url('https://www.amazon.in/dp/B123','amazon.in')
    assert amazon_url('https://evil.com/go?url=amazon.in','amazon.in') is None
    assert amazon_url('http://amazon.in/product','amazon.in') is None
    assert amazon_url('https://www.amazon.com/x','amazon.in') is None

def test_parse_partial_data_without_fabricating():
    rows=parse_search_results({'search_results':[{'title':'Example','rating':4.2,'reviews_total':34,'price':{'value':999},'link':'https://www.amazon.in/dp/foo'},
                                               {'title':'Missing fields', 'link':'https://evil.example/'}]},'amazon.in')
    assert len(rows)==2
    assert rows[0]['price']==999 and rows[0]['rating']==4.2
    assert rows[1]['price'] is None and rows[1]['rating'] is None and rows[1]['url'] is None
    assert rows[0]['source']=='Rainforest search results'

def test_bad_payload():
    with pytest.raises(ProviderError):parse_search_results({'status':'error'},'amazon.in')

class DummyResponse:
    def raise_for_status(self):pass
    def json(self):return {'search_results':[{'title':'Test item','price':{'value':500},'link':'https://www.amazon.in/dp/123'}]}
class Session:
    def __init__(self):self.params=None
    def get(self,url,params,timeout):self.params=params;self.timeout=timeout;return DummyResponse()

def test_fetch_passes_parameters():
    s=Session();rows=fetch_amazon('desk light','amazon.in','dummy-key',session=s)
    assert len(rows)==1 and s.params['search_term']=='desk light'
    assert s.params['api_key']=='dummy-key' and s.timeout==20

def test_missing_key():
    with pytest.raises(ProviderError):fetch_amazon('desk light','amazon.in','')

class FailingSession:
    def get(self,*args,**kwargs):raise requests.exceptions.RequestException('contains-secret-in-url')

def test_provider_does_not_echo_secret():
    with pytest.raises(ProviderError) as info:fetch_amazon('desk light','amazon.in','super-secret',session=FailingSession())
    assert 'secret' not in str(info.value)
