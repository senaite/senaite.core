Worksheet Print Templates
=========================

All data can be obtained from the dictionary returned by
view.getWorksheet():
```html
<tal:print tal:define="worksheet python:view.getWorksheet()">

    [your code here]

</tal:print>

Example for accessing and displaying data:

<p tal:content="python:worksheet['laboratory']['title']"></p>
or
<p tal:content="worksheet/laboratory/title"></p>
```

Worksheet's dictionary structure example
----------------------------------------

```python
{'analyst': {'email': 'analyst1@example.com',
             'fullname': 'Lab Analyst 1',
             'username': 'analyst1'},
 'createdby': {'email': '',
               'fullname': 'admin',
               'username': 'admin'},
 'date_created': u'2015-01-31 11:09 AM',
 'date_printed': u'2015-01-31 01:58 PM',
 'id': 'WS-002',
 'laboratory': {'accreditation_body': 'SAI',
                'accreditation_logo': '',
                'accredited': True,
                'address': '<div>Number 4, First Street</div><div>Little Town</div><div>Western Province</div><div>7195</div><div>South Africa</div>',
                'confidence': 95,
                'logo': 'http://localhost:8090/Plone/logo_print.jpg',
                'obj': <Laboratory at /Plone/bika_setup/laboratory>,
                'title': 'Bika \xcf\x84est Lab',
                'url': 'http://www.bikalims.org/'},
 'obj': <Worksheet at /Plone/worksheets/WS-002>,
 'portal': {'obj': <PloneSite at /Plone>,
            'url': 'http://localhost:8090/Plone'},
 'printedby': {'email': '',
               'fullname': 'admin',
               'username': 'admin'},
 'remarks': '',
 'template_title': '',
 'url': 'http://localhost:8090/Plone/worksheets/WS-002'}
 'ars': [{'analyses': [{'accredited': False,
                       'capture_date': None,
                       'category': 'Metals',
                       'formatted_result': '',
                       'formatted_specs': '9 - 11',
                       'formatted_uncertainty': '',
                       'formatted_unit': 'mg/l',
                       'id': 'Fe',
                       'keyword': 'Fe',
                       'obj': <Analysis at /Plone/clients/client-1/CN-0003-R01/Fe>,
                       'outofrange': False,
                       'point_of_capture': 'Lab Analyses',
                       'position': 1,
                       'refsample': 'CN-0003',
                       'reftype': None,
                       'remarks': '',
                       'request_id': 'CN-0003-R01',
                       'result': '',
                       'resultdm': '',
                       'retested': False,
                       'scientific_name': False,
                       'specs': {'error': 10,
                                 'hidemax': '',
                                 'hidemin': '',
                                 'max': 11,
                                 'min': 9,
                                 'rangecomment': ''},
                       'title': 'Iron',
                       'tmp_position': 100,
                       'type': 'Analysis',
                       'uncertainty': None,
                       'unit': 'mg/l',
                       'worksheet': None},
                      {'accredited': False,
                       'capture_date': None,
                       'category': 'Metals',
                       'formatted_result': '',
                       'formatted_specs': '9 - 11',
                       'formatted_uncertainty': '',
                       'formatted_unit': 'mg/l',
                       'id': 'Cu',
                       'keyword': 'Cu',
                       'obj': <Analysis at /Plone/clients/client-1/CN-0003-R01/Cu>,
                       'outofrange': False,
                       'point_of_capture': 'Lab Analyses',
                       'position': 1,
                       'refsample': 'CN-0003',
                       'reftype': None,
                       'remarks': '',
                       'request_id': 'CN-0003-R01',
                       'result': '',
                       'resultdm': '',
                       'retested': False,
                       'scientific_name': False,
                       'specs': {'error': 10,
                                 'hidemax': '',
                                 'hidemin': '',
                                 'max': 11,
                                 'min': 9,
                                 'rangecomment': ''},
                       'title': 'Copper',
                       'tmp_position': 103,
                       'type': 'Analysis',
                       'uncertainty': None,
                       'unit': 'mg/l',
                       'worksheet': None},
                      {'accredited': False,
                       'capture_date': None,
                       'category': 'Metals',
                       'formatted_result': '',
                       'formatted_specs': '9 - 11',
                       'formatted_uncertainty': '',
                       'formatted_unit': 'mg/l',
                       'id': 'Ca',
                       'keyword': 'Ca',
                       'obj': <Analysis at /Plone/clients/client-1/CN-0003-R01/Ca>,
                       'outofrange': False,
                       'point_of_capture': 'Lab Analyses',
                       'position': 1,
                       'refsample': 'CN-0003',
                       'reftype': None,
                       'remarks': '',
                       'request_id': 'CN-0003-R01',
                       'result': '',
                       'resultdm': '',
                       'retested': False,
                       'scientific_name': False,
                       'specs': {'error': 10,
                                 'hidemax': '',
                                 'hidemin': '',
                                 'max': 11,
                                 'min': 9,
                                 'rangecomment': ''},
                       'title': 'Calcium',
                       'tmp_position': 107,
                       'type': 'Analysis',
                       'uncertainty': None,
                       'unit': 'mg/l',
                       'worksheet': None}],
         'client': {'id': 'client-1',
                    'name': 'Happy Hills',
                    'obj': <Client at /Plone/clients/client-1>,
                    'url': 'http://localhost:8090/Plone/clients/client-1'},
         'date_received': u'2015-01-31 11:11 AM',
         'date_sampled': None,
         'id': 'CN-0003-R01',
         'obj': <AnalysisRequest at /Plone/clients/client-1/CN-0003-R01>,
         'position': 1,
         'sample': {'adhoc': False,
                    'client_sampleid': '',
                    'composite': False,
                    'date_disposal': None,
                    'date_disposed': None,
                    'date_expired': None,
                    'date_received': DateTime('2015/01/31 11:11:36.601871 GMT+1'),
                    'date_sampled': None,
                    'id': 'CN-0003',
                    'obj': <Sample at /Plone/clients/client-1/CN-0003>,
                    'remarks': '',
                    'sample_point': {},
                    'sample_type': {'id': 'sampletype-4',
                                    'obj': <SampleType at /Plone/bika_setup/bika_sampletypes/sampletype-4>,
                                    'title': 'Canola',
                                    'url': 'http://localhost:8090/Plone/bika_setup/bika_sampletypes/sampletype-4'},
                    'sampler': '',
                    'sampling_date': DateTime('2015/01/21 00:00:00 GMT+1'),
                    'url': 'http://localhost:8090/Plone/clients/client-1/CN-0003'},
         'tmp_position': 100,
         'url': 'http://localhost:8090/Plone/clients/client-1/CN-0003-R01'
        }]
}
```

Note the analyses are grouped by ars, so you need to iterate for each
ar to reach its analyses:

```html
    <!-- Your code here (WS level) -->

    <tal:ars tal:repeat="ar ws/ars">
        <!-- Your code here (AR level) -->

        <tal:ans tal:repeat="an ar/analyses">
            <!-- Your code here (analysis level) -->

        </tal>
    </tal>


```
