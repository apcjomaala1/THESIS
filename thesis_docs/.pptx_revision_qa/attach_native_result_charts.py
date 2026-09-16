"""Attach editable OOXML charts with matching embedded Excel data, preserving the source deck."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from io import BytesIO
import json
import hashlib
from lxml import etree as E
from openpyxl import Workbook, load_workbook

ROOT = Path(__file__).resolve().parents[2]
TARGET = ROOT / 'WASD - Thesis 2 - panel revised.pptx'
C = 'http://schemas.openxmlformats.org/drawingml/2006/chart'
A = 'http://schemas.openxmlformats.org/drawingml/2006/main'
P = 'http://schemas.openxmlformats.org/presentationml/2006/main'
R = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
REL = 'http://schemas.openxmlformats.org/package/2006/relationships'
CT = 'http://schemas.openxmlformats.org/package/2006/content-types'
NS = dict(c=C, a=A, p=P, r=R)

def el(parent, tag, text=None, **attrs):
    prefix, name = tag.split(':')
    node = E.SubElement(parent, '{'+NS[prefix]+'}'+name, **{k:str(v) for k,v in attrs.items()})
    if text is not None:
        node.text = str(text)
    return node

def tx(parent, size=1600):
    t=el(parent,'c:txPr');el(t,'a:bodyPr');el(t,'a:lstStyle');p=el(t,'a:p');pr=el(p,'a:pPr');r=el(pr,'a:defRPr',sz=size)
    el(r,'a:latin',typeface='Calibri');el(r,'a:srgbClr',val='191F28') if False else None
    fill=el(r,'a:solidFill');el(fill,'a:srgbClr',val='191F28');el(p,'a:endParaRPr',lang='en-US')

def ref(parent, kind, formula, values, fmt='General'):
    node=el(parent,'c:'+kind+'Ref');el(node,'c:f',formula);cache=el(node,'c:'+kind+'Cache')
    if kind=='num':el(cache,'c:formatCode',fmt)
    el(cache,'c:ptCount',val=len(values))
    for i,v in enumerate(values):el(el(cache,'c:pt',idx=i),'c:v',v)

def color(rgb):
    return f'{rgb & 255:02X}{(rgb>>8)&255:02X}{(rgb>>16)&255:02X}'

def chart_xml(spec):
    root=E.Element('{'+C+'}chartSpace',nsmap={'c':C,'a':A,'r':R});el(root,'c:lang',val='en-US')
    chart=el(root,'c:chart');el(chart,'c:autoTitleDeleted',val=1);plot=el(chart,'c:plotArea');el(plot,'c:layout')
    bar=el(plot,'c:barChart');el(bar,'c:barDir',val='col');el(bar,'c:grouping',val='clustered');el(bar,'c:varyColors',val=0)
    cats=spec['categories'];fmt=spec['number_format'];n=len(cats)
    for i,series in enumerate(spec['series']):
        s=el(bar,'c:ser');el(s,'c:idx',val=i);el(s,'c:order',val=i);col=chr(66+i)
        ref(el(s,'c:tx'),'str',f'Sheet1!${col}$1',[series['name']])
        sp=el(s,'c:spPr');el(el(sp,'a:solidFill'),'a:srgbClr',val=color(series['color']));el(el(sp,'a:ln'),'a:noFill')
        ref(el(s,'c:cat'),'str',f'Sheet1!$A$2:$A${n+1}',cats)
        ref(el(s,'c:val'),'num',f'Sheet1!${col}$2:${col}${n+1}',series['values'],fmt)
    labels=el(bar,'c:dLbls');el(labels,'c:numFmt',formatCode=fmt,sourceLinked=0);tx(labels,1600)
    el(labels,'c:dLblPos',val='outEnd');el(labels,'c:showLegendKey',val=0);el(labels,'c:showVal',val=1)
    el(labels,'c:showCatName',val=0);el(labels,'c:showSerName',val=0);el(labels,'c:showPercent',val=0);el(labels,'c:showBubbleSize',val=0)
    el(bar,'c:gapWidth',val=90);el(bar,'c:overlap',val=0);el(bar,'c:axId',val=10);el(bar,'c:axId',val=20)
    cat=el(plot,'c:catAx');el(cat,'c:axId',val=10);el(el(cat,'c:scaling'),'c:orientation',val='minMax');el(cat,'c:delete',val=0)
    el(cat,'c:axPos',val='b');el(cat,'c:majorTickMark',val='none');el(cat,'c:minorTickMark',val='none');el(cat,'c:tickLblPos',val='nextTo');tx(cat,1600)
    el(cat,'c:crossAx',val=20);el(cat,'c:crosses',val='autoZero');el(cat,'c:auto',val=1);el(cat,'c:lblAlgn',val='ctr');el(cat,'c:lblOffset',val=100)
    axis=el(plot,'c:valAx');el(axis,'c:axId',val=20);scale=el(axis,'c:scaling');el(scale,'c:orientation',val='minMax')
    maximum=1 if spec['maximum']==1.1 else spec['maximum'];el(scale,'c:max',val=maximum);el(scale,'c:min',val=0)
    el(axis,'c:delete',val=0);el(axis,'c:axPos',val='l');grid=el(axis,'c:majorGridlines');el(el(el(grid,'c:spPr'),'a:ln',w=6350),'a:solidFill').append(E.Element('{'+A+'}srgbClr',val='E5E8ED'))
    el(axis,'c:numFmt',formatCode='0%' if '%' in fmt else ('0.0' if maximum==1 else '0'),sourceLinked=0)
    el(axis,'c:majorTickMark',val='none');el(axis,'c:minorTickMark',val='none');el(axis,'c:tickLblPos',val='nextTo');tx(axis,1600)
    el(axis,'c:crossAx',val=10);el(axis,'c:crosses',val='autoZero');el(axis,'c:crossBetween',val='between');el(axis,'c:majorUnit',val=.2 if maximum==1 else (5 if maximum==25 else 10))
    if spec['legend']:
        leg=el(chart,'c:legend');el(leg,'c:legendPos',val='b');el(leg,'c:overlay',val=0);tx(leg,1700)
    el(chart,'c:plotVisOnly',val=1);el(chart,'c:dispBlanksAs',val='gap')
    sp=el(root,'c:spPr');el(el(sp,'a:solidFill'),'a:srgbClr',val='FFFFFF');el(el(sp,'a:ln'),'a:noFill')
    tx(root,1600);ed=el(root,'c:externalData');ed.set('{'+R+'}id','rId1');el(ed,'c:autoUpdate',val=0)
    return E.tostring(root,xml_declaration=True,encoding='UTF-8',standalone=True)

def main():
    with ZipFile(TARGET) as z:files={n:z.read(n) for n in z.namelist()}
    ct=E.fromstring(files['[Content_Types].xml']);report=[];count=0
    for name in sorted(files):
        if not name.startswith('ppt/slides/slide') or not name.endswith('.xml'):continue
        slide=E.fromstring(files[name])
        for shape in list(slide.findall('.//p:sp',NS)):
            nv=shape.find('p:nvSpPr/p:cNvPr',NS)
            if nv is None or nv.get('name')!='Results chart':continue
            spec=json.loads(nv.get('descr'));count+=1
            book=Workbook();ws=book.active;ws.title='Sheet1';ws.append(['Method']+[s['name'] for s in spec['series']])
            for i,category in enumerate(spec['categories']):ws.append([category]+[s['values'][i] for s in spec['series']])
            buf=BytesIO();book.save(buf);data=buf.getvalue();book.close()
            xlsx=f'WASD_results_{count}.xlsx';files['ppt/embeddings/'+xlsx]=data
            chart=f'chartPanel{count}.xml';files['ppt/charts/'+chart]=chart_xml(spec)
            rels=E.Element('{'+REL+'}Relationships',nsmap={None:REL});E.SubElement(rels,'{'+REL+'}Relationship',Id='rId1',Type=R+'/package',Target='../embeddings/'+xlsx)
            files['ppt/charts/_rels/'+chart+'.rels']=E.tostring(rels,xml_declaration=True,encoding='UTF-8')
            slide_rels='ppt/slides/_rels/'+Path(name).name+'.rels';rels=E.fromstring(files[slide_rels]);rid=f'rIdPanelChart{count}'
            E.SubElement(rels,'{'+REL+'}Relationship',Id=rid,Type=R+'/chart',Target='../charts/'+chart)
            files[slide_rels]=E.tostring(rels,xml_declaration=True,encoding='UTF-8')
            frame=E.Element('{'+P+'}graphicFrame');nvframe=el(frame,'p:nvGraphicFramePr')
            el(nvframe,'p:cNvPr',id=nv.get('id'),name='Editable results chart');el(nvframe,'p:cNvGraphicFramePr');el(nvframe,'p:nvPr')
            xf=el(frame,'p:xfrm');original=shape.find('p:spPr/a:xfrm',NS)
            for child in original:xf.append(E.fromstring(E.tostring(child)))
            graphic=el(frame,'a:graphic');gd=el(graphic,'a:graphicData',uri=C);cr=el(gd,'c:chart');cr.set('{'+R+'}id',rid)
            parent=shape.getparent();parent.replace(shape,frame)
            E.SubElement(ct,'{'+CT+'}Override',PartName='/ppt/charts/'+chart,ContentType='application/vnd.openxmlformats-officedocument.drawingml.chart+xml')
            if not any(e.get('Extension')=='xlsx' for e in ct):E.SubElement(ct,'{'+CT+'}Default',Extension='xlsx',ContentType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            check=load_workbook(BytesIO(data),data_only=True);actual=list(check.active.values);assert actual[0][1:]==tuple(s['name'] for s in spec['series'])
            for i,category in enumerate(spec['categories']):assert actual[i+1]==tuple([category]+[s['values'][i] for s in spec['series']])
            check.close();report.append({'slide_part':name,'chart_part':chart,'spec':spec,'workbook_verified':True})
        # Fix the architecture decision box before the one requested visual pass.
        for shape in slide.findall('.//p:sp',NS):
            nv=shape.find('p:nvSpPr/p:cNvPr',NS)
            if nv is not None and nv.get('name')=='Review decision':
                for rpr in shape.findall('.//a:rPr',NS):rpr.set('sz','1800')
        files[name]=E.tostring(slide,xml_declaration=True,encoding='UTF-8',standalone=True)
    assert count==4,f'Expected four charts, got {count}'
    files['[Content_Types].xml']=E.tostring(ct,xml_declaration=True,encoding='UTF-8',standalone=True)
    temp=TARGET.with_suffix('.charts.tmp.pptx')
    with ZipFile(temp,'w',ZIP_DEFLATED) as z:
        for name,data in files.items():z.writestr(name,data)
    temp.replace(TARGET)
    receipt=ROOT/'thesis_docs/.pptx_revision_qa/native_results_charts_receipt.json'
    receipt.write_text(json.dumps({'charts':report,'output_sha256':hashlib.sha256(TARGET.read_bytes()).hexdigest()},indent=2),encoding='utf-8')
    print(f'Attached and verified {count} native charts with embedded workbooks.')

if __name__=='__main__':main()
