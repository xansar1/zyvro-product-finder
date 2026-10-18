import pytest
from zyvro.catalog import demo_catalog, select_demo
from zyvro.analytics import COMPONENT_WEIGHTS, economics, rank_candidates, score_candidate, frame_for_table

def test_demo_deterministic():
    assert demo_catalog()==demo_catalog()
    assert len(demo_catalog())==70
    assert all(x['url'] is None and x['source']=='Fictional sample' for x in demo_catalog())

def test_filter_products():
    assert select_demo('laptop')
    assert all('laptop' in x['title'].lower() for x in select_demo('laptop'))
    assert select_demo('nonexistent niche')==[]
    assert all(x['category']=='Travel' for x in select_demo(category='Travel'))

def test_score_bounds():
    assert sum(COMPONENT_WEIGHTS.values())==100
    for item in demo_catalog():
        result=score_candidate(item)
        assert 0 <= result['opportunity_score'] <= 100
        assert sum(result['components'].values())-result['opportunity_score'] < .4

def test_missing_fields_reduce_evidence():
    incomplete=score_candidate({'title':'No data','rating':None,'price':None,'reviews':None,'currency':'INR'})
    assert incomplete['data_fields_present']==0
    assert incomplete['tier']=='Limited evidence'

def test_score_sorted():
    ranks=rank_candidates(demo_catalog())
    assert [x['opportunity_score'] for x in ranks]==sorted([x['opportunity_score'] for x in ranks],reverse=True)

def test_no_infinite_scores():
    assert score_candidate({'rating':float('nan'),'price':float('inf'),'reviews':-1})['opportunity_score']==0

def test_profit_scenario():
    result=economics(1000,400,50,10,80,20)
    assert result['fees']==100 and result['unit_profit']==350 and result['net_margin_percent']==35

def test_negative_profit_allowed():
    assert economics(100,200,40,10,20,10)['unit_profit']<0

@pytest.mark.parametrize('args', [(0,0,0,0,0,0), (100,-1,0,0,0,0),(100,0,0,101,0,0)])
def test_bad_economics(args):
    with pytest.raises(ValueError): economics(*args)

def test_dataframe_columns():
    assert list(frame_for_table([]).columns)==list(frame_for_table(rank_candidates(demo_catalog())).columns)
