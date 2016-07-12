# calling the classes here we avoid other functions to fail when looking
# for any resource in the 'old' sample.py file
from .ajax import ajaxGetSampleTypeInfo
from .analyses import SampleAnalysesView
from .partitions import SamplePartitionsView
from .edit import SampleEdit
from .partitions import createSamplePartition
from .printform import SamplesPrint
from .view import SampleView
from .view import SamplesView
