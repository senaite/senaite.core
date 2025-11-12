# -*- coding: utf-8 -*-

from bika.lims import api
from bika.lims.utils.analysisrequest import create_partition
from senaite.core import logger
from senaite.core.interfaces import IAfterCreateSampleHook
from senaite.core.registry import get_registry_record
from zope.interface import implementer

# Registry key constants
REGISTRY_KEY_COPY_PARTITIONS = "sample_add_form_copy_partitions"


@implementer(IAfterCreateSampleHook)
class AfterCreateSampleHook(object):
    """Copy sample structure with partitions
    """

    def __init__(self, sample, request):
        self.sample = sample
        self.request = request
        self.sort = 10

    def update(self, sample, source=None):
        """Update handler

        :param sample: The newly created sample
        :param source: The source sample to copy from (optional)
        """
        # Return immediately if we do not have a source sample
        # or the registry settings is set to False
        if not source or not self.get_copy_partitions():
            return

        # Check if the source sample has partitions
        if not self.has_partitions(source):
            return

        # Get the partition config from the source sample
        configs = self.get_partition_configurations(source)

        # Nothing to do if we have no configs
        if not configs:
            return

        # Create the partitions in the target sample
        self.create_partitions_from_config(sample, configs)

    def get_copy_partitions(self):
        """Returns whether to copy the sample structure with partitions

        :return: Boolean indicating if partition copying is enabled
        """
        record = get_registry_record(REGISTRY_KEY_COPY_PARTITIONS)
        return bool(record)

    def has_partitions(self, sample):
        """Check if the sample has partitions

        :param source: The source sample object
        :return: True if valid, False otherwise
        """
        if not sample:
            return False

        partitions = sample.getDescendantsUIDs()

        if not partitions:
            return False

        return True

    def get_partition_configurations(self, source):
        """Extract partition configurations from the source sample

        Returns a list of dictionaries containing partition configuration:
        - analyses: list of analysis objects
        - sample_type: SampleType UID or None
        - container: Container UID or None
        - preservation: Preservation UID or None

        :param source: The source sample object
        :return: List of partition configuration dictionaries
        """
        if not source:
            return []

        # Get all partitions from the source
        partitions = source.getDescendants(all_descendants=False)
        if not partitions:
            return []

        configurations = []
        for partition in partitions:
            # Get analyses that belong to this partition
            analyses = partition.getAnalyses(full_objects=True)

            # Get partition-specific settings
            sample_type = partition.getSampleType()
            container = partition.getContainer()
            preservation = partition.getPreservation()
            internal_use = partition.getInternalUse()

            config = {
                "analyses": analyses,
                "sample_type": sample_type,
                "container": container,
                "preservation": preservation,
                "internal_use": internal_use,
            }
            configurations.append(config)

        return configurations

    def create_partitions_from_config(self, primary_sample, configurations):
        """Create partitions for a sample based on configurations

        :param primary_sample: The primary sample object
        :param configurations: List of partition configuration dicts
        :return: List of created partition objects
        """
        if not configurations:
            return []

        created_partitions = []
        for idx, config in enumerate(configurations):
            analyses = config.get("analyses", [])
            sample_type = config.get("sample_type")
            container = config.get("container")
            preservation = config.get("preservation")
            internal_use = config.get("internal_use")

            logger.debug(
                "Creating partition {} of {} for sample {}".format(
                    idx + 1, len(configurations), api.get_id(primary_sample))
            )

            # Create the partition
            partition = create_partition(
                analysis_request=primary_sample,
                request=self.request,
                analyses=analyses,
                sample_type=sample_type,
                container=container,
                preservation=preservation,
                internal_use=internal_use,
            )
            created_partitions.append(partition)

        return created_partitions
