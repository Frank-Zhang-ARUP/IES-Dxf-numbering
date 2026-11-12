import gc, io, os, re
from collections import Counter, defaultdict
import streamlit as st
import ezdxf

st.set_page_config(page_title='DXF Room Numbering', layout='wide')
st.title('DXF Room Function Numbering Tool')
st.caption('Memory-conscious Streamlit version. Selected TEXT/MTEXT only; output is a new DXF.')
MAX_MB = 40
uploaded = st.file_uploader(f'DXF file (max {MAX_MB} MB recommended)', type=['dxf'])

def clean_text(s):
    s = '' if s is None else str(s)
    s = re.sub(r'\\P', ' ', s)
    s = re.sub(r'\\[A-Za-z][^;]*;', '', s)
    return re.sub(r'\s+', ' ', s.replace('{','').replace('}','')).strip()

def read_doc(b):
    # DXF is normally ASCII; latin-1 is lossless byte-to-text fallback.
    for enc in ('utf-8-sig','gb18030','latin-1'):
        try:
            return ezdxf.read(io.StringIO(b.decode(enc)))
        except (UnicodeDecodeError, ezdxf.DXFStructureError):
            continue
    raise ValueError('Unsupported or damaged DXF.')

def scan(doc):
    rows=[]
    for layout in doc.layouts:
        for e in layout:
            typ=e.dxftype()
            if typ not in ('TEXT','MTEXT'): continue
            raw=e.dxf.text if typ=='TEXT' else e.text
            label=clean_text(raw)
            if not label: continue
            p=e.dxf.insert
            rows.append((e,label,float(p.x),float(p.y),layout.name,e.dxf.layer))
    return rows

if uploaded is not None:
    size_mb=uploaded.size/(1024*1024)
    if size_mb > MAX_MB:
        st.error(f'File is {size_mb:.1f} MB. Please keep DXF below {MAX_MB} MB for Streamlit Community Cloud memory safety.')
        st.stop()
    data=uploaded.getvalue()
    try:
        doc=read_doc(data)
        del data; gc.collect()
        rows=scan(doc)
    except Exception as ex:
        st.error(f'Cannot read DXF: {ex}')
        st.stop()
    counts=Counter(r[1] for r in rows)
    st.write(f'Found **{len(rows)}** TEXT/MTEXT objects.')
    selected=st.multiselect('Room functions to number', sorted(counts, key=str.casefold), format_func=lambda x:f'{x} ({counts[x]})')
    c1,c2,c3=st.columns(3)
    order=c1.selectbox('Order',['Top to bottom, then left to right','Left to right, then top to bottom'])
    digits=c2.number_input('Digits',1,6,2)
    start=c3.number_input('Start',0,999999,1)
    sep=st.text_input('Separator',' ')
    if st.button('START NUMBERING', type='primary', disabled=not selected):
        groups=defaultdict(list); sel=set(selected)
        for r in rows:
            if r[1] in sel: groups[r[1]].append(r)
        changed=[]
        for label, items in groups.items():
            items.sort(key=(lambda r:(-r[3],r[2])) if order.startswith('Top') else (lambda r:(r[2],-r[3])))
            for n,r in enumerate(items,int(start)):
                e=r[0]; new=f'{label}{sep}{n:0{int(digits)}d}'
                if e.dxftype()=='TEXT': e.dxf.text=new
                else: e.text=new
                changed.append((label,new,r[4],r[5],r[2],r[3]))
        # Write directly to memory once; avoid duplicate temp files / cached DXF objects.
        out=io.StringIO(); doc.write(out); payload=out.getvalue().encode('utf-8'); out.close()
        name=re.sub(r'(?i)\.dxf$','',uploaded.name)+'_Room_Numbered.dxf'
        st.success(f'{len(changed)} labels changed.')
        st.download_button('DOWNLOAD DXF',payload,name,'application/dxf')
        st.dataframe([{'Function':x[0],'New text':x[1],'Layout':x[2],'Layer':x[3],'X':round(x[4],2),'Y':round(x[5],2)} for x in changed],use_container_width=True)
        del payload; gc.collect()

st.markdown('''### Cloud memory controls
- No `st.cache_data` / `st.cache_resource` is used for uploaded DXF objects.
- Upload is capped in-app at 40 MB; set Streamlit server upload limit to 50 MB.
- The original upload byte buffer is released after parsing.
- Output is created once and held only for the download button.
- No drawing preview/rendering is performed, which avoids large image/geometry arrays.
- For very large/complex CAD drawings, run locally rather than on Community Cloud.
''')
