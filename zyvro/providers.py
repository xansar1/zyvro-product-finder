"""Optional Rainforest Amazon search connector; credentials must remain server-side."""
from __future__ import annotations
from urllib.parse import urlparse
import requests

API_ENDPOINT = 'https://api.rainforestapi.com/request'
MARKETS = {'amazon.in': 'INR','amazon.com': 'USD'}

class ProviderError(RuntimeError):
    pass

def amazon_url(value: str | None, marketplace: str) -> str | None:
    """Never link provider-controlled redirect/third-party URLs."""
    if not value or not isinstance(value,str) or marketplace not in MARKETS:
        return None
    try:
        parsed = urlparse(value)
        return value if parsed.scheme=='https' and parsed.hostname in {marketplace, 'www.'+marketplace} else None
    except ValueError:
        return None

def parse_search_results(payload: dict, marketplace: str) -> list[dict]:
    if marketplace not in MARKETS:raise ValueError('Unknown marketplace')
    if not isinstance(payload,dict) or not isinstance(payload.get('search_results'),list):
        raise ProviderError('Search provider did not return a usable product list.')
    parsed=[]
    for i,item in enumerate(payload['search_results']):
        if not isinstance(item,dict) or not str(item.get('title','')).strip():continue
        raw_price = item.get('price')
        raw_price = raw_price.get('value') if isinstance(raw_price,dict) else raw_price
        try:
            price=float(raw_price) if raw_price is not None else None
            if price is not None and not (0 < price < 1e9):price=None
        except (TypeError,ValueError,OverflowError):price=None
        def numeric(key,minimum,maximum):
            try:
                x=float(item.get(key))
                if minimum<=x<=maximum:return x
            except (ValueError,TypeError,OverflowError):pass
            return None
        reviews=numeric('reviews_total',0,1e9)
        link=amazon_url(item.get('link'), marketplace)
        parsed.append({'id':f'PROVIDER-{i+1:03}','title':str(item['title']).strip()[:240],
            'category':'Provider search results','price':price,'currency':MARKETS[marketplace],
            'rating':numeric('rating',0,5),'reviews':int(reviews) if reviews is not None else None,
            'url':link, 'source':'Rainforest search results','sponsored':bool(item.get('sponsored',False))})
    return parsed

def fetch_amazon(keyword:str, marketplace:str, api_key:str, max_results:int=40, timeout:int=20,
                 session=None)->list[dict]:
    keyword=keyword.strip()
    if marketplace not in MARKETS:raise ValueError('Unsupported marketplace')
    if not 2<=len(keyword)<=120:raise ValueError('Search must contain 2 to 120 characters')
    if not api_key:raise ProviderError('Rainforest API key is not configured on the server.')
    client=session or requests
    try:
        response=client.get(API_ENDPOINT, params={'api_key':api_key,'type':'search',
                 'amazon_domain':marketplace,'search_term':keyword,'page':1}, timeout=timeout)
        response.raise_for_status()
        payload=response.json()
        if not isinstance(payload,dict):raise ProviderError('Unexpected provider response.')
        info = payload.get('request_info')
        if isinstance(info, dict) and info.get('success') is False:
            raise ProviderError('The provider could not complete this search.')
    except ProviderError:raise
    except (requests.exceptions.RequestException,ValueError):
        # Never include original exception: requests may include URL/query with secret api_key.
        raise ProviderError('Provider request failed. Verify credentials, quota, and connectivity.') from None
    return parse_search_results(payload,marketplace)[:max_results]
