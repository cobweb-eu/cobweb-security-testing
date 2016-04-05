import unittest
import pycurl

from StringIO import StringIO

WFS_POST_URL = "https://dyfi.cobwebproject.eu/test/service/wfs"
WFS_URL = "https://dyfi.cobwebproject.eu/test/service/wfs?request=GetFeature&service=WFS&version=1.1.0&"

USER_UUID = "040522c4-e3d6-0ec7-0124-dc64602b9346"
SURVEY_1 = "cobweb:sid-78cd6e23-583a-4ba7-ac52-9c56e492d59c"
SURVEY_2 = "cobweb:sid-f629c133-d4af-45ce-9e8b-97545abd61cc"

GEOSERVER_WFS_URL = "http://localhost:8020/geoserver/cobweb/wfs?"


def get_request(url):
    buf = StringIO()
    c = pycurl.Curl()
    c.setopt(c.URL, url)
    c.setopt(pycurl.SSL_VERIFYPEER, 0)
    c.setopt(pycurl.SSL_VERIFYHOST, 0)
    c.setopt(c.WRITEDATA, buf)
    c.setopt(pycurl.HTTPHEADER, ['uuid: %s'%USER_UUID])
    c.perform()
    c.close()
    return buf.getvalue()


def post_request(payload):
    buf = StringIO()
    c = pycurl.Curl()
    c.setopt(c.URL, WFS_POST_URL)
    c.setopt(c.POSTFIELDS, payload)
    c.setopt(pycurl.SSL_VERIFYPEER, 0)
    c.setopt(pycurl.SSL_VERIFYHOST, 0)
    c.setopt(pycurl.HTTPHEADER, ['Content-type: text/xml', 'uuid: %s'%USER_UUID])
    c.setopt(c.WRITEDATA, buf)
    c.perform()
    c.close()
    return buf.getvalue()


def print_live_or_dev():
    import socket
    address = socket.gethostbyname_ex('dyfi.cobwebproject.eu')
    print(address[2][0])
    if '192.168.10.100' in address[2]:
        print("Testing on DEV!")
    else:
        print("Testing on LIVE!")


class TestSimpleGetFeature(unittest.TestCase):
    def test_single_type_name(self):
        desiredResult = 'request=GetFeature;service=WFS;version=1.1.0;typeName=' \
                        'A;FILTER=(<fes:Filter xmlns:fes="http://www.opengis.net' \
                        '/ogc"><fes:PropertyIsEqualTo><fes:PropertyName>userid</' \
                        'fes:PropertyName><fes:Literal>Joe</fes:Literal></fes:Pro' \
                        'pertyIsEqualTo></fes:Filter>)'
        result = get_request(WFS_URL + "typeName=A")
        self.assertEqual(result, desiredResult)   

    def test_multiple_type_names(self):
        desiredResult = 'request=GetFeature;service=WFS;version=1.1.0;typeName=A,B' \
                        ';FILTER=(<fes:Filter xmlns:fes="http://www.opengis.net/ogc">' \
                        '<fes:PropertyIsEqualTo><fes:PropertyName>userid</fes:Property' \
                        'Name><fes:Literal>Joe</fes:Literal></fes:PropertyIsEqualTo>' \
                        '</fes:Filter>),(<fes:Filter xmlns:fes="http://www.opengis.net' \
                        '/ogc"><fes:PropertyIsEqualTo><fes:PropertyName>userid</fes:' \
                        'PropertyName><fes:Literal>Joe</fes:Literal></fes:PropertyIs' \
                        'EqualTo></fes:Filter>)'
        result = get_request(WFS_URL + "typeName=A,B")
        self.assertEqual(result, desiredResult)
        

class TestFilteredGetFeature(unittest.TestCase):

    def test_single_type_name_filter(self):
        desiredResult = 'request=GetFeature;service=WFS;version=1.1.0;typeName=' \
                        'A;FILTER=(<Filter><And><fes:PropertyIsEqualTo xmlns:fe' \
                        's="http://www.opengis.net/ogc"><fes:PropertyName>useri' \
                        'd</fes:PropertyName><fes:Literal>Joe</fes:Literal></fe' \
                        's:PropertyIsEqualTo><F1/></And></Filter>)'
        result = get_request(WFS_URL + "typeName=A&filter=<Filter><F1/></Filter>")
        self.assertEqual(result, desiredResult)
        
    def test_multiple_name_filter(self):
        desiredResult = 'request=GetFeature;service=WFS;version=1.1.0;typeName=' \
                        'A,B;FILTER=(<Filter><And><fes:PropertyIsEqualTo xmlns:' \
                        'fes="http://www.opengis.net/ogc"><fes:PropertyName>use' \
                        'rid</fes:PropertyName><fes:Literal>Joe</fes:Literal></' \
                        'fes:PropertyIsEqualTo><F1/></And></Filter>),(<Filter><' \
                        'And><fes:PropertyIsEqualTo xmlns:fes="http://www.openg' \
                        'is.net/ogc"><fes:PropertyName>userid</fes:PropertyName' \
                        '><fes:Literal>Joe</fes:Literal></fes:PropertyIsEqualTo' \
                        '><F2/></And></Filter>)'
        result = get_request(WFS_URL + "typeName=A,B&filter=(<Filter><F1/></" \
                                "Filter>),(<Filter><F2/></Filter>)")
        self.assertEqual(result, desiredResult)

        
class TestBoundedGetFeature(unittest.TestCase):
    
    def test_single_type_name(self):
        desiredResult = 'request=GetFeature;service=WFS;version=1.1.0;typeName=' \
                        'A;FILTER=(<fes:Filter xmlns:fes="http://www.opengis.ne' \
                        't/ogc"><fes:And xmlns:fes="http://www.opengis.net/ogc"' \
                        '><fes:BBOX xmlns:fes="http://www.opengis.net/ogc"><gml' \
                        ':Envelope xmlns:gml="http://www.opengis.net/gml" srsNa' \
                        'me="EPSG:4326"><gml:lowerCorner>0 1</gml:lowerCorner><' \
                        'gml:upperCorner>2 3</gml:upperCorner></gml:Envelope></' \
                        'fes:BBOX><fes:PropertyIsEqualTo xmlns:fes="http://www.' \
                        'opengis.net/ogc"><fes:PropertyName>userid</fes:Propert' \
                        'yName><fes:Literal>Joe</fes:Literal></fes:PropertyIsEq' \
                        'ualTo></fes:And></fes:Filter>)'
        result = get_request(WFS_URL + "typeName=A&bbox=0,1,2,3")
        self.assertEqual(result, desiredResult)
        
    def test_multiple_type_name(self):
        desiredResult = 'request=GetFeature;service=WFS;version=1.1.0;typeName=' \
                        'A,B;FILTER=(<fes:Filter xmlns:fes="http://www.opengis.' \
                        'net/ogc"><fes:And xmlns:fes="http://www.opengis.net/og' \
                        'c"><fes:BBOX xmlns:fes="http://www.opengis.net/ogc"><g' \
                        'ml:Envelope xmlns:gml="http://www.opengis.net/gml" srs' \
                        'Name="EPSG:4326"><gml:lowerCorner>0 1</gml:lowerCorner' \
                        '><gml:upperCorner>2 3</gml:upperCorner></gml:Envelope>' \
                        '</fes:BBOX><fes:PropertyIsEqualTo xmlns:fes="http://ww' \
                        'w.opengis.net/ogc"><fes:PropertyName>userid</fes:Prope' \
                        'rtyName><fes:Literal>Joe</fes:Literal></fes:PropertyIs' \
                        'EqualTo></fes:And></fes:Filter>),(<fes:Filter xmlns:fe' \
                        's="http://www.opengis.net/ogc"><fes:And xmlns:fes="htt' \
                        'p://www.opengis.net/ogc"><fes:BBOX xmlns:fes="http://w' \
                        'ww.opengis.net/ogc"><gml:Envelope xmlns:gml="http://www.opengis.net/gml" srsName="EPSG:4326"><gml:lowerCorner>0 1</gml:lowerCorner><gml:upperCorner>2 3</gml:upperCorner></gml:Envelope></fes:BBOX><fes:PropertyIsEqualTo xmlns:fes="http://www.opengis.net/ogc"><fes:PropertyName>userid</fes:PropertyName><fes:Literal>Joe</fes:Literal></fes:PropertyIsEqualTo></fes:And></fes:Filter>)'
        result = get_request(WFS_URL + "typeName=A,B&bbox=0,1,2,3")
        self.assertEqual(result, desiredResult)


class TestFeatureIDGetFeature(unittest.TestCase):
    
    def test_single_feature(self):
        desiredResult = 'request=GetFeature;service=WFS;version=1.1.0;typeName=' \
                        'A;FILTER=(<fes:Filter xmlns:fes="http://www.opengis.ne' \
                        't/ogc"><fes:And xmlns:fes="http://www.opengis.net/ogc"' \
                        '><fes:FeatureId xmlns:fes="http://www.opengis.net/ogc"' \
                        ' fid="id_4711"/><fes:PropertyIsEqualTo xmlns:fes="http' \
                        '://www.opengis.net/ogc"><fes:PropertyName>userid</fes:' \
                        'PropertyName><fes:Literal>Joe</fes:Literal></fes:Prope' \
                        'rtyIsEqualTo></fes:And></fes:Filter>)'
        result = get_request(WFS_URL + "typeName=A&featureid=id_4711")
        self.assertEqual(result, desiredResult)
        
    def test_multiple_features(self):
        desiredResult = 'request=GetFeature;service=WFS;version=1.1.0;typeName=' \
                        'A;FILTER=(<fes:Filter xmlns:fes="http://www.opengis.ne' \
                        't/ogc"><fes:And xmlns:fes="http://www.opengis.net/ogc"' \
                        '><fes:FeatureId xmlns:fes="http://www.opengis.net/ogc"' \
                        ' fid="id_4711"/><fes:FeatureId xmlns:fes="http://www.o' \
                        'pengis.net/ogc" fid="id_4712"/><fes:PropertyIsEqualTo ' \
                        'xmlns:fes="http://www.opengis.net/ogc"><fes:PropertyNa' \
                        'me>userid</fes:PropertyName><fes:Literal>Joe</fes:Lite' \
                        'ral></fes:PropertyIsEqualTo></fes:And></fes:Filter>)'
        result = get_request(WFS_URL + "typeName=A&featureid=id_4711,id_4712")
        self.assertEqual(result, desiredResult)


class TestPostFeature(unittest.TestCase):
    
    def test_single_feature(self):
        desiredResult = '<wfs:GetFeature xmlns:wfs="http://www.opengis.net/wfs" xmlns:ogc="http://www.opengis.net/ogc" xmlns:myns="http://www.example.com/myns" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" service="WFS" version="1.0.0" xsi:schemaLocation="http://www.opengis.net/wfs ../wfs/1.0.0/WFS-basic.xsd">    <wfs:Query typeName="A"><fes:Filter xmlns:fes="http://www.opengis.net/ogc"><fes:PropertyIsEqualTo><fes:PropertyName>userid</fes:PropertyName><fes:Literal>Joe</fes:Literal></fes:PropertyIsEqualTo></fes:Filter></wfs:Query>    <wfs:Query typeName="B">     <ogc:Filter><And><fes:PropertyIsEqualTo xmlns:fes="http://www.opengis.net/ogc"><fes:PropertyName>userid</fes:PropertyName><fes:Literal>Joe</fes:Literal></fes:PropertyIsEqualTo><ogc:F1 xmlns:ogc="http://www.opengis.net/ogc"/></And></ogc:Filter>    </wfs:Query>    <wfs:Query typeName="C">     <ogc:Filter><ogc:And><ogc:F2/><ogc:F3/><fes:PropertyIsEqualTo xmlns:fes="http://www.opengis.net/ogc"><fes:PropertyName>userid</fes:PropertyName><fes:Literal>Joe</fes:Literal></fes:PropertyIsEqualTo></ogc:And></ogc:Filter>    </wfs:Query>    <wfs:Query typeName="D"><fes:Filter xmlns:fes="http://www.opengis.net/ogc"><fes:PropertyIsEqualTo><fes:PropertyName>userid</fes:PropertyName><fes:Literal>Joe</fes:Literal></fes:PropertyIsEqualTo></fes:Filter></wfs:Query> </wfs:GetFeature>'
        requestXml = '<wfs:GetFeature   service="WFS"   version="1.1.0"   xmlns:wfs="http://www.opengis.net/wfs"   xmlns:ogc="http://www.opengis.net/ogc"   xmlns:myns="http://www.example.com/myns"   xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"   xsi:schemaLocation="http://www.opengis.net/wfs ../wfs/1.1.0/WFS-basic.xsd">   <wfs:Query typeName="A"/>   <wfs:Query typeName="B">    <ogc:Filter><ogc:F1/></ogc:Filter>   </wfs:Query>   <wfs:Query typeName="C">    <ogc:Filter><ogc:And><ogc:F2/><ogc:F3/></ogc:And></ogc:Filter>   </wfs:Query>   <wfs:Query typeName="D"/></wfs:GetFeature>'
        result = post_request(requestXml)
        self.assertEqual(result, desiredResult)
        
if __name__ == '__main__':
    print_live_or_dev()
    # TODO: Add tests for AccessDenied requests
    unittest.main()
