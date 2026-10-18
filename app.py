"""ZYVRO AI V2 — responsible e-commerce product research studio.

All public default records are fictional. Optional Rainforest mode requires a private API key.
The 0–100 opportunity heuristic is not a trained ML model and never predicts sales.
"""
from __future__ import annotations
import os

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from zyvro.catalog import CATALOG, select_demo
from zyvro.analytics import COMPONENT_WEIGHTS, economics, frame_for_table, rank_candidates
from zyvro.providers import ProviderError, fetch_amazon, MARKETS

st.set_page_config(page_title='ZYVRO AI | Research Studio', page_icon='🔎', layout='wide', initial_sidebar_state='expanded')
st.markdown('''<style>
:root{--mint:#8bf8d7;--muted:#94a8c5;--stroke:#293f5a}
[data-testid="stAppViewContainer"]{background:radial-gradient(circle at 83% 1%,#251f48 0,transparent 34%),radial-gradient(circle at 5% 88%,#0a2930 0,transparent 26%),#080e1b;color:#edf5ff}
[data-testid="stHeader"]{background:#080e1bdc}
[data-testid="stSidebar"]{background:linear-gradient(150deg,#0f1929,#0b1222 82%);border-right:1px solid var(--stroke)}
[data-testid="stSidebar"] label,[data-testid="stSidebar"] small,[data-testid="stSidebar"] p{color:#c1cde0!important}
[data-testid="stMainBlockContainer"]{max-width:1420px;padding-top:2rem;padding-bottom:6rem}
[data-testid="stMetric"]{padding:15px 20px!important;background:#121d30;border:1px solid #2b415d;border-radius:12px}
[data-testid="stMetricValue"]{color:#eff8ff}
[data-testid="stPlotlyChart"],[data-testid="stDataFrame"]{border:1px solid #2c3d57;border-radius:13px;overflow:hidden}
h1,h2,h3{letter-spacing:-.05em!important}
.z-brand{display:flex;align-items:center;gap:12px;padding:8px 0 23px}.z-logo{height:43px;width:43px;border-radius:13px;background:linear-gradient(135deg,#8ff9d7,#92b7ff);color:#0a2531;display:grid;place-items:center;font-size:26px;font-weight:900}.z-brand b{display:block;font-size:21px;line-height:1.1;color:white}.z-brand small{letter-spacing:.18em;font-size:8px;color:#92b4c6}
.z-hero{padding:40px 45px;background:radial-gradient(circle at 88% 52%,#4a3c9d55 0,transparent 35%),linear-gradient(128deg,#122c38,#13172d);border:1px solid #35506d;border-radius:19px;margin:9px 0 24px}
.z-hero small{letter-spacing:.18em;color:#9bfddc;font-size:10px;font-weight:800}.z-hero h1{font-size:clamp(44px,5vw,77px);line-height:1.04;margin:17px 0}.z-hero h1 span{color:#8cfad9}.z-hero p{max-width:700px;font-size:15px;color:#aabfd5;line-height:1.75;margin-bottom:0}
.z-note{padding:14px 19px;border:1px solid #7d6855;background:#261f29;color:#f0cc9e;font-size:12px;border-radius:9px;margin:10px 0 25px}
.z-kicker{color:#90f8dc;letter-spacing:.18em;font-size:11px;font-weight:800;margin:21px 0 12px}
.z-footer{color:#8ba0b9;font-size:11px;letter-spacing:.07em;margin:45px 0 15px}
[data-baseweb="tab-list"]{gap:20px}
[data-baseweb="tab"]{font-weight:700}
@media(max-width:680px){.z-hero{padding:26px 21px}.z-hero h1{font-size:43px}}
</style>''',unsafe_allow_html=True)


def private_api_key() -> str:
    key=os.getenv('RAINFOREST_API_KEY','')
    if key:
        return key.strip()
    try:
        return str(st.secrets.get('RAINFOREST_API_KEY','')).strip()
    except (FileNotFoundError,KeyError,AttributeError):
        return ''


st.sidebar.markdown('''<div class="z-brand"><div class="z-logo">✧</div><div><b>zyvro<span style="color:#86f8dc">.ai</span></b><small>PRODUCT RESEARCH STUDIO</small></div></div>''',unsafe_allow_html=True)
st.sidebar.caption('WORKSPACE / RESEARCH MODE')
mode = st.sidebar.radio('Data source', ['Fictional demo catalog','Rainforest provider search'],label_visibility='visible')
if mode == 'Fictional demo catalog':
    st.sidebar.success('Fictional demo records · 70 items')
    keyword = st.sidebar.text_input('Search fictional catalog',placeholder='e.g. laptop, pet, travel')
    category = st.sidebar.selectbox('Product category', ['All']+list(CATALOG))
    records = select_demo(keyword,category)
    provider_label = 'Fictional sample'
    currency='INR'
else:
    st.sidebar.info('Search provider results. API usage may incur charges.')
    keyword = st.sidebar.text_input('Amazon search keyword',value='desk lamp',max_chars=120)
    marketplace = st.sidebar.selectbox('Marketplace',list(MARKETS))
    currency = MARKETS[marketplace]
    st.sidebar.caption('A private Rainforest API key must be configured on the server, not entered here.')
    if st.sidebar.button('Fetch provider search results',type='primary',use_container_width=True):
        try:
            with st.spinner('Fetching product search results…'):
                found=fetch_amazon(keyword,marketplace,private_api_key())
            st.session_state.zyvro_last_results=found
            st.session_state.zyvro_last_query=(keyword,marketplace)
            st.sidebar.success(f'Found {len(found)} result entries')
        except (ProviderError,ValueError) as exc:
            st.sidebar.error(str(exc))
    records=st.session_state.get('zyvro_last_results',[])
    saved_query=st.session_state.get('zyvro_last_query')
    if saved_query!=(keyword,marketplace):
        records=[]
    provider_label='Rainforest search results'

st.sidebar.markdown('---')
st.sidebar.caption('REFINE CANDIDATES')
min_score=st.sidebar.slider('Minimum heuristic score',0,100,0,5)
min_rating=st.sidebar.slider('Minimum displayed rating',0.0,5.0,0.0,0.5)
include_unrated=st.sidebar.checkbox('Include missing ratings',value=True)
sort_by=st.sidebar.selectbox('Sort by',['Opportunity score (heuristic)','Most reviews','Highest rating','Lowest price'])

scored = rank_candidates(records)
filtered=[r for r in scored if r['opportunity_score']>=min_score and (
    (r['rating'] is None and include_unrated) or (r['rating'] is not None and r['rating']>=min_rating)
)]
key_map={'Opportunity score (heuristic)':'opportunity_score','Most reviews':'reviews','Highest rating':'rating','Lowest price':'price'}
if sort_by!='Opportunity score (heuristic)':
    name=key_map[sort_by]
    filtered.sort(key=lambda r: (r.get(name) is not None, -(r.get(name) or 0) if sort_by=='Lowest price' else (r.get(name) or 0)),reverse=True)

st.markdown('''<div class="z-hero"><small>RESEARCH INTELLIGENCE / 2026</small><h1>Find signals.<br><span>Question assumptions.</span></h1><p>Explore product research data, compare listing signals and stress-test unit economics. Transparent ranking heuristics. No invented sales predictions.</p></div>''',unsafe_allow_html=True)
if mode=='Fictional demo catalog':
    st.markdown('<div class="z-note"><b>FICTIONAL DATA:</b> All 70 product examples, prices, ratings and review counts are simulated. No actual Amazon inventory, price, trend, or demand data is shown.</div>',unsafe_allow_html=True)
else:
    st.markdown('<div class="z-note"><b>PROVIDER SEARCH:</b> Results come from a third-party search API at request time. These are unverified listing attributes, not confirmed sales, inventory, competition or future demand.</div>',unsafe_allow_html=True)

if not scored:
    st.warning('No records yet. In demo mode try “Travel”, “laptop”, “Kitchen & Home”, or clear the filters. In provider mode configure a private API key and fetch a search.')
    st.stop()

st.markdown('<div class="z-kicker">01 / MARKET RESEARCH SNAPSHOT</div>', unsafe_allow_html=True)
with_rating=[x['rating'] for x in filtered if x.get('rating') is not None]
with_prices=[x['price'] for x in filtered if x.get('price') is not None]
a,b,c,d=st.columns(4)
a.metric('Candidates',f'{len(filtered)}')
b.metric('Median rating',f'{np.median(with_rating):.1f} / 5' if with_rating else 'Unknown')
c.metric('Median price',f'{"₹" if currency=="INR" else "$"}{np.median(with_prices):,.0f}' if with_prices else 'Unknown')
d.metric('Best heuristic score',f'{max([x["opportunity_score"] for x in filtered]):.1f} / 100' if filtered else '—')

p_discover,p_compare,p_profit,p_method=st.tabs(['Discovery','Compare','Unit Economics','Methodology'])

with p_discover:
    st.subheader('Candidate explorer')
    st.caption('A score ranks relative fit under published heuristics; it is not a prediction of actual product success.')
    df=frame_for_table(filtered)
    if not df.empty:
        display=df.rename(columns={'title':'Product','category':'Category','price':'Price','currency':'Currency','rating':'Rating','reviews':'Reviews','opportunity_score':'Heuristic / 100','tier':'Research tier','review_density_proxy':'Review density proxy','source':'Source','url':'Verified Amazon URL'})
        st.dataframe(display,hide_index=True,use_container_width=True,height=370,
                     column_config={'Verified Amazon URL':st.column_config.LinkColumn('Verified Amazon URL')})
        csv=df.to_csv(index=False).encode('utf-8')
        st.download_button('Export research CSV',data=csv,file_name='zyvro_research_v2.csv',mime='text/csv')
        left,right=st.columns([1.2,1])
        with left:
            fig=px.bar(df.head(12),x='opportunity_score',y='title',orientation='h',
                       hover_data=['source','rating','reviews'],labels={'title':'','opportunity_score':'Heuristic score'},
                       title='Top candidates by transparent heuristic')
            fig.update_layout(template='plotly_dark',paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',
                              height=450,margin=dict(l=0,r=8,t=50,b=10),yaxis={'categoryorder':'total ascending'},showlegend=False)
            st.plotly_chart(fig,use_container_width=True)
        with right:
            choice=st.selectbox('Inspect a candidate',options=range(len(filtered)),format_func=lambda i:filtered[i]['title'])
            item=filtered[choice]
            st.markdown('#### Explainable score')
            st.metric('Opportunity heuristic',f'{item["opportunity_score"]:.1f} / 100')
            st.caption('Every bar adds to the score. Scoring is manually defined, not an ML forecast.')
            factors=pd.DataFrame([{'Factor':k.replace('_',' ').title(),'Points':v,'Maximum':COMPONENT_WEIGHTS[k]} for k,v in item['components'].items()])
            fig=px.bar(factors,x='Points',y='Factor',orientation='h',range_x=[0,25],
                       title='Scoring components (points)')
            fig.update_layout(template='plotly_dark',paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',
                              height=330,margin=dict(l=0,r=8,t=50,b=10))
            st.plotly_chart(fig,use_container_width=True)
            st.caption(f'Evidence fields present: {item["data_fields_present"]}/3 • Source: {item["source"]}')
            if item.get('url'):st.link_button('Open verified product link',item['url'])
            else:st.info('No validated Amazon product URL for this record.')
    else:
        st.info('No candidates meet the current filters. Lower the minimum score or rating.')

with p_compare:
    st.subheader('Compare candidates side-by-side')
    st.caption('Select up to three products to compare observable fields and heuristic components.')
    names={x['id']:x for x in filtered}
    keys=st.multiselect('Choose candidates',list(names),default=list(names)[:min(3,len(names))],
                        max_selections=3,format_func=lambda key:names[key]['title'])
    if keys:
        compare=[]
        for k in keys:
            item=names[k]
            compare.append({'Product':item['title'],'Score':item['opportunity_score'],
              'Price':item['price'],'Rating':item['rating'],'Reviews':item['reviews'],
              'Review density proxy':item['review_density_proxy'],'Source':item['source']})
        st.dataframe(pd.DataFrame(compare),hide_index=True,use_container_width=True)
        factors=[]
        for k in keys:
            item=names[k]
            for factor,points in item['components'].items():
                factors.append({'Product':item['title'],'Factor':factor.replace('_',' ').title(),'Points':points})
        fig=px.bar(pd.DataFrame(factors),x='Factor',y='Points',color='Product',barmode='group',title='Score breakdown by item')
        fig.update_layout(template='plotly_dark',paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',height=430)
        st.plotly_chart(fig,use_container_width=True)
    else:st.info('Choose candidates in the selector to compare.')

with p_profit:
    st.subheader('Unit economics scenario lab')
    st.caption('Enter hypothetical selling price and costs; this is a calculator, not predicted ROI, demand or sales.')
    item_index=st.selectbox('Reference candidate',range(len(filtered)),format_func=lambda i:filtered[i]['title']) if filtered else None
    starting=float(filtered[item_index]['price']) if item_index is not None and filtered[item_index]['price'] else 1299.0
    st.info('Default costs are illustrative assumptions; replace them with verified sourcing, tax and platform-fee figures.')
    with st.form('profit_assumptions'):
        col1,col2,col3=st.columns(3)
        with col1:
            sell=st.number_input(f'Selling price ({currency})',min_value=1.0,value=max(starting,1.0),step=50.0)
            source=st.number_input(f'Sourcing cost ({currency})',min_value=0.0,value=round(starting*.42,2),step=10.0)
        with col2:
            ship=st.number_input(f'Shipping ({currency})',min_value=0.0,value=65.0,step=5.0)
            fee=st.number_input('Platform fees (%)',min_value=0.0,max_value=100.0,value=12.0,step=1.0)
        with col3:
            ad=st.number_input(f'Ads per unit ({currency})',min_value=0.0,value=100.0,step=10.0)
            returns=st.number_input(f'Return allowance per unit ({currency})',min_value=0.0,value=45.0,step=5.0)
        misc=st.number_input(f'Other costs and taxes per unit ({currency})',min_value=0.0,value=0.0,step=5.0)
        submit=st.form_submit_button('Calculate assumption-based margin',type='primary')
    if submit:
        result=economics(sell,source,ship,fee,ad,returns,misc)
        colA,colB,colC=st.columns(3)
        symbol='₹' if currency=='INR' else '$'
        colA.metric('Unit profit / loss',f'{symbol}{result["unit_profit"]:,.2f}')
        colB.metric('Net margin',f'{result["net_margin_percent"]:.1f}%')
        colC.metric('Costs per unit',f'{symbol}{result["total_cost"]:,.2f}')
        if result['unit_profit']<0:st.warning('Under your inputs the item loses money per unit.')
        else:st.success('Under these assumptions the model shows a positive unit margin. Real outcomes may differ.')

with p_method:
    st.subheader('How this research prototype works')
    st.markdown('''
**Data sources:** The default catalog contains **70 fictional products** and invented example prices/ratings/reviews. Optional Rainforest search returns real third-party records at request time, which may be missing or outdated.

**What the score measures:** A **handcrafted 0–100 opportunity heuristic**, built from rating (25 points), review signal (20), inverse review-density proxy (25), fixed price-band preference (15), and completeness (15). High reviews count both as evidence and as more crowded listings; this trade-off is a simple research rule, not real competition analysis.

**What the score does NOT do:** It is not a trained AI model, actual demand estimation, validated conversion-rate forecast, guaranteed profitability, or a buy recommendation. A product with a high score can still fail in the marketplace.

**Money calculations:** These use inputs you supply for purchase, shipping, platform, marketing, returns, and miscellaneous costs. No unseen real fees or tax rates are invented.

**Security:** Provider keys stay server-side. Only use a new key after rotating any key previously committed to GitHub. Never upload customer, banking, or other private commerce records in this public research demo.
''')
    st.markdown('#### Scoring weights')
    st.dataframe(pd.DataFrame([{'Factor':k.replace('_',' ').title(),'Max points':v} for k,v in COMPONENT_WEIGHTS.items()]),hide_index=True,use_container_width=True)
    st.caption('Portfolio demonstration · Built by Muhammed Ansar · 2026')

st.markdown('<div class="z-footer">ZYVRO AI / V2 RESEARCH STUDIO · DEMONSTRATION ONLY · NO FINANCIAL OR MARKET PERFORMANCE GUARANTEES</div>',unsafe_allow_html=True)
