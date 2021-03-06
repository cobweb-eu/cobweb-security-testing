import unittest
import pycurl

from StringIO import StringIO
from xml.dom.minidom import parseString

# The following define the base URLs we will use for WFS request
WFS_POST_URL = "https://dyfi.cobwebproject.eu/test/service/wfs"
WFS_URL = "https://dyfi.cobwebproject.eu/test/service/wfs?request=GetFeature&service=WFS&version=1.1.0&"

# The following are the UUID of users and surveys for this test
# Both users should have observations on both surveys
# Each user should only see their own observations (because we 
# do not pass the cookie "surveys" parameter).
USER1 = "UUID"
USER2 = "UUID"
SURVEY1 = "cobweb:sid-UUID"
SURVEY2 = "cobweb:sid-UUID"
FILTER_ATTR = "cobweb:pos_acc"
FILTER_VAL = "-1.0"
BBOX_CONTAINS_OBS = (50,-5,55,0)
BBOX_NO_CONTAIN_OBS = (1, 2, 2, 3)


# The following is a group of convenience functions
# to make request handling simpler

""" Convenience function to perform a GET request constructing a filter and
    returning a parsed dom object
"""
def _performFilterRequestParseResponse(filterAttr, filterVal, surveys, user):
    filterString = _makeEqualFilter(filterAttr, filterVal)
    request = 'typeName=%s&%s'%(','.join(surveys), filterString)
    return _performDOMGetRequest(request, user)

def _performBBoxRequestParseResponse(left, lower, right, upper, surveys, user):
    bboxString = ','.join(str(x) for x in [left, lower, right, upper])
    request = 'typeName=%s&%s'%(','.join(surveys), bboxString)
    return _performDOMGetRequest(request, user)
    
""" Convenience function to perform a GET request and return a DOM
    Parameters are the url to GET and the uuid to use in the header
"""
def _performDOMGetRequest(url, uuid):
    return parseString(_performRequest(''.join(WFS_URL, url), uuid))

""" Convenience function to perform a GET
    WFS request.
"""
def _performRequest(url, uuid):
    buffer = StringIO()
    c = pycurl.Curl()
    c.setopt(c.URL, url)
    c.setopt(pycurl.SSL_VERIFYPEER, 0)
    c.setopt(pycurl.SSL_VERIFYHOST, 0)
    c.setopt(c.WRITEDATA, buffer)
    c.setopt(pycurl.HTTPHEADER, ['uuid: %s'%uuid])
    c.perform()
    c.close()
    return buffer.getvalue()

""" Convenience function to perform a POST
    WFS request.
"""
def _performPostRequest(payload):
    buffer = StringIO()
    c = pycurl.Curl()
    c.setopt(c.URL, WFS_POST_URL)
    c.setopt(c.POSTFIELDS, payload)
    c.setopt(pycurl.SSL_VERIFYPEER, 0)
    c.setopt(pycurl.SSL_VERIFYHOST, 0)
    c.setopt(pycurl.HTTPHEADER, ['Content-type: text/xml', 'uuid: Joe'])
    c.setopt(c.WRITEDATA, buffer)
    c.perform()
    c.close()
    return buffer.getvalue()

""" Convenience function to print which environment is tested on
"""
def _printLiveOrDev():
    import socket
    address = socket.gethostbyname_ex('dyfi.cobwebproject.eu')
    print(address[2][0])
    if '192.168.10.100' in address[2]:
        print("Testing on DEV!")
    else:
        print("Testing on LIVE!")

""" Convenience function to return a list uuids from a
    feature collection, one from each observation
"""
def _getUserIDsFromFeatures(self, wfsFeatureCollectionDom):
        return (x.firstChild.nodeValue for x in
                wfsFeatureCollectionDom.getElementsByTagName('cobweb:userid'))
    
""" Makes a WFS Filter to match a parameter
    with a value
"""
def _makeEqualFilter(param, value):
    return 'Filter=<Filter><PropertyIsEqualTo><PropertyName>\%s</PropertyName> \
            <Literal>%s</Literal></PropertyIsEqualTo></Filter>'%(param, value)


# Now come the main test classes

""" TestSimpleGetFeature tests that simple filterless
    WFS GetFeature requests (HTTP GET) are rewritten correctly
    so that valid requests, once rewritten, produce valid results

    Specifically, we need to test that the UUID from the http header
    is correctly inserted into the WFS filter clause under a variety
    of request conditions. We also check that the filter is applied 
    correctly by WFS so that only the results for the UUID are returned
"""
class TestSimpleGetFeature(unittest.TestCase):
    
    """ Tests a request with a single survey and 
        no further request parameters
    """
    def testSingleTypeName(self):
        # Make a valid request simple request, check filter is applied
        request = "typeName=%s"%SURVEY1
        result = _performDOMGetRequest(request, USER1)
        
        # check that the result contains results for this UUID only
        userIDs = _getUserIDsFromFeatures(result)
        for userID in userIDs:
            self.assertEqual(userID, USER1)

    """ Test that a request for multiple surveys
        is rewritten and actioned correctly
    """
    def testMultipleTypeNames(self):
        # Make a valid request with two surveys
        request = "typeName=%s,%s"%(SURVEY1,SURVEY2)
        result = _performDOMGetRequest(request, USER2)
        
        # Make sure we only see our observations
        userIDs = _getUserIDsFromFeatures(result)
        for userID in userIDs:
            self.assertEqual(userID, USER2)
            
        # Make sure there are observations for both surveys
        self.assertGreater(len(result.getElementsByTagName(SURVEY1)), 0)
        self.assertGreater(len(result.getElementsByTagName(SURVEY2)), 0)
    
        
""" Tests HTTP Get with WFS Filter applied
"""
class TestFilteredGetFeature(unittest.TestCase):

    """ Tests a single survey request, with, sample filter
    
        For this test to pass SURVEY1 should have at least
        one observation for USER1 with FILTER_ATTR set to
        FILTER_VAL. Observations by other users with this
        value set should also exist.
    """
    def test_single_type_name_filter(self):
        result = _performFilterRequestParseResponse(FILTER_ATTR, '1.0',
                                                    [SURVEY1], USER1)  
        # should not contain observation
        self.assertEqual(len(_getUserIDsFromFeatures(result)), 0)
        
        # do the test with correct filter
        result = _performFilterRequestParseResponse(FILTER_ATTR, FILTER_VAL,
                                                    [SURVEY1], USER1)
        # should contain some observations
        userIDs = _getUserIDsFromFeatures(result)
        self.assertGreater(len(userIDs), 0)
        
        # should only be those belonging to USER1
        for uuid in userIDs:
            self.assertEqual(uuid, USER1)
    
        
    def test_multiple_name_filter(self):
        result = _performFilterRequestParseResponse(FILTER_ATTR, '1.0',
                                                    [SURVEY1,SURVEY2], USER1)
        # should not contain observation
        self.assertEqual(len(_getUserIDsFromFeatures(result)), 0)
        
        # do the test with correct filter
        result = _performFilterRequestParseResponse(FILTER_ATTR, FILTER_VAL,
                                                    [SURVEY1,SURVEY2], USER1)
        # should contain some observations
        userIDs = _getUserIDsFromFeatures(result)
        self.assertGreater(len(userIDs), 0)
        
        # should only be those belonging to USER1
        for uuid in userIDs:
            self.assertEqual(uuid, USER1)
         
        # should be across both surveys
        self.assertGreater(len(result.getElementsByTagName(SURVEY1)), 0)
        self.assertGreater(len(result.getElementsByTagName(SURVEY2)), 0)
        

""" Tests the rewriting of WFS requests that use a bounding box parameter
"""
class TestBoundedGetFeature(unittest.TestCase):
    
    """ Tests the rewriting with a bounding box and a single survey
    """
    def test_single_type_name(self):
        u, l, b, r = BBOX_CONTAINS_OBS 
        result = _performBBoxRequestParseResponse(u, l, b, r, [SURVEY1], USER1)
        
        # assert that we have observations returned, only for user1
        userIDs = _getUserIDsFromFeatures(result)
        self.assertGreater(len(userIDs), 0)
        for user in userIDs:
            self.assertEqual(user, USER1)
        
        # request with bbox containing no observations, should contain none
        u, l, b, r = BBOX_NO_CONTAIN_OBS
        result = _performBBoxRequestParseResponse(u, l, b, r, [SURVEY1], USER1)
        self.assertEqual(len(_getUserIDsFromFeatures(result)), 0)
        
    def test_multiple_type_name(self):
        u, l, b, r = BBOX_CONTAINS_OBS
        result = _performBBoxRequestParseResponse(u, l, b, r,
                                                  [SURVEY1,SURVEY2], USER1)
        # should contain at least one observation from each survey, only USER1
        self.assertGreater(len(result.getElementsByTagName(SURVEY1)), 0)
        self.assertGreater(len(result.getElementsByTagName(SURVEY2)), 0)
        for user in _getUserIDsFromFeatures(result):
            self.assertEqual(user, USER1)
        
        # request with bbox containing no observations, should contain none 
        u, l, b, r = BBOX_NO_CONTAIN_OBS
        result = _performBBoxRequestParseResponse(u, l, b, r,
                                                  [SURVEY1,SURVEY2], USER1)
        self.assertEqual(len(_getUserIDsFromFeatures(result)), 0)
        

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
        result = performRequest(WFS_URL + "typeName=A&featureid=id_4711")
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
        result = performRequest(WFS_URL + "typeName=A&featureid=id_4711,id_4712")
        self.assertEqual(result, desiredResult)


class TestPostFeature(unittest.TestCase):
    
    def test_single_feature(self):
        desiredResult = 'POSTDATA=<wfs:GetFeature xmlns:wfs="http://www.opengis' \
                        '.net/wfs" xmlns:ogc="http://www.opengis.net/ogc" xmlns' \
                        ':myns="http://www.example.com/myns" xmlns:xsi="http://' \
                        'www.w3.org/2001/XMLSchema-instance" service="WFS" vers' \
                        'ion="1.1.0" xsi:schemaLocation="http://www.opengis.net' \
                        '/wfs ../wfs/1.1.0/WFS-basic.xsd">   <wfs:Query typeNam' \
                        'e="A"><fes:Filter xmlns:fes="http://www.opengis.net/og' \
                        'c"><fes:PropertyIsEqualTo><fes:PropertyName>userid</fe' \
                        's:PropertyName><fes:Literal>Joe</fes:Literal></fes:Pro' \
                        'pertyIsEqualTo></fes:Filter></wfs:Query>   <wfs:Query ' \
                        'typeName="B">    <ogc:Filter><And><fes:PropertyIsEqual' \
                        'To xmlns:fes="http://www.opengis.net/ogc"><fes:Propert' \
                        'yName>userid</fes:PropertyName><fes:Literal>Joe</fes:L' \ 
                        'iteral></fes:PropertyIsEqualTo><ogc:F1 xmlns:ogc="http' \
                        '://www.opengis.net/ogc"/></And></ogc:Filter>   </wfs:Q' \
                        'uery>   <wfs:Query typeName="C">    <ogc:Filter><ogc:A' \
                        'nd><ogc:F2/><ogc:F3/><fes:PropertyIsEqualTo xmlns:fes=' \
                        '"http://www.opengis.net/ogc"><fes:PropertyName>userid<' \
                        '/fes:PropertyName><fes:Literal>Joe</fes:Literal></fes:' \
                        'PropertyIsEqualTo></ogc:And></ogc:Filter>   </wfs:Quer' \
                        'y>   <wfs:Query typeName="D"><fes:Filter xmlns:fes="ht' \
                        'tp://www.opengis.net/ogc"><fes:PropertyIsEqualTo><fes:' \
                        'PropertyName>userid</fes:PropertyName><fes:Literal>Joe' \
                        '</fes:Literal></fes:PropertyIsEqualTo></fes:Filter></w' \
                        'fs:Query></wfs:GetFeature>'

        requestXml = '<wfs:GetFeature   service="WFS"   version="1.1.0"   xmlns' \
                     ':wfs="http://www.opengis.net/wfs"   xmlns:ogc="http://www' \
                     '.opengis.net/ogc"   xmlns:myns="http://www.example.com/my' \
                     'ns"   xmlns:xsi="http://www.w3.org/2001/XMLSchema-instanc' \
                     'e"   xsi:schemaLocation="http://www.opengis.net/wfs ../wf' \
                     's/1.1.0/WFS-basic.xsd">   <wfs:Query typeName="A"/>   <wf' \
                     's:Query typeName="B">    <ogc:Filter><ogc:F1/></ogc:Filte' \
                     'r>   </wfs:Query>   <wfs:Query typeName="C">    <ogc:Filt' \
                     'er><ogc:And><ogc:F2/><ogc:F3/></ogc:And></ogc:Filter>   <' \
                     '/wfs:Query>   <wfs:Query typeName="D"/></wfs:GetFeature>'

        result = performPostRequest(requestXml)
        self.assertEqual(result, desiredResult)
        
if __name__ == '__main__':
    printLiveOrDev()
    # TODO: Add tests for AccessDenied requests
    unittest.main()
    
